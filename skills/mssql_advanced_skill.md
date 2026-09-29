---
name: MSSQL Advanced Coding Skill
version: 2.2
description: >
  Reusable skill module for SQL Server T-SQL development. Covers version
  detection, stored procedure templates, NOLOCK explained clearly, query
  optimisation, indexing, security, and mandatory test script generation.
  The transactional procedure and its test script were run on SQL Server 2022.
applies_to: [mssql, t-sql, sql-server, azure-sql]
tags: [mssql, t-sql, stored-procedures, isolation, dynamic-sql, indexing, testing]
---

# MSSQL Advanced Coding Skill — v2.2

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | Writing or reviewing T-SQL: procedures, indexes, dynamic SQL on SQL Server / Azure SQL |
| **Skip when** | Portable schema design — `database_skill`. Diagnosing a slow or blocked server — `mssql_dba_skill` |
| **Inputs** | SQL Server version (§1 — detect first), schema, workload |
| **Produces** | Procedures, indexes, test scripts |
| **Steps** | 1. Detect version → 2. Write set-based queries → 3. Procedures with `NOCOUNT` + `XACT_ABORT` + `TRY/CATCH` → 4. Index from the plan → 5. Generate the test script |
| **Done when** | §8 rules hold; a test script accompanies every procedure |
| **Senior defaults** | `SET XACT_ABORT ON` in every transactional procedure · `THROW`, never `RAISERROR`, in new code · dynamic SQL only via `sp_executesql` with parameters · set-based over cursors · `NOLOCK` only with the dirty-read trade-off written down · explicit column lists and schema prefixes |
| **Load on demand** | §1 version · §2 NOLOCK · §3 procedures · §4 indexing · §5 dynamic SQL · §6 query standards · §7 test template |
| **Run report** | `html_report_skill` — adds: Procedures + test scripts |
| **Pairs with** | `database_skill`, `mssql_dba_skill` |

---

## 1. Version Detection First

Before writing any SQL, check what is installed:

```sql
-- Run this and share the output
SELECT @@VERSION;
SELECT SERVERPROPERTY('ProductVersion') AS [Version],
       SERVERPROPERTY('Edition')        AS [Edition];
```

| Version | Key Features Available |
|---------|----------------------|
| SQL Server 2016 | JSON support, `STRING_SPLIT`, temporal tables |
| SQL Server 2017 | `STRING_AGG`, Graph tables, cross-platform (Linux) |
| SQL Server 2019 | `APPROX_COUNT_DISTINCT`, Accelerated Database Recovery (ADR), UTF-8 support |
| SQL Server 2022 | `IS [NOT] DISTINCT FROM`, ledger tables, improved JSON, Azure Synapse Link |
| SQL Server 2025 | Native `json` and `vector` types, `VECTOR_DISTANCE`; `REGEXP_LIKE` and the other regex functions need compatibility level 170 (verified on 17.0 RTM-CU9) |
| Azure SQL | Always latest — auto-patched, serverless option, hyperscale |

---

## 2. NOLOCK — Explained Simply

This is one of the most misunderstood hints in T-SQL. Understand it before using it.

### What NOLOCK Does

```sql
-- NOLOCK = READ UNCOMMITTED isolation level
-- Translation: "Read data even if another transaction is actively changing it."
--
-- SQL Server normal behaviour (READ COMMITTED):
--   Reader waits for Writer to finish and commit. Safe, but can block.
--
-- NOLOCK behaviour:
--   Reader does NOT wait. Reads the data as it is right now —
--   even if the writing transaction hasn't committed yet
--   (or might roll back).

-- Example of the risk — a dirty read:
-- Transaction A: starts updating order #99 (balance was £500, now writing £200)
-- Transaction B (with NOLOCK): reads order #99 and sees £200
-- Transaction A: gets an error, rolls back — balance goes back to £500
-- Transaction B now has a "fact" (£200) that was never true. It never committed.
```

### Decision Guide — NOLOCK or Not?

```sql
Is this query used for financial calculations, balances, or totals?
  YES → ❌ Never use NOLOCK. Use RCSI instead.

Is this query used for order status that drives a business decision?
  YES → ❌ Never use NOLOCK. Use RCSI instead.

Is this a dashboard or report where approximate counts are acceptable?
  MAYBE → ✅ NOLOCK is acceptable. Document the trade-off.

Is this a development/debug query to inspect data quickly?
  YES → ✅ NOLOCK is fine. Don't commit this to production code.
```

