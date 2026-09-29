---
name: database
description: Designing tables, indexes, or migrations for PostgreSQL, MySQL, or SQL Server — `architect:schema`
---

# Database Schema Generation Skill — v1.2

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | Designing tables, indexes, or migrations for PostgreSQL, MySQL, or SQL Server — `architect:schema` |
| **Skip when** | T-SQL procedure standards — `mssql_advanced_skill`. Tuning a live SQL Server — `mssql_dba_skill` |
| **Inputs** | Entities, relationships, access patterns, target RDBMS, the project's migration tool (`docs/project-setup/libraries.md`) |
| **Produces** | Versioned migration files in the tool's format, constraints, indexes, `SCHEMA.md` |
| **Steps** | 1. Model entities to 3NF → 2. Keys and constraints → 3. Index from the queries, not the columns → 4. One versioned migration per change; expand → migrate → contract for breaking ones → 5. Validate against §6 |
| **Done when** | §6 checklist passes; migrations apply to an empty database and to a copy of production; every FK indexed |
| **Senior defaults** | Index the actual WHERE + ORDER BY, with covering `INCLUDE` where reads dominate · a UNIQUE constraint already is an index — never add a second one · migrations forward-only in prod, expand → migrate → contract for breaking changes · `NOT NULL` + defaults set explicitly · `timestamptz` / `datetime2` in UTC · `ON DELETE RESTRICT` unless cascading is the business rule · denormalise only with a measured reason and an ADR |
| **Load on demand** | §2 input · §3 output · §4 process · §5 example · §6 checklist · §9 performance · §11 patterns · §12 platform notes |
| **Run report** | `html_report_skill` — adds: Schema diff · Migration files applied |
| **Pairs with** | `mssql_advanced_skill`, `adr_skill` (Database type), `project_setup_skill` (chooses the migration tool) |

---

## 1. Purpose

This skill enables database architects and backend developers to:
- Write versioned, reviewable migrations in the project's migration tool
- Create normalized, performant schemas with proper constraints
- Define indexes and partitioning strategies
- Change a live schema without downtime (expand → migrate → contract)
- Validate schemas against best practices

The skill covers three RDBMS platforms: PostgreSQL, MySQL, and SQL Server.

---

## 2. Input

The skill receives:

1. **Entity Definitions** — entities with fields, types, constraints
   ```yaml
   entities:
     - name: users
       fields:
         - name: id
           type: uuid
           primary_key: true
         - name: email
           type: varchar(255)
           unique: true
           nullable: false
         - name: created_at
           type: timestamptz
           default: now()
   ```

2. **Relationship Definitions** — foreign keys and cardinality
   ```yaml
   relationships:
     - from: orders
       to: users
       cardinality: many-to-one
       on_delete: restrict
   ```

3. **Access Patterns** — the queries the schema must serve; indexes come from these
   ```yaml
   queries:
     - name: a user's orders, newest first
       where: [user_id]
       order_by: [created_at DESC]
       returns: [status, total_amount]
   ```

4. **Platform Selection** — target RDBMS (PostgreSQL, MySQL, SQL Server)

5. **Migration Tool** — from `docs/project-setup/libraries.md` (`project_setup_skill`). Java: Flyway or Liquibase. Python: Alembic. If none is chosen, choose one first — hand-run SQL scripts are not a migration strategy.

---

## 3. Output

1. **Migration files, in the tool's format** — one change per file, never edited after they have run anywhere shared
   - Flyway: `src/main/resources/db/migration/V3__orders_add_currency.sql`
   - Liquibase: a changeset with `id` and `author` in the changelog
   - Alembic: `alembic/versions/<rev>_orders_add_currency.py` with `upgrade()` and `downgrade()`

2. **Schema Documentation** — `SCHEMA.md`
   - Table descriptions and business meaning of each column
   - Relationship diagram
   - Which query each index serves

3. **Validation Report** — the §6 checklist, with results

**Idempotency comes from the tool, not from `IF NOT EXISTS`.** Flyway and
Alembic record every applied migration in a history table and run each one
exactly once. `IF NOT EXISTS` in a versioned migration hides drift: the
migration "succeeds" against a table that has a different shape.

**Rollback is a new forward migration.** In production you do not run
"down" scripts — a dropped column's data is gone. Alembic's `downgrade()` is
for development databases. The safe path for a breaking change is §4 step 4.

---

## 4. Process

### Step 1: Model
- Entities to 3NF; every table has a primary key
- Natural uniqueness (email, order number) as `UNIQUE` constraints
- Enumerations as `CHECK` constraints or a lookup table with a foreign key

