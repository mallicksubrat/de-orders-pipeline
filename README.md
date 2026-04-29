# 🛒 Production-Grade Orders Data Pipeline

A scalable batch data pipeline designed to ingest, validate, transform, and monitor order data for analytics use cases.

---

## 📌 Problem
Raw order data is often inconsistent, incomplete, and unreliable, making it difficult to generate accurate business insights.

---

## ⚙️ Solution
This project implements a production-style ETL pipeline with:

- Data ingestion from API / JSON sources
- Data validation and quality checks
- Transformation into canonical format
- Storage in a warehouse (SQLite/Postgres)
- Lineage tracking and observability

---

## 🏗 Architecture
source → extractor → transformer → quality checks → warehouse load → lineage → metrics

---

## 🛠 Tech Stack
Python • Pandas • SQLAlchemy • PostgreSQL • Docker • Airflow (design-ready) • Prometheus

---

## 🔥 Key Features
- Idempotent pipeline execution
- Modular architecture (extract, transform, load separation)
- Data quality validation rules
- Lineage tracking via JSONL logs
- Metrics and observability integration
- Config-driven pipeline (YAML + env overrides)

---

## 📦 Project Structure
- `extractors/` → data ingestion
- `transformers/` → data normalization
- `quality/` → validation rules
- `loaders/` → warehouse + parquet output
- `orchestration/` → pipeline runner
- `dags/` → Airflow integration

---

## 🚀 Running the Pipeline

### Local:
```
PYTHONPATH=src python -m my_project.cli run --env dev
```

### Docker:
```
docker compose up -d postgres mock-api
docker compose run --rm pipeline
```

---

## 📊 Outputs
- Warehouse table (SQLite/Postgres)
- Parquet snapshot
- Lineage logs (JSONL)
- Pipeline execution metrics

---

## ⚙️ Configuration
- YAML-based configs (`configs/`)
- Environment variable overrides supported

---

## 🚀 Future Improvements
- Full Airflow orchestration
- Real-time ingestion (Kafka)
- Data warehouse optimization

---

## 💡 What I Learned
- Designing production-grade pipelines
- Handling real-world data quality issues
- Building observable and scalable systems

Small production-style batch pipeline that ingests order data, validates it, stores it in a warehouse table, writes a parquet snapshot, and emits lineage events.

## Architecture

Flow:

`source -> extractor -> transformer -> quality checks -> warehouse load -> lineage -> metrics`

Core modules:

- `src/my_project/config.py`: typed config loaded from `configs/`
- `src/my_project/extractors/orders_api.py`: order ingestion from HTTP or local JSON
- `src/my_project/transformers/clean_orders.py`: canonical order normalization
- `src/my_project/quality/orders.py`: explicit data quality rules
- `src/my_project/loaders/warehouse.py`: SQL warehouse load and parquet snapshot
- `src/my_project/orchestration/tasks.py`: end-to-end pipeline runner
- `dags/orders_pipeline.py`: optional Airflow wrapper

## Run locally

```bash
PYTHONPATH=src python -m my_project.cli run --env dev
```

Show resolved configuration:

```bash
PYTHONPATH=src python -m my_project.cli show-config --env dev
```

Run tests:

```bash
PYTHONPATH=src pytest -q
```

## Outputs

The development profile reads from `data/raw/orders.json` and writes:

- SQLite warehouse: `data/processed/warehouse.db`
- Parquet artifact: `data/processed/orders.parquet`
- Lineage log: `data/processed/lineage.jsonl`

## Run as a real stack

The repo includes a self-contained deployment profile with:

- `mock-api`: HTTP source serving `mock_api/orders.json`
- `postgres`: warehouse database
- `pipeline`: one-shot batch job container

Start the dependencies:

```bash
cp .env.example .env
docker compose up -d postgres mock-api
```

Run the pipeline container:

```bash
docker compose run --rm pipeline
```

Expected outputs:

- Postgres table: `analytics.orders`
- Parquet artifact: `data/processed/orders.parquet`
- Lineage log: `data/processed/lineage.jsonl`

You can use the convenience targets instead:

```bash
make docker-up
make docker-run
make docker-down
```

## Configuration

`configs/base.yaml` contains the default local runnable setup.

`configs/docker.yaml` runs against the bundled HTTP source and Postgres stack.

`configs/prod.yaml` shows how the same pipeline can target a remote API and Postgres warehouse in production.

Environment variables override YAML values. The main ones are:

- `SOURCE_URL`
- `WAREHOUSE_DB_URL`
- `WAREHOUSE_TABLE_NAME`
- `WAREHOUSE_IF_EXISTS`
- `LINEAGE_PATH`
- `SOURCE_AUTH_HEADER`
- `SOURCE_AUTH_TOKEN`
