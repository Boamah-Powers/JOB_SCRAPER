"""
Job Scraper DAG
---------------
Daily job scraping pipeline orchestrated by Airflow.

This DAG runs the complete ETL pipeline:
1. Scrapes jobs from Indeed
2. Stores raw data in Cloudinary (Bronze)
3. Normalizes and deduplicates (Silver)
4. Loads to PostgreSQL (Gold)

Schedule: Daily at 2 AM UTC
"""

from pathlib import Path
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

# Get the scraper directory path
SCRAPER_DIR = Path(__file__).parent.parent.parent / "scraper"


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 31),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'job_scraper_pipeline',
    default_args=default_args,
    description='Daily job scraping and ETL pipeline',
    schedule='0 2 * * *',  # Daily at 2 AM UTC
    catchup=False,  # Don't run for past dates
    tags=['etl', 'jobs', 'indeed'],
)

# Define the bash command to activate conda environment and run pipeline
bash_command = f"""
source $(conda info --base)/etc/profile.d/conda.sh && \
conda activate scraper && \
cd {SCRAPER_DIR} && \
python pipeline.py
"""

# Alternative: If using Python venv instead of conda (uncomment and adjust path)
# bash_command = f"""
# source /path/to/your/venv/bin/activate && \
# cd {SCRAPER_DIR} && \
# python pipeline.py
# """

# Define the task
scrape_and_load_jobs = BashOperator(
    task_id='run_job_scraper_pipeline',
    bash_command=bash_command,
    dag=dag,
)

# Single task - no dependencies needed
scrape_and_load_jobs
