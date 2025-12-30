# Job Scraper - Refactored Project Structure

## Overview
This project implements a modular data pipeline for scraping, normalizing, and storing job postings following the **Bronze → Silver → Gold** data engineering pattern with cloud-based storage for Airflow compatibility.

## Project Structure

```
job_scraper/
├── src/
│   ├── schema.py                 # Canonical job schema definition
│   ├── ingestion/
│   │   └── indeed_scraper.py     # Indeed job scraping logic
│   ├── storage/
│   │   └── bronze.py             # Cloud storage via Cloudinary
│   ├── transformation/
│   │   └── normalize.py          # Data normalization and cleaning
│   └── loader/
│       └── database.py           # Database loading (Gold layer)
├── docs/
│   ├── project_plan.md
│   └── phase_1.md
├── pipeline.py                   # Main ETL orchestrator
├── scraper_sb.py                 # Original monolithic script (deprecated)
├── requirements.txt
└── .env                          # Database & Cloudinary credentials
```

## Data Flow

```
┌─────────────────┐
│   1. EXTRACT    │ → Scrape jobs from Indeed
│   (Ingestion)   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   2. BRONZE     │ → Save raw JSON to Cloudinary (immutable)
│  (Cloud Storage)│    Cloudinary: job_scraper/bronze/indeed_*
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   3. SILVER     │ → Normalize, validate, deduplicate
│  (Transform)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   4. GOLD       │ → Load to PostgreSQL
│  (Database)     │    (incremental, no duplicates)
└─────────────────┘
```

## Running the Pipeline

### Prerequisites
Create a `.env` file with:
```bash
# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Single Command Execution
```bash
python pipeline.py
```

This will:
1. Scrape jobs from Indeed (UK, UAE, Singapore)
2. Save raw data to Cloudinary (cloud storage)
3. Normalize and deduplicate jobs
4. Load only new jobs to PostgreSQL

### Key Features
- **Cloud-Native**: Bronze data stored in Cloudinary for Airflow compatibility
- **Idempotent**: Re-running won't create duplicates
- **Modular**: Each layer can be tested independently
- **Traceable**: Clear data lineage from raw → normalized → database
- **Extensible**: Easy to add new job sources
- **Production-Ready**: Works with distributed Airflow workers

## Modules

### `src/schema.py`
Defines the canonical job schema that all sources map to.

### `src/ingestion/indeed_scraper.py`
Handles web scraping with bot detection bypass, pagination, and data extraction.

### `src/storage/bronze.py`
Manages raw data storage in Cloudinary with immutability guarantees. Uses unsigned uploads with upload preset for cloud storage.

### `src/transformation/normalize.py`
Normalizes raw data to canonical schema and removes duplicates.

### `src/loader/database.py`
Loads data to PostgreSQL with duplicate detection and incremental loading.

## Phase 1 Compliance

✅ **Canonical Schema** - Defined in `src/schema.py`  
✅ **Single Data Source** - Indeed scraper implemented  
✅ **Bronze Storage** - Raw JSON stored in Cloudinary (cloud-based)  
✅ **Silver Transformation** - Normalization and deduplication  
✅ **Database Persistence** - PostgreSQL with validation  
✅ **Idempotency** - No duplicates on re-runs  
✅ **Airflow-Ready** - Cloud storage enables distributed execution

## Architecture Benefits

### Cloud Storage (Cloudinary)
- **Persistent**: Data survives container/worker restarts
- **Accessible**: Any Airflow worker can access bronze data
- **Scalable**: No local disk limitations
- **Immutable**: Raw data preserved for audit and replay

## Next Steps (Phase 2+)
- Add more job sources (Greenhouse, Lever)
- Implement Airflow/Prefect orchestration
- Add data quality tests (Great Expectations)
- Build analytics dashboard (Streamlit/FastAPI)