### The Better Alternative: RCSI

```sql
-- Instead of sprinkling NOLOCK everywhere, enable RCSI at the database level.
-- RCSI gives you non-blocking reads WITHOUT the dirty-read risk of NOLOCK.
-- It does this using row versioning — readers see a consistent snapshot.

-- Check if RCSI is already enabled:
SELECT
    name,
    is_read_committed_snapshot_on   AS [RCSI Enabled?]
FROM sys.databases
WHERE name = DB_NAME();

-- Enable RCSI (do this during a low-traffic window):
ALTER DATABASE YourDatabase
SET READ_COMMITTED_SNAPSHOT ON
WITH ROLLBACK IMMEDIATE;

-- After this, READ COMMITTED queries will automatically use snapshots.
-- You do NOT need to add NOLOCK hints anywhere.
```

### Isolation Level Summary

```sql
READ UNCOMMITTED (= NOLOCK)
  Dirty reads: YES  |  Blocks writers: NO   |  Risk: HIGH
  → Only for non-critical dashboards or dev queries

READ COMMITTED (SQL Server default)
  Dirty reads: NO   |  Blocks writers: YES  |  Risk: MEDIUM
  → Default. Can cause blocking under heavy concurrent load.

READ COMMITTED SNAPSHOT (RCSI)  ← RECOMMENDED FOR OLTP
  Dirty reads: NO   |  Blocks writers: NO   |  Risk: LOW
  → Best of both worlds. Enable at DB level, not per-query.

SNAPSHOT ISOLATION
  Dirty reads: NO   |  Non-repeatable: NO   |  Phantoms: NO
  → For long-running reports that need a consistent point-in-time view.

SERIALIZABLE
  Dirty reads: NO   |  All anomalies: NO    |  Blocks heavily
  → Only for financial reconciliation or critical single-row operations.
```

---

## 3. Stored Procedure Standards

Every stored procedure must follow this template. No exceptions.

### Read-Only Procedure

```sql
-- ═══════════════════════════════════════════════════════════════════════
-- Procedure : dbo.usp_GetOrdersByCustomer
-- Purpose   : Returns all orders for a customer, optionally filtered by status.
-- Author    : [Name]
-- Created   : [Date]
--
-- Parameters:
--   @CustomerId   INT          Required. The customer to query.
--   @StatusFilter VARCHAR(20)  Optional. Filter by status. NULL = all statuses.
--
-- Returns   : OrderId, Status, TotalAmount, CreatedAt — ordered by newest first.
--
-- Index     : Requires IX_Orders_CustomerId on dbo.orders(customer_id)
-- Called by : OrderService.getOrdersByCustomer() in the application layer
-- ═══════════════════════════════════════════════════════════════════════
CREATE OR ALTER PROCEDURE dbo.usp_GetOrdersByCustomer
    @CustomerId   INT,
    @StatusFilter VARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;   -- Suppresses "N rows affected" — improves performance

    -- Validate input. Never trust the caller.
    -- THROW ends the procedure; no RETURN needed after it.
    IF @CustomerId IS NULL OR @CustomerId <= 0
        THROW 50001, 'CustomerId must be a positive integer.', 1;

    -- Main query. Explicit columns, schema-qualified table name.
    SELECT
        o.order_id        AS OrderId,
        o.status          AS Status,
        o.total_amount    AS TotalAmount,
        o.created_at      AS CreatedAt
    FROM
        dbo.orders AS o
    WHERE
        o.customer_id = @CustomerId
        -- The @StatusFilter IS NULL check means: if no filter is provided,
        -- return all orders regardless of status
        AND (@StatusFilter IS NULL OR o.status = @StatusFilter)
    ORDER BY
        o.created_at DESC
    -- Optional-filter ("catch-all") queries get one cached plan for whichever
    -- parameters compiled first. RECOMPILE builds a plan per call, which is right
    -- when the call rate is modest; for hot paths, split into two queries instead.
    OPTION (RECOMPILE);

END;
```

### Transactional Procedure (Write Operations)

