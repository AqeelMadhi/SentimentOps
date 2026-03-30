# SentimentOps

> End-to-end NLP pipeline with medallion architecture, MLOps, and REST API serving for sentiment classification on Amazon review data.

## Architecture

```
Raw Data → Bronze → Silver → Gold → Feature Store
                                         ↓
                               Training Pipeline
                                         ↓
                          MLflow Experiment Tracking
                                         ↓
                              Model Registry (Azure ML)
                                         ↓
                            CI/CD (GitHub Actions)
                                         ↓
                          FastAPI Serving (Docker → Render)
                                         ↓
                              Frontend Demo (HF Spaces)
```

## Project Structure

```
sentimentops/
├── data/                    # DVC-tracked, Delta Lake bronze/silver/gold
├── pipelines/               # Ingestion, transform, feature engineering
├── features/                # Feast feature store definitions
├── training/                # Baseline, fine-tuning, evaluation
├── api/                     # FastAPI application
├── monitoring/              # Prometheus metrics, Grafana dashboards
├── frontend/                # Demo UI
├── .github/workflows/       # CI/CD pipelines
├── pyproject.toml           # Dependency groups by layer
├── Dockerfile               # API container
└── dvc.yaml                 # Pipeline DAG
```

## Stack

| Layer | Tools |
|---|---|
| Data Engineering | DuckDB, Polars, Delta Lake, DVC, Great Expectations, Feast |
| Modelling | DistilBERT, scikit-learn, Optuna, SHAP, MLflow |
| MLOps | MLflow, Azure ML, GitHub Actions, Docker |
| Serving | FastAPI, Redis, Prometheus, Grafana, Render |

## Quickstart

```bash
# Install dependencies for a specific layer
poetry install --with data
poetry install --with ml
poetry install --with api

# Configure pre commit setup
pre commit install

# Run tests
poetry run pytest

# Lint
poetry run ruff check .
```

## Status

| Layer | Status |
|---|---|
| Data Engineering | In Progress |
| Modelling | Planned |
| MLOps |  Planned |
| Serving | Planned |
| Frontend | Planned |


## Archtecture Decision Records
[Architecture Decision Records](docs/adr/)