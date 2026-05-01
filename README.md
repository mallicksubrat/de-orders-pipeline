# Production-Grade Orders Data Pipeline

A scalable batch data pipeline that ingests, validates, transforms, and monitors order data for analytics use cases.

---

## Problem

Raw order data is often inconsistent, incomplete, and unreliable, making it difficult to generate accurate business insights. Missing fields, schema drift, and duplicate records cause silent failures in downstream analytics.

---

## Solution

A production-style ETL pipeline with end-to-end data quality enforcement:

- Data ingestion from API and JSON sources
- Schema validation and data quality checks
- Transformation into canonical format
- Storage in a warehouse (SQLite or PostgreSQL)
- Lineage tracking and observability

---

## Architecture

![Pipeline Architecture](docs/architecture.png)

Mock API → Extractor → Transformer → Quality Checks → Warehouse Loader → Lineage Logger → Prometheus Metrics

**Data flow:**
1. Mock API generates synthetic order events
2. Extractor pulls and parses JSON payloads
3. Transformer normalizes fields and applies business rules
4. Quality layer validates schema, nulls, and referential integrity
5. Loader writes to PostgreSQL warehouse and Parquet snapshot
6. Lineage logger records pipeline run metadata as JSONL
7. Prometheus metrics track execution time, record counts, and error rates

---

## Tech Stack

- **Python** — primary processing language
- **Pandas** — in-memory transformation for sub-10GB order datasets
- **SQLAlchemy** — ORM abstraction allowing DB backend swap without code changes
- **PostgreSQL** — ACID-compliant warehouse for order analytics
- **Docker** — reproducible local environment matching production
- **Prometheus** — pipeline execution metrics and alerting hooks

---

## Key Features

- Idempotent pipeline execution — safe to re-run without duplicate data
- Modular architecture — extract, transform, load as separate, testable layers
- Data quality validation rules — null checks, type checks, range checks
- Lineage tracking via JSONL logs — full audit trail per pipeline run
- Config-driven pipeline — YAML configs with environment variable overrides
- Observability — Prometheus metrics for monitoring and alerting

---

## Project Structure

de-orders-pipeline/
├── src/
│   └── my_project/
│       ├── extractors/     # Data ingestion
│       ├── transformers/   # Data normalization
│       ├── quality/        # Validation rules
│       ├── loaders/        # Warehouse + parquet output
│       └── orchestration/  # Pipeline runner
├── dags/                   # Airflow DAG definitions
├── configs/                # YAML configs per environment
├── data/                   # Sample synthetic data
├── docs/adr/               # Architecture decision records
├── infra/terraform/        # Infrastructure as code
├── migrations/             # Database schema migrations
├── mock_api/               # Synthetic order data generator
├── monitoring/             # Prometheus + Grafana config
├── notebooks/              # Exploratory analysis
├── sql/                    # Raw SQL queries
├── tests/                  # Unit and integration tests
├── .env.example            # Environment variable template
├── docker-compose.yml      # Local orchestration
├── Dockerfile              # Container definition
├── Makefile                # Common commands
└── pyproject.toml          # Project metadata and dependencies

---

## Running the Pipeline

### Prerequisites

```bash
cp .env.example .env
# Fill in your values in .env
```

### Local

```bash
PYTHONPATH=src python -m my_project.cli run --env dev
```

### Docker

```bash
docker compose up -d postgres mock-api
docker compose run --rm pipeline
```

### Make commands

```bash
make run        # Run pipeline locally
make test       # Run test suite
make lint       # Run linter
make docker-up  # Start all services
```

---

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Warehouse table | PostgreSQL | Normalized orders for analytics |
| Parquet snapshot | `data/output/` | Compressed columnar backup |
| Lineage logs | `data/lineage/` | JSONL audit trail per run |
| Metrics | Prometheus | Execution time, record counts, errors |

---

## Configuration

Pipeline behavior is controlled via YAML files in `configs/`:

```yaml
pipeline:
  batch_size: 1000
  idempotency_key: order_id
  fail_on_quality_error: true

warehouse:
  backend: postgresql  # or sqlite for local dev
  schema: orders_raw
```

Environment variables override YAML values. See `.env.example` for all supported variables.

---

## Engineering Decisions and Trade-offs

**Why SQLAlchemy over raw psycopg2:**
ORM abstraction allows swapping the DB backend (SQLite locally, PostgreSQL in production) without changing pipeline logic. Reduces environment-specific code.

**Why config-driven YAML:**
Allows environment-specific overrides (dev/staging/prod) without code changes. The pipeline reads environment from `--env` flag and loads the corresponding config file.

**Why idempotent design:**
Re-running the pipeline on the same data produces identical results. Critical for backfills and failure recovery — if the pipeline crashes mid-run, restarting it doesn't create duplicate records.

**Failure modes considered:**
- Source API returning empty payload — pipeline logs warning, skips batch, continues
- Schema drift in incoming JSON — quality layer catches unexpected fields, fails loudly
- PostgreSQL connection timeout during bulk load — SQLAlchemy retry logic with exponential backoff

**At 10x scale:**
Would replace Pandas with PySpark for distributed processing, move from PostgreSQL to a columnar warehouse (Redshift or BigQuery), and introduce Kafka for event-driven ingestion instead of polling.

---

## Future Improvements

- Full Airflow orchestration with retry policies and SLA monitoring
- Real-time ingestion via Kafka consumer
- dbt models for warehouse transformation layer
- Great Expectations integration for richer data quality reporting

---

## Dataset

Synthetic e-commerce orders data generated via mock API to simulate real-world ingestion patterns including late arrivals, null fields, and schema drift. No real customer data is used.
