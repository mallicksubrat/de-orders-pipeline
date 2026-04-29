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

### Local
```bash
PYTHONPATH=src python -m my_project.cli run --env dev
```

### Docker
```bash
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