```sql
-- ═══════════════════════════════════════════════════════════════════════
-- Procedure : dbo.usp_CreateOrder
-- Purpose   : Creates a new order and its line items in a single transaction.
--             Either everything is saved, or nothing is (atomic).
-- Author    : [Name]
-- Created   : [Date]
--
-- Parameters:
--   @CustomerId  INT              Required.
--   @Items       NVARCHAR(MAX)    Required. JSON array of { productId, qty, price }.
--   @OrderId     INT OUTPUT       The generated order ID.
-- ═══════════════════════════════════════════════════════════════════════
CREATE OR ALTER PROCEDURE dbo.usp_CreateOrder
    @CustomerId  INT,
    @Items       NVARCHAR(MAX),  -- Pass items as JSON: '[{"productId":1,"qty":2,"price":9.99}]'
    @OrderId     INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    -- XACT_ABORT ON means: if ANY statement fails, the transaction is
    -- automatically rolled back. No need to check @@ERROR manually.
    SET XACT_ABORT ON;

    -- ── Validate inputs ───────────────────────────────────────────────
    IF @CustomerId IS NULL OR @CustomerId <= 0
        THROW 50001, 'CustomerId is required and must be positive.', 1;

    IF @Items IS NULL OR ISJSON(@Items) = 0 OR NOT EXISTS (SELECT 1 FROM OPENJSON(@Items))
        THROW 50002, 'Order must contain at least one item.', 1;

    -- Check the customer exists before creating the order
    IF NOT EXISTS (SELECT 1 FROM dbo.customers WHERE customer_id = @CustomerId)
        THROW 50003, 'Customer not found.', 1;

    -- ── Begin the atomic transaction ──────────────────────────────────
    BEGIN TRANSACTION;

    BEGIN TRY

        -- Insert the order header
        INSERT INTO dbo.orders (customer_id, status, created_at)
        VALUES (@CustomerId, 'PENDING', SYSUTCDATETIME());

        -- Capture the generated order ID
        SET @OrderId = SCOPE_IDENTITY();

        -- Insert line items. OPENJSON ... WITH gives typed columns;
        -- JSON_VALUE would return nvarchar and convert implicitly.
        INSERT INTO dbo.order_items (order_id, product_id, quantity, unit_price)
        SELECT @OrderId, item.productId, item.qty, item.price
        FROM OPENJSON(@Items)
             WITH (productId INT            '$.productId',
                   qty       INT            '$.qty',
                   price     DECIMAL(12, 2) '$.price') AS item;

        -- All done — commit everything
        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        -- Something went wrong — undo everything.
        -- Note: this rolls back the CALLER's transaction too, if there is one.
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        -- Re-raise the original error to the caller
        THROW;
    END CATCH;

END;
```

---

## 4. Indexing Guide

When to add an index and how to document it:

```sql
-- WHEN TO ADD AN INDEX:
--   1. A column appears in a WHERE clause on a large table
--   2. A column is used in a JOIN condition
--   3. A query shows a "Table Scan" or "Index Scan" in the execution plan
--   4. sys.dm_db_missing_index_details recommends it

-- HOW TO WRITE AN INDEX (always include a comment block):

-- ─────────────────────────────────────────────────────────────────────
-- Index   : IX_Orders_CustomerId_Status
-- Table   : dbo.orders
-- Purpose : Supports the query: WHERE customer_id = ? AND status = ?
--           Used by: usp_GetOrdersByCustomer
--
-- Key columns    : customer_id, status  (used in WHERE)
-- Include columns: total_amount, created_at  (returned by the query — avoids key lookup)
-- Filter         : Only active orders — reduces index size
-- ─────────────────────────────────────────────────────────────────────
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_Status
ON dbo.orders (customer_id, status)
INCLUDE (total_amount, created_at)
WHERE status IN ('PENDING', 'CONFIRMED', 'PROCESSING');

-- FIND MISSING INDEXES (run after testing your query with the execution plan):
SELECT
    mid.statement                                           AS table_name,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns,
    migs.avg_total_user_cost * migs.avg_user_impact / 100  AS estimated_benefit
FROM sys.dm_db_missing_index_group_stats AS migs
JOIN sys.dm_db_missing_index_groups      AS mig ON migs.group_handle = mig.index_group_handle
JOIN sys.dm_db_missing_index_details     AS mid ON mig.index_handle  = mid.index_handle
ORDER BY estimated_benefit DESC;
```

---

## 5. Safe Dynamic SQL

