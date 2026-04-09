# ADR 006: Removing Feast Feature Store

## Status
Accepted

## Date
2026-04-09

## Context
Feast was included in the original architecture to provide training/serving consistency via an offline and online feature store. After defining the full inference requirements of the API, we evaluated whether Feast earns its complexity in this specific use case.

## Decision
We **remove Feast** from the stack.

## Reasoning

### What Feast is designed to solve
Feast prevents training/serving skew — the risk that features computed at training time differ from features served at inference time. It maintains an offline store (batch training) and an online store (low-latency serving). It is the right tool when:
- Features are expensive to compute and must be pre-computed and cached
- Multiple models share the same feature definitions
- There is a real risk of divergence between training and serving feature pipelines

### Why Feast does not apply here
At inference time, the API receives only raw review text in the request payload. The engineered features in the Gold layer — word count, text length, helpful votes, verified purchase — were derived from historical batch data and are not available from the client at inference time.

This means there are no pre-computed features to serve. The only input is raw text, processed directly in the serving layer. A feature store would add significant infrastructure complexity with no benefit.

Adding Feast without a genuine offline/online serving split would be a pattern mismatch — it would effectively be a complicated way to read a Parquet file.

## Consequences
- `feast` removed from `pyproject.toml` data dependencies
- References to Feast removed from ADR 003 and README
- Features derivable from raw text at inference time (word count, text length) are computed inline in the serving layer as pre-processing steps
- If the project evolves to include features that are expensive to compute in real-time and shared across models, Feast should be reconsidered
