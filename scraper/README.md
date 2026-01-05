# Job Scraper - Pipeline Directory

## Overview
This directory contains the core data pipeline for scraping, normalizing, and storing job postings following the **Bronze → Silver → Gold** data engineering pattern with cloud-based storage.

## Directory Structure

```
scraper/
├── src/
│   ├── __init__.py
│   ├── schema.py                 # Canonical job schema definition
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── indeed_scraper.py     # Indeed job scraping with error handling
│   ├── storage/
│   │   ├── __init__.py
│   │   └── bronze.py             # Cloud storage via Cloudinary
│   ├── transformation/
│   │   ├── __init__.py
│   │   └── normalize.py          # Data normalization and deduplication
│   └── loader/
│       ├── __init__.py
│       └── database.py           # PostgreSQL loading (Gold layer)
├── pipeline.py                   # Main ETL orchestrator
├── run_scraper.sh                # Automated setup and execution script
├── requirements.txt              # Python dependencies
└── README.md                     # This file

Note: .env file is located in the parent directory (job_scraper/.env) and is shared with the web application.
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

## Prerequisites

### Required Software
- **Python 3.10+**
- **Google Chrome or Chromium** - Required for web scraping
- **Conda** or **Python venv** - For environment management

### Chrome Installation
The scraper uses Selenium with Chrome. Install Chrome for your platform:

**Linux:**
```bash
sudo apt-get install -y google-chrome-stable  # Ubuntu/Debian
sudo dnf install google-chrome-stable         # Fedora/RHEL
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
Download from https://www.google.com/chrome/

### Environment Variables

Create a `.env` file in the **parent directory** (`job_scraper/.env`) with the following:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/dbname

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

This `.env` file is shared between the scraper and web application.

## Key Features

- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Flexible Environments**: Supports both Conda and Python venv
- **Cloud-Native**: Bronze data stored in Cloudinary (Airflow-compatible)
- **Error Handling**: Comprehensive logging and graceful degradation
- **Idempotent**: Re-running won't create duplicates in database
- **Modular**: Each layer (Bronze/Silver/Gold) independently testable
- **Traceable**: Clear data lineage from raw → normalized → database
- **Extensible**: Easy to add new job sources (Greenhouse, Lever, etc.)
- **Production-Ready**: Works with distributed orchestration (Airflow)

## Configuration

### Job Scraper Settings
Edit [`src/ingestion/indeed_scraper.py`](src/ingestion/indeed_scraper.py) to customize:

```python
locations = {
    "uk": "United Kingdom",
    "ae": "United Arab Emirates", 
    "sg": "Singapore"
}

positions = ["software engineer", "data engineer"]
```

### Pagination Safety
The scraper limits pagination to 10 pages per position/location to avoid bot detection:
```python
MAX_PAGES = 10  # Adjust in indeed_scraper.py
```

### Database Table
Jobs are stored in the `indeed_jobs` table. Schema defined in [`src/schema.py`](src/schema.py)
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## Running the Pipeline

### Automated Setup and Execution

The easiest way to run the scraper is using the automated script:

**Using Conda (Recommended):**
```bash
./run_scraper.sh conda
```

**Using Python venv:**
```bash
./run_scraper.sh venv
```

This script will:
1. Detect your operating system (Linux/macOS/Windows)
2. Check for Chrome installation (provides instructions if missing)
3. Create environment if it doesn't exist (conda: `scraper`, venv: `scraper_env`)
4. Install all dependencies from `requirements.txt`
5. Run the complete pipeline

### Manual Execution

If you prefer manual control:

**Setup with Conda:**
```bash
conda create -n scraper python=3.10 -y
conda activate scraper
pip install -r requirements.txt
``` Details

### `src/schema.py`
- Defines canonical job schema (12 required fields)
- Provides validation methods
- Used by all pipeline stages for consistency

### `src/ingestion/indeed_scraper.py`
- Selenium-based scraping with undetected ChromeDriver
- Multi-level error handling (page-level and job-level)
- Comprehensive logging for debugging
- Bot detection bypass with CDP protocol
- Configurable locations and job positions

### `src/storage/bronze.py`
- Cloud storage via Cloudinary
- Unsigned uploads with preset: `job_scraper`
- ITroubleshooting

### Chrome/ChromeDriver Issues
If you see "target window already closed" or similar errors:
1. Ensure Chrome is installed and accessible
2. Check Chrome version matches ChromeDriver (auto-managed by SeleniumBase)
3. Try running in non-headless mode for debugging

### Environment Variables Not Found
```bash
# Verify .env file exists in parent directory (job_scraper/.env)
cd .. && ls -la .env

# Check file contents (safely)
cat ../.env | grep -v SECRET

# Or from scraper directory
ls -la ../.env
```

### Database Connection Errors
```bash
# Test PostgreSQL connection
python -c "from sqlalchemy import create_engine; import os; from dotenv import load_dotenv; load_dotenv(); engine = create_engine(os.getenv('DATABASE_URL')); print('Connected:', engine.connect())"
```

### Cloudinary Upload Failures
- Verify API credentials in `.env`
- Check upload preset `job_scraper` exists in Cloudinary settings
- Ensure unsigned uploads are enabled for the preset

### Import Errors
If you see `ModuleNotFoundError`:
```bash
# Ensure you're in the scraper directory
cd /path/to/scraper

# Verify environment is activated
which python  # Should show path to scraper env

# Reinstall dependencies
pip install -r requirements.txt
```

## Logs and Debugging

The scraper provides detailed logging:
- **INFO**: Normal operation (jobs scraped, pages processed)
- **WARNING**: Recoverable issues (single job extraction failed)
- **ERROR**: Critical failures (page load timeout, database errors)

Example output:
```
INFO - Starting scraping for software engineer in uk
INFO - Navigating to page 1
INFO - Found 15 job listings on page 1
INFO - Successfully extracted 14 jobs from page 1
WARNING - Failed to extract job: Missing required field 'job_title'
INFO - Scraping summary: 14 successful, 1 failed
```

## Production Deployment

For automated execution with Airflow, see [`../airflow/README.md`](../airflow/README.md)

The pipeline is designed to run in production with:
- Scheduled execution (e.g., daily at 2 AM UTC)
- Retry logic on failures
- Alert notifications
- Log aggregation
- Monitoring dashboards

## Dependencies

See [`requirements.txt`](requirements.txt) for full list. Key dependencies:
- `seleniumbase` - Web scraping with bot detection bypass
- `sqlalchemy` - Database ORM
- `pandas` - Data transformation
- `cloudinary` - Cloud storage
- `python-dotenv` - Environment variables
- `psycopg2-binary` - PostgreSQL driver

## Architecture Benefits

### Cloud Storage (Cloudinary)
- **Persistent**: Data survives restarts and crashes
- **Distributed**: Any worker can access bronze data
- **Scalable**: No local disk limitations
- **Immutable**: Raw data preserved for audit and replay
- **Cost-Effective**: Free tier supports development and testing

### Modular Design
- **Testable**: Each layer can be unit tested independently
- **Maintainable**: Clear separation of concerns
- **Extensible**: Add new sources without touching existing code
- **Observable**: Each stage logs its operations

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