```sql
-- ❌ DANGEROUS — never do this. User input goes directly into SQL code.
DECLARE @sql NVARCHAR(500) = 'SELECT * FROM dbo.orders WHERE status = ''' + @Status + '''';
EXEC (@sql);

-- ✅ SAFE — always use sp_executesql with parameters.
--    The value is treated as data, not as SQL code.
--    SQL injection is impossible this way.
DECLARE @sql      NVARCHAR(500);
DECLARE @paramDef NVARCHAR(200);

SET @sql      = N'SELECT order_id, status, total_amount
                  FROM dbo.orders
                  WHERE status = @StatusParam
                    AND customer_id = @CustomerIdParam';

SET @paramDef = N'@StatusParam VARCHAR(20), @CustomerIdParam INT';

EXEC sp_executesql
    @sql,
    @paramDef,
    @StatusParam     = @Status,       -- bound as a parameter, not code
    @CustomerIdParam = @CustomerId;
```

---

## 6. Query Writing Standards

```sql
-- Always:
--   ✅ Use explicit column lists — never SELECT *
--   ✅ Schema-qualify all table names — dbo.orders, not just orders
--   ✅ Use table aliases consistently
--   ✅ Use CTEs (WITH clauses) instead of nested subqueries
--   ✅ Add a comment explaining complex logic

-- Example — CTE for readability:
WITH recent_orders AS (
    -- Get the most recent order for each customer
    SELECT
        o.customer_id,
        o.order_id,
        o.total_amount,
        -- ROW_NUMBER gives each order a rank within its customer group
        -- ordered by newest first
        ROW_NUMBER() OVER (
            PARTITION BY o.customer_id
            ORDER BY o.created_at DESC
        ) AS order_rank
    FROM dbo.orders AS o
    WHERE o.status = 'DELIVERED'
)
SELECT
    r.customer_id,
    r.order_id,
    r.total_amount
FROM recent_orders AS r
WHERE r.order_rank = 1;  -- Only keep the most recent per customer
```

---

## 7. Test Script Template

Every stored procedure must have a test script generated alongside it.

**Do not wrap the tests in one outer transaction.** A procedure with
`XACT_ABORT ON` and `ROLLBACK` in its `CATCH` rolls back the *caller's*
transaction too. Verified on SQL Server 2022: with the tests inside
`BEGIN TRANSACTION … ROLLBACK`, a failure inside the procedure's own
transaction left `@@TRANCOUNT = 0` and deleted the test's setup rows, and the
error-path tests left the outer transaction uncommittable (`Msg 3998` at the
end of the batch). Use reserved test keys and delete them in a teardown, as
below — all five tests pass and the script can be re-run. For a larger suite,
use tSQLt.

