# ADR 004: Gold Layer Design — Single ML-Focused Table

## Status
Accepted

## Date
2026-04-09

## Context
We needed to decide how to structure the Gold layer for this project. Options considered were: a single ML-focused table, multiple domain-specific tables (analytics, reporting, ML), or a generic "business-ready" table with no ML-specific logic.

## Decision
We use a **single Gold table** optimised specifically for sentiment classification training.

The table contains:
- `text` and `title` — raw review text for model input
- `sentiment_label` — mapped from rating (1-2 = bad, 3 = average, 4-5 = good)
- `text_word_count`, `title_word_count` — derived features
- `text_text_length`, `title_text_length` — character count features
- `helpful_vote`, `verified_purchase` — behavioural signals
- `category` — dataset source category

## Reasoning

### Multiple Gold tables (alternative)
- Appropriate when the same data serves multiple distinct downstream use cases (analytics dashboards, recommendation systems, NLP models)
- Adds maintenance overhead for a single-use-case project
- Premature abstraction at this stage

### Single ML-focused Gold table
- This project has one primary ML use case: sentiment classification
- All features in the table are model-agnostic within the NLP domain — word count, text length, and behavioural signals are reusable across different text classifiers
- Tokenisation and embeddings are model-specific and belong in the training pipeline, not Gold
- Keeps the pipeline simple and focused

### Design principle
Temporal features (day of week, month) were explicitly excluded — sentiment on Amazon reviews is unlikely to vary meaningfully by time, and including noise features hurts model quality.

## Consequences
- Gold layer contains one Delta table: `data/gold/reviews_ml/`
- ML engineers read directly from Gold for training
- If a new ML use case arises with significantly different feature requirements, a second Gold table should be created rather than polluting this one
