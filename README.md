# Job Scraper - Automated Job Posting Pipeline

A production-ready data engineering pipeline for scraping, processing, and storing job postings from multiple sources. Built with modular architecture following the **Bronze → Silver → Gold** pattern with cloud storage and Airflow orchestration.

## Project Overview

This project automates the collection of job postings across different locations and stores them in a structured database for analysis and tracking. It uses web scraping, cloud storage, data normalization, and automated scheduling to maintain an up-to-date job database.

### Key Features

-  **Multi-Source Scraping** - Currently supports Indeed (extensible to Greenhouse, Lever, LinkedIn)
-  **Cloud-Native** - Bronze layer stored in Cloudinary for distributed access
-  **Automated Orchestration** - Daily execution via Apache Airflow
-  **Error Resilient** - Comprehensive error handling with graceful degradation
-  **Idempotent** - Safe to re-run without creating duplicates
-  **Cross-Platform** - Works on Linux, macOS, and Windows
-  **Flexible Setup** - Supports both Conda and Python venv

## Project Structure

```
job_scraper/
├── README.md                  # This file
├── .gitignore
│
├── scraper/                   # Core ETL pipeline
│   ├── src/
│   │   ├── schema.py          # Canonical job schema
│   │   ├── ingestion/         # Web scraping modules
│   │   ├── storage/           # Cloud storage (Bronze)
│   │   ├── transformation/    # Data normalization (Silver)
│   │   └── loader/            # Database loading (Gold)
│   ├── pipeline.py            # ETL orchestrator
│   ├── run_scraper.sh         # Automated setup script
│   ├── requirements.txt
│   └── README.md              # Scraper documentation
│
└── airflow/                   # Orchestration setup
    ├── dags/
    │   └── job_scraper_dag.py # Daily pipeline DAG
    ├── airflow_install.sh     # Airflow setup script
    ├── run_airflow.sh         # Airflow launcher
    └── README.md              # Airflow documentation
```

## Quick Start

### Prerequisites

- **Python 3.10+**
- **PostgreSQL** - For storing job data
- **Cloudinary Account** - For bronze layer storage (free tier available)
- **Google Chrome** - For web scraping
- **Conda** or **Python venv**

### 1. Clone the Repository

```bash
git clone https://github.com/Boamah-Powers/JOB_SCRAPER.git
cd job_scraper
```

### 2. Configure Environment Variables

Create a `.env` file in the `scraper/` directory:

```bash
# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Run the Scraper (Standalone)

```bash
cd scraper
./run_scraper.sh conda  # or: ./run_scraper.sh venv
```

This will scrape jobs, store them in Cloudinary, normalize data, and load to PostgreSQL.

### 4. Set Up Airflow (Production)

For automated daily execution:

```bash
cd airflow
./airflow_install.sh conda  # or: ./airflow_install.sh venv
./run_airflow.sh
```

Access the Airflow UI at http://localhost:8080 (admin/admin)

## Data Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ETL PIPELINE                             │
└─────────────────────────────────────────────────────────────────┘

1. EXTRACT (Ingestion)
   ↓
   └─→ Scrape job postings from Indeed
       • Multi-location support (UK, UAE, Singapore)
       • Pagination with safety limits
       • Bot detection bypass
       • Error handling per job/page

2. BRONZE (Raw Storage)
   ↓
   └─→ Save raw JSON to Cloudinary
       • Cloud-based immutable storage
       • Timestamped for traceability
       • Accessible by all workers
       • Audit trail preservation

3. SILVER (Transformation)
   ↓
   └─→ Normalize and deduplicate
       • Map to canonical schema
       • Validate required fields
       • Remove duplicates
       • Add metadata

4. GOLD (Database)
   ↓
   └─→ Load to PostgreSQL
       • Incremental loading
       • Duplicate prevention
       • Indexed for performance
       • Ready for analytics
```

## Documentation

- **[Scraper Documentation](scraper/README.md)** - Detailed guide for running the pipeline
- **[Airflow Documentation](airflow/README.md)** - Orchestration setup and troubleshooting

## Configuration

### Job Sources and Locations

