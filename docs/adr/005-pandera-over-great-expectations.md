# ADR 005: Pandera over Great Expectations for Data Validation

## Status
Accepted

## Date
2026-04-09

## Context
We needed a data validation library to assert data quality contracts on the Silver layer. Great Expectations was originally included in the stack as the default industry choice. We evaluated it against the actual project stack and requirements.

## Decision
We use **Pandera** with native Polars support instead of Great Expectations.

## Reasoning

### Great Expectations (original choice)
- Industry-standard for data validation in Databricks and Spark-based stacks, which is the environment I typically work in
- When the stack was initially designed, GE was the natural default choice given that familiarity
- However, on examining the dataset (~20GB Amazon Reviews), it became clear that distributed processing was not required — the data fits comfortably in single-machine memory
- This led to choosing Polars over Spark for its performance on single-machine workloads
- GE does not support Polars DataFrames natively — only Pandas and Spark
- Using GE would require converting Polars DataFrames to Pandas purely for validation, adding unnecessary overhead and reintroducing a Pandas dependency we had deliberately avoided

### Pandera
- Native Polars support — no conversion required
- Lightweight schema definition: column types, nullability, value constraints defined as a Python class
- Consistent with the project's Polars-first approach
- Once the decision to use Polars was made, Pandera was the correct tool to match — GE belongs in Spark stacks, Pandera belongs in Polars stacks

## Consequences
- `great-expectations` removed from `pyproject.toml` data dependencies
- `pandera[polars]` added to `pyproject.toml` data dependencies
- Silver layer validation implemented in `pipelines/silver_validation.py`
- If the project migrates to Databricks with Spark, validation approach should be revisited
