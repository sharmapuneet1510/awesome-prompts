---
name: MSSQL Advanced Coding Skill
version: 2.0
description: >
  Reusable skill module for SQL Server T-SQL development. Covers version
  detection, stored procedure templates, NOLOCK explained clearly, query
  optimisation, indexing, security, and mandatory test script generation.
applies_to: [mssql, t-sql, sql-server, azure-sql]
---

# MSSQL Advanced Coding Skill — v2.0

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

```
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

```
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
    IF @CustomerId IS NULL OR @CustomerId <= 0
    BEGIN
        THROW 50001, 'CustomerId must be a positive integer.', 1;
        RETURN;
    END

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
        o.created_at DESC;

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

    IF @Items IS NULL OR @Items = '[]'
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

        -- Insert line items from the JSON array
        INSERT INTO dbo.order_items (order_id, product_id, quantity, unit_price)
        SELECT
            @OrderId,
            JSON_VALUE(item.value, '$.productId'),
            JSON_VALUE(item.value, '$.qty'),
            JSON_VALUE(item.value, '$.price')
        FROM OPENJSON(@Items) AS item;

        -- All done — commit everything
        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        -- Something went wrong — undo everything
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

```sql
-- ═══════════════════════════════════════════════════════════════════════
-- Test Script : dbo.usp_CreateOrder
-- Environment : Development / Test database ONLY
-- Cleanup     : All changes are rolled back at the end — DB is unchanged
-- ═══════════════════════════════════════════════════════════════════════

-- Start a transaction so we can roll back all test data at the end
BEGIN TRANSACTION;

-- ── Setup: insert a test customer ─────────────────────────────────────
INSERT INTO dbo.customers (customer_id, name, email)
VALUES (9901, 'Test Customer', 'test@example.com');

-- ── TEST 1: Happy path — valid order should be created ────────────────
PRINT '=== TEST 1: Valid order creation ===';

DECLARE @OrderId INT;

EXEC dbo.usp_CreateOrder
    @CustomerId = 9901,
    @Items      = '[{"productId":1,"qty":2,"price":9.99},{"productId":2,"qty":1,"price":4.99}]',
    @OrderId    = @OrderId OUTPUT;

-- Verify the order was created
IF EXISTS (SELECT 1 FROM dbo.orders WHERE order_id = @OrderId AND status = 'PENDING')
    PRINT 'PASS ✓ Order created with PENDING status. OrderId: ' + CAST(@OrderId AS VARCHAR)
ELSE
    PRINT 'FAIL ✗ Order was not created or has wrong status';

-- Verify line items were inserted
DECLARE @ItemCount INT;
SELECT @ItemCount = COUNT(*) FROM dbo.order_items WHERE order_id = @OrderId;

IF @ItemCount = 2
    PRINT 'PASS ✓ Both line items were inserted'
ELSE
    PRINT 'FAIL ✗ Expected 2 items, found: ' + CAST(@ItemCount AS VARCHAR);


-- ── TEST 2: Non-existent customer should fail ─────────────────────────
PRINT '=== TEST 2: Non-existent customer ===';

BEGIN TRY
    EXEC dbo.usp_CreateOrder
        @CustomerId = 99999,    -- this customer does not exist
        @Items      = '[{"productId":1,"qty":1,"price":5.00}]',
        @OrderId    = @OrderId OUTPUT;

    PRINT 'FAIL ✗ Should have thrown error 50003 but did not';
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() = 50003
        PRINT 'PASS ✓ Correctly rejected: customer not found'
    ELSE
        PRINT 'FAIL ✗ Wrong error. Expected 50003, got: ' + CAST(ERROR_NUMBER() AS VARCHAR);
END CATCH;


-- ── TEST 3: Empty items array should fail ─────────────────────────────
PRINT '=== TEST 3: Empty items array ===';

BEGIN TRY
    EXEC dbo.usp_CreateOrder
        @CustomerId = 9901,
        @Items      = '[]',     -- empty array
        @OrderId    = @OrderId OUTPUT;

    PRINT 'FAIL ✗ Should have thrown error 50002 but did not';
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() = 50002
        PRINT 'PASS ✓ Correctly rejected: empty items'
    ELSE
        PRINT 'FAIL ✗ Wrong error. Expected 50002, got: ' + CAST(ERROR_NUMBER() AS VARCHAR);
END CATCH;


-- ── TEST 4: Invalid customer ID should fail ───────────────────────────
PRINT '=== TEST 4: Invalid customer ID (zero) ===';

BEGIN TRY
    EXEC dbo.usp_CreateOrder
        @CustomerId = 0,        -- must be positive
        @Items      = '[{"productId":1,"qty":1,"price":5.00}]',
        @OrderId    = @OrderId OUTPUT;

    PRINT 'FAIL ✗ Should have thrown error 50001 but did not';
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() = 50001
        PRINT 'PASS ✓ Correctly rejected: invalid customer ID'
    ELSE
        PRINT 'FAIL ✗ Wrong error. Expected 50001, got: ' + CAST(ERROR_NUMBER() AS VARCHAR);
END CATCH;


-- ── Cleanup: roll back ALL test data ──────────────────────────────────
ROLLBACK TRANSACTION;
PRINT '=== All test data rolled back. Database is unchanged. ===';
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