Edit [`scraper/src/ingestion/indeed_scraper.py`](scraper/src/ingestion/indeed_scraper.py):

```python
locations = {
    "uk": "United Kingdom",
    "ae": "United Arab Emirates",
    "sg": "Singapore"
}

positions = [
    "software engineer",
    "data engineer"
]
```

### Airflow Schedule

Edit [`airflow/dags/job_scraper_dag.py`](airflow/dags/job_scraper_dag.py):

```python
schedule='0 2 * * *'  # Daily at 2:00 AM UTC
```

## 🔧 Technologies Used

| Component | Technology |
|-----------|-----------|
| **Web Scraping** | SeleniumBase (undetected ChromeDriver) |
| **Cloud Storage** | Cloudinary |
| **Database** | PostgreSQL + SQLAlchemy |
| **Orchestration** | Apache Airflow 3.0.6 |
| **Data Processing** | Pandas |
| **Environment** | Conda / Python venv |
| **Version Control** | Git + GitHub |

## Development

### Project Layout

The project follows a modular architecture:

- **`scraper/src/`** - Core pipeline modules (single responsibility principle)
- **`scraper/pipeline.py`** - Orchestrates the ETL flow
- **`airflow/dags/`** - Airflow DAG definitions
- **`docs/`** - Planning and architecture documentation

### Adding New Job Sources

1. Create new scraper in `scraper/src/ingestion/`
2. Implement the same interface as `indeed_scraper.py`
3. Map fields to canonical schema in `src/schema.py`
4. Update `pipeline.py` to include new source
5. Test independently before integrating

### Running Tests

```bash
cd scraper
python -m pytest tests/  # (when tests are implemented)
```

## Troubleshooting

### Common Issues

**Chrome not found:**
```bash
# Install Chrome for your platform
# Linux: sudo apt-get install google-chrome-stable
# macOS: brew install --cask google-chrome
```

**Database connection error:**
```bash
# Verify DATABASE_URL in .env
# Test connection:
psql $DATABASE_URL -c "SELECT 1"
```

**Cloudinary upload fails:**
- Check API credentials in `.env`
- Verify upload preset `job_scraper` exists and allows unsigned uploads

**Airflow DAG not appearing:**
```bash
# Check for syntax errors
python airflow/dags/job_scraper_dag.py

# Verify AIRFLOW_HOME is set correctly
echo $AIRFLOW_HOME
```

For detailed troubleshooting, see:
- [Scraper Troubleshooting](scraper/README.md#troubleshooting)
- [Airflow Troubleshooting](airflow/README.md#troubleshooting)

## Usage Examples

### Standalone Scraper Run

```bash
cd scraper
python pipeline.py
```

Output:
```
INFO - Stage 1: Extract - Starting scraping...
INFO - Scraped 45 jobs successfully
INFO - Stage 2: Bronze - Saving to Cloudinary...
INFO - Stage 3: Silver - Normalizing data...
INFO - Stage 4: Gold - Loading to database...
INFO - Loaded 42 new jobs (3 duplicates skipped)
```

### Airflow Manual Trigger

```bash
cd airflow
source airflow_env/bin/activate  # or: conda activate airflow
airflow dags trigger job_scraper_pipeline
```

### Check Latest Jobs

```sql
-- Connect to your PostgreSQL database
SELECT job_title, company_name, location, posted_date
FROM indeed_jobs
ORDER BY scraped_at DESC
LIMIT 10;
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional job board integrations
- Enhanced error handling
- Data quality monitoring
- Performance optimizations
- Test coverage
- Documentation improvements

## Links

- **GitHub Repository**: https://github.com/Boamah-Powers/JOB_SCRAPER
- **Cloudinary**: https://cloudinary.com/
- **Apache Airflow**: https://airflow.apache.org/
- **SeleniumBase**: https://seleniumbase.io/

## Support

For issues or questions:
1. Check the relevant README files ([scraper](scraper/README.md), [airflow](airflow/README.md))
2. Review error logs in `airflow/logs/` or terminal output
3. Verify environment variables and dependencies
4. Consult the troubleshooting sections

---

**Built with ❤️ for automated job searching and data engineering practice**
