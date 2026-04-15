# ADR 003: Medallion Architecture (Bronze / Silver / Gold)

## Status
Accepted

## Date
2026-03-11

## Context
We needed a data organisation strategy for the pipeline that takes raw Amazon Reviews data through to model-ready features. The alternative was a flat pipeline that transforms data in a single pass directly to a final dataset.

## Decision
We adopt the **Medallion Architecture** with three distinct layers: Bronze, Silver, and Gold.

## Layer Definitions

### Bronze — Raw Ingestion
- Contains raw data exactly as received from the source (HuggingFace Amazon Reviews dataset)
- **Never modified after write** — immutable source of truth
- Schema matches source exactly, including nulls, duplicates, and inconsistencies
- Format: Delta Lake table (Parquet + transaction log)
- Purpose: guarantees we can always reprocess from the original data regardless of downstream bugs

### Silver — Cleaned & Validated
- Produced by applying cleaning transforms to Bronze
- Removes duplicates, handles nulls, standardises data types
- Schema is enforced and documented
- Pandera schema validation runs at this layer to assert data quality contracts (see ADR 005)
- Format: Delta Lake table
- Purpose: a reliable, clean dataset that any downstream consumer can trust

### Gold — Feature-Engineered
- Produced by applying feature engineering transforms to Silver
- Contains model-ready features: tokenised text, encoded labels, derived features (review length, sentiment score bins, etc.)
- Optimised for training and serving consumption
- Format: Delta Lake table
- Purpose: separates feature engineering logic from model training logic, enabling feature reuse

## Reasoning

### Single-pass pipeline (alternative)
- Faster to implement initially
- No auditability — if the final dataset is wrong, the cause is hard to trace
- Cannot reprocess selectively — a bug in cleaning requires rerunning everything including expensive feature engineering
- No intermediate quality checks

### Medallion Architecture
- **Separation of concerns**: ingestion, cleaning, and feature engineering are independent, testable steps
- **Debuggability**: failures can be isolated to a specific layer
- **Reprocessability**: Silver can be rebuilt from Bronze, Gold can be rebuilt from Silver, independently
- **Industry standard**: directly maps to Databricks lakehouse patterns used in production ML teams

## Consequences
- Three separate Delta tables: `data/bronze/`, `data/silver/`, `data/gold/`
- Each layer has its own pipeline script in `pipelines/`
- Pandera validation runs on the Silver layer before writing (see ADR 005)
- DVC tracks each layer independently for versioning