```sql
-- ═══════════════════════════════════════════════════════════════════════
-- Test Script : dbo.usp_CreateOrder
-- Environment : Development / Test database ONLY
-- Isolation   : No outer transaction. The procedure uses XACT_ABORT and rolls
--               back on error, which would also roll back (or doom) a transaction
--               wrapped around these tests. Test rows use reserved keys (99xx) and
--               the teardown at the end deletes them.
-- ═══════════════════════════════════════════════════════════════════════
SET NOCOUNT ON;
DECLARE @OrderId INT, @Count INT;

-- ── Setup: a test customer with a reserved key ─────────────────────────
DELETE oi FROM dbo.order_items AS oi JOIN dbo.orders AS o ON o.order_id = oi.order_id WHERE o.customer_id = 9901;
DELETE FROM dbo.orders    WHERE customer_id = 9901;
DELETE FROM dbo.customers WHERE customer_id = 9901;
INSERT INTO dbo.customers (customer_id, name, email) VALUES (9901, 'Test Customer', 'test@example.com');

-- ── TEST 1: Happy path — valid order should be created ────────────────
PRINT '=== TEST 1: Valid order creation ===';
EXEC dbo.usp_CreateOrder
    @CustomerId = 9901,
    @Items      = '[{"productId":1,"qty":2,"price":9.99},{"productId":2,"qty":1,"price":4.99}]',
    @OrderId    = @OrderId OUTPUT;

SELECT @Count = COUNT(*) FROM dbo.order_items WHERE order_id = @OrderId;
IF EXISTS (SELECT 1 FROM dbo.orders WHERE order_id = @OrderId AND status = 'PENDING') AND @Count = 2
    PRINT 'PASS ✓ Order created with PENDING status and 2 line items'
ELSE
    PRINT 'FAIL ✗ Order missing, wrong status, or item count ' + CAST(@Count AS VARCHAR(10));

-- ── TEST 2: Non-existent customer should fail ─────────────────────────
PRINT '=== TEST 2: Non-existent customer ===';
BEGIN TRY
    EXEC dbo.usp_CreateOrder @CustomerId = 99999, @Items = '[{"productId":1,"qty":1,"price":5.00}]', @OrderId = @OrderId OUTPUT;
    PRINT 'FAIL ✗ Should have thrown error 50003 but did not';
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() = 50003 PRINT 'PASS ✓ Correctly rejected: customer not found'
    ELSE PRINT 'FAIL ✗ Expected 50003, got: ' + CAST(ERROR_NUMBER() AS VARCHAR(10));
END CATCH;

-- ── TEST 3: Empty items array should fail ─────────────────────────────
PRINT '=== TEST 3: Empty items array ===';
BEGIN TRY
    EXEC dbo.usp_CreateOrder @CustomerId = 9901, @Items = '[]', @OrderId = @OrderId OUTPUT;
    PRINT 'FAIL ✗ Should have thrown error 50002 but did not';
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() = 50002 PRINT 'PASS ✓ Correctly rejected: empty items'
    ELSE PRINT 'FAIL ✗ Expected 50002, got: ' + CAST(ERROR_NUMBER() AS VARCHAR(10));
END CATCH;

-- ── TEST 4: Invalid customer ID should fail ───────────────────────────
PRINT '=== TEST 4: Invalid customer ID (zero) ===';
BEGIN TRY
    EXEC dbo.usp_CreateOrder @CustomerId = 0, @Items = '[{"productId":1,"qty":1,"price":5.00}]', @OrderId = @OrderId OUTPUT;
    PRINT 'FAIL ✗ Should have thrown error 50001 but did not';
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() = 50001 PRINT 'PASS ✓ Correctly rejected: invalid customer ID'
    ELSE PRINT 'FAIL ✗ Expected 50001, got: ' + CAST(ERROR_NUMBER() AS VARCHAR(10));
END CATCH;

-- ── TEST 5: Failure mid-transaction leaves nothing behind (atomicity) ──
PRINT '=== TEST 5: Unknown product rolls back the order header ===';
DECLARE @OrdersBefore INT = (SELECT COUNT(*) FROM dbo.orders WHERE customer_id = 9901);
BEGIN TRY
    EXEC dbo.usp_CreateOrder @CustomerId = 9901, @Items = '[{"productId":999,"qty":1,"price":5.00}]', @OrderId = @OrderId OUTPUT;
    PRINT 'FAIL ✗ Should have thrown a foreign key error (547) but did not';
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() = 547
       AND @@TRANCOUNT = 0
       AND (SELECT COUNT(*) FROM dbo.orders WHERE customer_id = 9901) = @OrdersBefore
        PRINT 'PASS ✓ FK error raised; no orphan order header; no open transaction'
    ELSE
        PRINT 'FAIL ✗ Error ' + CAST(ERROR_NUMBER() AS VARCHAR(10)) + ', @@TRANCOUNT ' + CAST(@@TRANCOUNT AS VARCHAR(10));
END CATCH;

-- ── Teardown: delete everything the tests created ─────────────────────
DELETE oi FROM dbo.order_items AS oi JOIN dbo.orders AS o ON o.order_id = oi.order_id WHERE o.customer_id = 9901;
DELETE FROM dbo.orders    WHERE customer_id = 9901;
DELETE FROM dbo.customers WHERE customer_id = 9901;
PRINT '=== Test rows deleted. ===';
```

---

## 8. Code Quality Rules (Quick Reference)

| Rule | Detail |
|------|--------|
| `SELECT *` | Never — always list columns explicitly |
| Schema prefix | Always — `dbo.table_name`, not bare `table_name` |
| Procedures | Always `SET NOCOUNT ON` + `SET XACT_ABORT ON` |
| Error handling | All transactional code needs `TRY/CATCH` + `THROW` |
| Dynamic SQL | Only via `sp_executesql` — never string concatenation |
| Cursors | Last resort — replace with set-based operations |
| NOLOCK | Always document WHY it was used — explain the trade-off |
| Test scripts | Always generated alongside procedures — never skipped |
| DDL changes | Always confirm with user before generating `DROP`/`TRUNCATE` |