### Step 2: Keys and Constraints
- `NOT NULL` on every column that is not optional in the business
- Explicit, named constraints (`uq_users_email`, `fk_orders_users`) — names appear in errors and in later migrations
- `ON DELETE RESTRICT` (SQL Server: the default `NO ACTION`) unless deleting the parent must delete the children as a business rule. Cascading deletes from `users` into `orders` erase financial history
- Times in UTC: `timestamptz` (PostgreSQL), `timestamp(6)` (MySQL, stored as UTC), `datetime2` (SQL Server)

### Step 3: Indexes — from the queries
- Every foreign key column is the leading column of some index (joins, and `RESTRICT` checks on parent delete)
- One composite index per important query: equality columns first, then the range or sort column, then `INCLUDE` for returned columns
- Do not index what a `PRIMARY KEY` or `UNIQUE` constraint already indexes

### Step 4: Migrations
- One logical change per file. MySQL commits each DDL statement implicitly, so a half-failed multi-statement file there is half-applied
- **Breaking changes in three releases — expand → migrate → contract:**
  1. **Expand** — add the new column or table, nullable; old code keeps working
  2. **Migrate** — deploy code that writes both shapes; backfill existing rows
  3. **Contract** — once nothing reads or writes the old shape, add `NOT NULL`, drop the old column
- Large backfills in batches (e.g. 5,000 rows per transaction), not one `UPDATE` holding locks on the whole table

### Step 5: Validate and Report
- Apply all migrations to an empty database in CI (Testcontainers, not an in-memory substitute)
- Apply the new migration to a restored copy of production data before release — constraints that pass on empty tables fail on real rows
- Run the §6 checklist

---

## 5. Code Example: Users and Orders

The same schema on each platform. Each file was applied to an empty database,
then checked: duplicate email rejected, deleting a user with orders rejected,
`updated_at` advanced on update, no duplicate indexes.

### PostgreSQL

```sql
-- V1__create_users_orders.sql  (Flyway runs this once, inside one transaction)
CREATE TABLE users (
    id          uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
    email       varchar(255) NOT NULL,
    username    varchar(100) NOT NULL,
    is_active   boolean      NOT NULL DEFAULT true,
    created_at  timestamptz  NOT NULL DEFAULT now(),
    updated_at  timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT uq_users_email    UNIQUE (email),      -- the constraint creates the index
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT ck_users_email    CHECK (email LIKE '%_@_%')  -- sanity only; real validation lives in the app
);

CREATE TABLE orders (
    id            uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid          NOT NULL,
    order_number  varchar(50)   NOT NULL,
    total_amount  numeric(12,2) NOT NULL,
    status        varchar(20)   NOT NULL DEFAULT 'pending',
    created_at    timestamptz   NOT NULL DEFAULT now(),
    updated_at    timestamptz   NOT NULL DEFAULT now(),
    CONSTRAINT fk_orders_users       FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT uq_orders_order_number UNIQUE (order_number),
    CONSTRAINT ck_orders_total       CHECK (total_amount > 0),
    CONSTRAINT ck_orders_status      CHECK (status IN ('pending', 'processing', 'completed', 'cancelled'))
);

-- FK column indexed, in the shape the main query reads it: "a user's orders, newest first"
CREATE INDEX ix_orders_user_created ON orders (user_id, created_at DESC) INCLUDE (status, total_amount);

-- updated_at is maintained by the database, not by every caller remembering to
CREATE FUNCTION set_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END $$;

CREATE TRIGGER trg_users_updated_at  BEFORE UPDATE ON users  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

Verified: the indexes on the two tables are exactly `users_pkey`,
`uq_users_email`, `uq_users_username`, `orders_pkey`,
`uq_orders_order_number`, `ix_orders_user_created` — no duplicates.

**Expand → migrate → contract** — adding a required `currency` column:

```sql
-- V2__orders_add_currency_expand.sql — EXPAND: nullable column; old code keeps working
ALTER TABLE orders ADD COLUMN currency char(3);

-- V3__orders_backfill_currency.sql — MIGRATE: after the new code writes currency on every insert
UPDATE orders SET currency = 'GBP' WHERE currency IS NULL;

