# ADR 002: Delta Lake for Medallion Layer Storage

## Status
Accepted

## Date
2026-03-11

## Context
We needed a storage format for the Bronze, Silver, and Gold medallion layers that could handle concurrent writes, schema evolution, and provide data reliability guarantees. Plain Parquet files were the baseline alternative.

## Decision
We use **Delta Lake** on top of Parquet for all three medallion layers.

## Reasoning

### Plain Parquet (baseline)
- No transaction guarantees — a failed mid-write leaves partial or corrupt data
- No concurrent write protection — two pipeline runs writing simultaneously corrupt each other
- No schema enforcement at the table level
- No audit trail — no way to know when data changed or who changed it
- No time travel — cannot query data as it existed at a previous point in time

### Delta Lake
- **ACID transactions**: every write is atomic — either the full write succeeds or nothing is written. No partial states.
- **Transaction log**: every operation (insert, update, delete, schema change) is recorded in a `_delta_log/` folder as JSON commit files. This is the source of all Delta Lake guarantees.
- **Optimistic concurrency control**: concurrent writers are allowed to proceed but only one can commit. The other must retry, preventing corruption.
- **Time travel**: because every version is logged, you can query the table as it existed at any previous version or timestamp — critical for debugging pipeline failures.
- **Schema enforcement**: Delta Lake rejects writes that don't match the table schema, preventing silent data corruption.
- **Schema evolution**: when intentional schema changes are needed, Delta Lake supports them explicitly with `overwriteSchema` or `mergeSchema` options.

## Consequences
- Each medallion layer is a Delta table, not a flat folder of Parquet files
- The `_delta_log/` folder must never be deleted or modified manually
- Time travel enables full pipeline reprocessing from any historical state
- `deltalake` Python package is required in the data dependency group
- DVC tracks the Delta table folders as versioned datasets
