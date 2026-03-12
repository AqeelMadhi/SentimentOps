# ADR 001: Parquet as the Standard Data Format

## Status
Accepted

## Date
2026-03-11

## Context
SentimentOps processes Amazon Reviews data at scale (~500k rows). We needed to choose a file format for storing data across all three medallion layers (Bronze, Silver, Gold). The candidate formats were CSV, JSON/JSONL, and Parquet.

## Decision
We use **Apache Parquet** as the standard storage format across all medallion layers.

## Reasoning

### CSV
- Row-oriented: reads entire rows even when only a few columns are needed
- No schema enforcement — data types must be inferred on read
- No compression built in
- Acceptable for small files, unacceptable at 500k+ rows

### JSON/JSONL
- Native format of the Amazon Reviews source data
- Flexible schema but no enforcement
- Row-oriented with high storage overhead
- Appropriate only for Bronze ingestion of raw source data

### Parquet
- **Columnar storage**: only the columns needed for a query are read from disk, dramatically reducing I/O at scale
- **Schema enforcement**: data types are stored with the file — no silent type coercion on read
- **Built-in compression**: typically 3-5x smaller than equivalent CSV
- **Native support** across the entire stack: DuckDB, Polars, Pandas, Delta Lake, HuggingFace Datasets, and Spark all read Parquet natively
- Industry standard for analytical workloads

## Consequences
- All pipeline outputs (Bronze, Silver, Gold) are written as Parquet files
- Raw source JSONL from HuggingFace is converted to Parquet immediately on ingestion into Bronze
- Downstream consumers (DuckDB queries, model training, feature store) read Parquet directly without format conversion