-- V4__orders_currency_not_null.sql — CONTRACT: next release, once no writer leaves it NULL
ALTER TABLE orders ALTER COLUMN currency SET DEFAULT 'GBP';
ALTER TABLE orders ALTER COLUMN currency SET NOT NULL;
```

### MySQL

```sql
-- V1__create_users_orders.sql — MySQL 8.0.16+ (CHECK enforced), InnoDB
-- DDL commits implicitly in MySQL: a failed migration is NOT rolled back. Keep one change per file.
CREATE TABLE users (
    id          bigint unsigned NOT NULL AUTO_INCREMENT,
    email       varchar(255)    NOT NULL,
    username    varchar(100)    NOT NULL,
    is_active   boolean         NOT NULL DEFAULT true,
    created_at  timestamp(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at  timestamp(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    CONSTRAINT uq_users_email    UNIQUE (email),
    CONSTRAINT uq_users_username UNIQUE (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE orders (
    id            bigint unsigned NOT NULL AUTO_INCREMENT,
    user_id       bigint unsigned NOT NULL,
    order_number  varchar(50)     NOT NULL,
    total_amount  decimal(12,2)   NOT NULL,
    status        varchar(20)     NOT NULL DEFAULT 'pending',
    created_at    timestamp(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at    timestamp(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    CONSTRAINT uq_orders_order_number UNIQUE (order_number),
    -- table-level FOREIGN KEY: an inline "col INT REFERENCES t(id)" is parsed and silently ignored
    CONSTRAINT fk_orders_users  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT ck_orders_total  CHECK (total_amount > 0),
    CONSTRAINT ck_orders_status CHECK (status IN ('pending', 'processing', 'completed', 'cancelled')),
    KEY ix_orders_user_created (user_id, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

Verified on MySQL 8.4: a column written as `changed_by INT REFERENCES users(id)`
created no foreign key at all (`information_schema.REFERENTIAL_CONSTRAINTS`
listed only the table-level one). InnoDB uses `ix_orders_user_created` for the
foreign key, so it adds no index of its own.

### SQL Server

```sql
-- V1__create_users_orders.sql — SQL Server 2017+ / Azure SQL
-- T-SQL has no CREATE TABLE IF NOT EXISTS; the migration tool guarantees run-once.
SET XACT_ABORT ON;
BEGIN TRANSACTION;

CREATE TABLE dbo.users (
    id          bigint         IDENTITY(1,1) NOT NULL,
    email       nvarchar(255)  NOT NULL,
    username    nvarchar(100)  NOT NULL,
    is_active   bit            NOT NULL CONSTRAINT df_users_is_active  DEFAULT (1),
    created_at  datetime2(3)   NOT NULL CONSTRAINT df_users_created_at DEFAULT (SYSUTCDATETIME()),
    updated_at  datetime2(3)   NOT NULL CONSTRAINT df_users_updated_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT pk_users          PRIMARY KEY CLUSTERED (id),
    CONSTRAINT uq_users_email    UNIQUE (email),
    CONSTRAINT uq_users_username UNIQUE (username)
);

CREATE TABLE dbo.orders (
    id            bigint         IDENTITY(1,1) NOT NULL,
    user_id       bigint         NOT NULL,
    order_number  varchar(50)    NOT NULL,
    total_amount  decimal(12,2)  NOT NULL,
    status        varchar(20)    NOT NULL CONSTRAINT df_orders_status     DEFAULT ('pending'),
    created_at    datetime2(3)   NOT NULL CONSTRAINT df_orders_created_at DEFAULT (SYSUTCDATETIME()),
    updated_at    datetime2(3)   NOT NULL CONSTRAINT df_orders_updated_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT pk_orders              PRIMARY KEY CLUSTERED (id),
    CONSTRAINT uq_orders_order_number UNIQUE (order_number),
    CONSTRAINT fk_orders_users        FOREIGN KEY (user_id) REFERENCES dbo.users (id),  -- NO ACTION = restrict
    CONSTRAINT ck_orders_total        CHECK (total_amount > 0),
    CONSTRAINT ck_orders_status       CHECK (status IN ('pending', 'processing', 'completed', 'cancelled'))
);

CREATE NONCLUSTERED INDEX ix_orders_user_created
    ON dbo.orders (user_id, created_at DESC) INCLUDE (status, total_amount);

COMMIT TRANSACTION;
GO

-- SQL Server has no ON UPDATE for columns: a trigger keeps updated_at honest.
CREATE OR ALTER TRIGGER dbo.trg_orders_updated_at ON dbo.orders AFTER UPDATE AS
BEGIN
    SET NOCOUNT ON;
    IF UPDATE(updated_at) RETURN;   -- the trigger's own update; also lets a caller set it deliberately
    UPDATE o SET updated_at = SYSUTCDATETIME()
    FROM dbo.orders AS o JOIN inserted AS i ON i.id = o.id;
END;
GO
```

Verified on SQL Server 2022: the earlier version of this example, written with
`CREATE TABLE IF NOT EXISTS`, failed with `Msg 156: Incorrect syntax near the
keyword 'IF'`. This one applies cleanly. Surrogate keys here are `bigint
IDENTITY`, not `NEWID()`: random GUIDs as the clustered key fragment the index
and leave pages part-empty (`mssql_dba_skill` §6.4).

---

## 6. Validation Checklist

- [ ] **Applies Cleanly** — All migrations apply, in order, to an empty database in CI
- [ ] **Applies to Real Data** — The new migration applies to a restored copy of production
- [ ] **Primary Keys** — Every table has exactly one primary key
- [ ] **Foreign Keys** — Declared at table level with a name; every FK column leads some index
- [ ] **Delete Rules** — `ON DELETE` is `RESTRICT`/`NO ACTION` unless cascading is the business rule
- [ ] **No Duplicate Indexes** — No index repeats a `PRIMARY KEY`/`UNIQUE` constraint or the left prefix of another index
- [ ] **Query Coverage** — Each important query has an index matching its WHERE + ORDER BY
- [ ] **Constraints** — `CHECK`, `UNIQUE`, `NOT NULL` express the business rules
- [ ] **Defaults** — Explicit and sensible; times default to UTC now
- [ ] **Time Types** — `timestamptz` / `timestamp(6)` in UTC / `datetime2`; never `DATETIME` or zone-less local time
- [ ] **One Change per Migration** — Applied migrations are never edited; fixes are new migrations
- [ ] **Breaking Changes** — Split into expand → migrate → contract across releases
- [ ] **Large Backfills** — Batched, not one table-wide `UPDATE`
- [ ] **Collation** — UTF-8 (`utf8mb4` on MySQL) and consistent across tables
- [ ] **Documentation** — `SCHEMA.md` states each table's purpose and which query each index serves
- [ ] **Partitioning** — Only with a data-lifecycle reason, recorded as an ADR (§9)

---

## 7. Success Criteria

1. **Fresh Build** — Migrations applied to an empty database in CI produce the expected schema
2. **Constraints Enforced** — Tests show a duplicate unique value, a missing parent, and a failed `CHECK` are each rejected
3. **Restrict Works** — Deleting a parent that has children is rejected
4. **Indexes Exist, No Duplicates** — `pg_indexes` / `information_schema.STATISTICS` / `sys.indexes` lists exactly the intended indexes
5. **Plans Use Them** — The main queries show an index seek or index scan in their plans on realistic data
6. **Production Copy** — The new migration applies to restored production data within the maintenance window
7. **Application Agrees** — ORM mapping validation (`spring.jpa.hibernate.ddl-auto=validate`, Alembic autogenerate showing no diff) passes

---

## 8. Integration with Agent Workflows

- `architect:schema` — designs the model and writes the migrations with this skill
- `implementer:build` — adds migrations alongside the code that needs them, in the same PR
- `adr_skill` — a new table shape, partitioning, or denormalisation is a `Database` ADR
- `jira_implementation_skill` — routes "schema change" tickets here

---

## 9. Performance Optimization Guidelines

### Indexing Strategy

**Single-Column Indexes:**
- Primary key and `UNIQUE` constraints are indexed automatically — do not add another
- Foreign key columns, unless a composite index already leads with them
- High-cardinality filter columns

**Composite Indexes (Multi-Column):**
- Query patterns: `WHERE user_id = ? ORDER BY created_at DESC` → index `(user_id, created_at DESC)`
- Covering indexes: add returned columns so the query never touches the table
- Example: `CREATE INDEX ix_orders_user_created ON orders (user_id, created_at DESC) INCLUDE (status, total_amount);`

**Partitioning (Large Tables):**
- Buys data lifecycle (drop or archive a month instantly), not query speed — only queries filtering on the partition key skip partitions
- Every unique index, including the primary key, must include the partition key
- See §11 for PostgreSQL and `mssql_dba_skill` §7 for SQL Server

### Normalization

- **3NF minimum** — eliminate transitive dependencies
- **BCNF recommended** — stricter than 3NF for complex schemas
- **Avoid denormalization** unless performance testing proves necessary, and record it as an ADR
- **Use views** for denormalized read queries (don't duplicate data)

---

## 10. Error Handling

### Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Duplicate key value" when adding a `UNIQUE` | Existing rows already collide | Find and resolve duplicates in a migrate step first, then add the constraint |
| "Foreign key constraint fails" | Child rows reference missing parents | Clean orphans in a migrate step; then add the FK |
| "Column contains null values" on `SET NOT NULL` | Backfill incomplete, or a writer still inserts NULL | Finish expand → migrate before contract |
| Flyway "checksum mismatch" | An applied migration file was edited | Revert the edit; write a new migration |
| Migration waits or times out on a lock | Long transactions hold the table | Run in a window; PostgreSQL: `SET lock_timeout` and retry; `CREATE INDEX CONCURRENTLY` in its own non-transactional migration |
| MySQL migration half-applied | DDL commits implicitly per statement | One DDL change per migration file |

---

## 11. Examples by Pattern

### Audit Logging Pattern

```sql
CREATE TABLE audit_log (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name   varchar(100) NOT NULL,
    record_id    uuid         NOT NULL,
    action       varchar(10)  NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_row      jsonb,
    new_row      jsonb,
    changed_by   uuid,                        -- no FK: audit rows outlive the users they name
    changed_at   timestamptz  NOT NULL DEFAULT now()
);
CREATE INDEX ix_audit_record ON audit_log (table_name, record_id, changed_at DESC);
```

### Soft Delete Pattern

One active row per email; deleted rows keep their email for audit:

```sql
ALTER TABLE users ADD COLUMN deleted_at timestamptz;
ALTER TABLE users DROP CONSTRAINT uq_users_email;
CREATE UNIQUE INDEX uq_users_email_active ON users (email) WHERE deleted_at IS NULL;
```

Verified: after soft-deleting `a@x.io`, one new active `a@x.io` inserts; a
second active one is rejected by `uq_users_email_active`. (SQL Server: a
filtered unique index, `WHERE deleted_at IS NULL`. MySQL has no partial
indexes — use a generated column that is `email` when active and `NULL` when
deleted, with a `UNIQUE` on it.)

### Time Series Data Pattern (PostgreSQL declarative partitioning)

```sql
CREATE TABLE metrics (
    metric_name  varchar(100)  NOT NULL,
    measured_at  timestamptz   NOT NULL,
    value        numeric(18,4) NOT NULL,
    CONSTRAINT pk_metrics PRIMARY KEY (metric_name, measured_at)   -- must include the partition key
) PARTITION BY RANGE (measured_at);

CREATE TABLE metrics_2026_09 PARTITION OF metrics FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
CREATE TABLE metrics_2026_10 PARTITION OF metrics FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
CREATE TABLE metrics_default PARTITION OF metrics DEFAULT;   -- catches rows with no partition yet
```

Verified on PostgreSQL 17: a query for October scanned only
`metrics_2026_10`; a 2027 row landed in `metrics_default`. Create next
month's partition ahead of time (a scheduled job or `pg_partman`) and alert
when the default partition receives rows. `PARTITION BY RANGE (YEAR(...))` is
not PostgreSQL — it fails with `function year(...) does not exist`.

---

## 12. Platform-Specific Notes

### PostgreSQL
- `uuid` with `gen_random_uuid()` (built in since 13), or `bigint GENERATED ALWAYS AS IDENTITY`
- `jsonb` for semi-structured data, with GIN indexes when queried
- Partial indexes (`WHERE deleted_at IS NULL`) and `INCLUDE` columns
- DDL is transactional — a failed Flyway migration rolls back completely
- `CREATE INDEX CONCURRENTLY` avoids blocking writes but cannot run inside a transaction

### MySQL
- `bigint unsigned AUTO_INCREMENT` surrogate keys; InnoDB only — foreign keys need it
- `CHECK` constraints enforced from 8.0.16; ignored before
- Foreign keys only as table-level `CONSTRAINT … FOREIGN KEY` — inline `REFERENCES` is ignored
- DDL commits implicitly — no transactional migrations
- `utf8mb4`, never `utf8` (which is 3-byte and cannot store all of Unicode)

### SQL Server
- `bigint IDENTITY` clustered keys; `NEWSEQUENTIALID()` if a GUID is required — not `NEWID()`
- `datetime2` with `SYSUTCDATETIME()`; `datetimeoffset` when the offset itself matters
- No `CREATE TABLE IF NOT EXISTS`; `DROP … IF EXISTS` exists from 2016
- DDL is transactional; `SET XACT_ABORT ON` so any error rolls the migration back
- Filtered indexes for partial uniqueness; indexed views for materialised aggregates
- Procedures and T-SQL standards: `mssql_advanced_skill`; live diagnosis: `mssql_dba_skill`

---
