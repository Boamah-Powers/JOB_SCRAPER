# Airflow Job Scraper Pipeline

This directory contains the Apache Airflow setup for automating the job scraper pipeline.

## Prerequisites

1. **Python 3.10** installed on your system
2. **Conda** or **Python venv** capability
3. **Environment Variables** - Create a `.env` file in the `scraper/` directory with:
   ```bash
   DATABASE_URL=postgresql://user:password@host:port/database
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

## Installation

Run the installation script with your preferred environment manager:

### Using Conda (Recommended)
```bash
cd airflow
./airflow_install.sh conda
```

### Using Python venv
```bash
cd airflow
./airflow_install.sh venv
```

This script will:
- Create an Airflow environment (conda or venv)
- Install Apache Airflow 3.0.6 with PostgreSQL support
- Configure Airflow settings (executor, auth manager, secrets)
- Initialize the Airflow database
- Create an admin user

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin`
- Email: `admin@example.com`

## Starting Airflow

From the `airflow/` directory, run:

```bash
./run_airflow.sh
```

This script will:
- Auto-detect and activate your environment (conda or venv)
- Start all Airflow components:
  - Scheduler
  - DAG Processor
  - Triggerer
  - API Server (Web UI on port 8080)

**Stopping Airflow:**
Press `Ctrl+C` to gracefully shut down all components.

## Accessing the Web UI

1. Open your browser and navigate to: http://localhost:8080
2. Login with the admin credentials (default: admin/admin)
3. You should see the `job_scraper_pipeline` DAG

## Running the Pipeline

### Via Web UI
1. Go to http://localhost:8080
2. Find the `job_scraper_pipeline` DAG
3. Toggle it to "ON" if it's paused
4. Click the play button (▶) to trigger a manual run

### Via Command Line
```bash
# Activate your environment first
source airflow_env/bin/activate  # for venv
# OR
conda activate airflow  # for conda

# Trigger the DAG
airflow dags trigger job_scraper_pipeline
```

## DAG Schedule

The pipeline runs automatically **daily at 2:00 AM UTC**.

You can modify the schedule in `dags/job_scraper_dag.py`:
```python
schedule='0 2 * * *'  # Cron expression: minute hour day month day_of_week
```

## Pipeline Overview

The DAG executes the following stages:

1. **Extract** - Scrapes job postings from Indeed for multiple locations
2. **Bronze Layer** - Saves raw JSON data to Cloudinary
3. **Silver Layer** - Normalizes and deduplicates job data
4. **Gold Layer** - Loads cleaned data into PostgreSQL database

## Logs

Airflow logs are stored in `airflow/logs/`:
- DAG processor logs: `logs/dag_processor/`
- Task execution logs: `logs/dag_id=job_scraper_pipeline/`

To view logs for a specific task run, check the Web UI or navigate to the log directory.

## Troubleshooting

### Environment Not Found
If `run_airflow.sh` reports no environment found:
```bash
./airflow_install.sh conda  # or venv
```

### Port 8080 Already in Use
If port 8080 is occupied, modify `airflow.cfg`:
```ini
[webserver]
web_server_port = 8081  # Change to available port
```

Or kill the process using port 8080:
```bash
lsof -ti:8080 | xargs kill -9
```

### DAG Not Appearing
1. Check that `dags/` folder exists in `AIRFLOW_HOME`
2. Verify DAG file has no syntax errors:
   ```bash
   python dags/job_scraper_dag.py
   ```
3. Check scheduler logs for import errors

### Database Connection Issues
Ensure your `.env` file in `scraper/` directory has the correct `DATABASE_URL` and the database is accessible.

### Conda Environment Issues
If conda activation fails, ensure conda is initialized for bash:
```bash
conda init bash
source ~/.bashrc  # or ~/.bash_profile on macOS
```

## Configuration

The Airflow installation uses:
- **Executor**: LocalExecutor (supports parallel task execution)
- **Auth Manager**: FAB (Flask AppBuilder) with username/password
- **Database**: SQLite for metadata (can be upgraded to PostgreSQL)
- **Security**: Auto-generated JWT secrets for secure sessions

To modify settings, edit `airflow.cfg` after installation.

## File Structure

```
airflow/
├── README.md                   # This file
├── airflow_install.sh          # Installation script
├── run_airflow.sh              # Startup script
├── airflow.cfg                 # Airflow configuration (generated)
├── dags/
│   └── job_scraper_dag.py      # Pipeline DAG definition
├── logs/                       # Execution logs
└── plugins/                    # Custom plugins (optional)
```

## Upgrading

To upgrade Airflow or dependencies:

1. Activate your environment
2. Run pip upgrade:
   ```bash
   pip install --upgrade apache-airflow
   ```
3. Run database migration:
   ```bash
   airflow db migrate
   ```

## Support

For issues or questions:
- Check Airflow logs in `logs/` directory
- Review Apache Airflow documentation: https://airflow.apache.org/docs/
- Verify environment variables are correctly set
