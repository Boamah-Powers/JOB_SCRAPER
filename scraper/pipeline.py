"""
Job Scraper Pipeline
--------------------
Main orchestration script for the job scraping data pipeline.

Pipeline stages:
1. Extract: Scrape jobs from Indeed (Bronze)
2. Store: Save raw data to JSON files (Bronze)
3. Transform: Normalize and deduplicate (Silver)
4. Load: Insert into PostgreSQL database (Gold)

This implements the ETL pattern with clear data lineage:
Bronze (raw) → Silver (normalized) → Gold (database)
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from src.ingestion.indeed_scraper import IndeedScraper
from src.storage.bronze import BronzeStorage
from src.transformation.normalize import JobNormalizer
from src.loader.database import DatabaseLoader


def run_pipeline():
    """
    Execute the complete job scraping pipeline.
    """
    print("\n" + "="*70)
    print("STARTING JOB SCRAPER PIPELINE")
    print("="*70)
    print(f"Run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Load environment variables
    load_dotenv()
    database_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://username:password@localhost:5432/database_name"
    )
    
    # Configuration
    locations = {
        "uk": "United Kingdom",
        "ae": "UAE",
        "sg": "Singapore"
    }
    
    positions = ["software engineer", "data engineer"]
    
    # ========================================================================
    # STAGE 1: EXTRACT (Ingestion)
    # ========================================================================
    print("\n" + "="*70)
    print("STAGE 1: EXTRACT - Scraping job data from Indeed")
    print("="*70 + "\n")
    
    scraper = IndeedScraper(
        locations=locations,
        positions=positions,
        headless=True
    )
    
    raw_jobs = scraper.scrape_all()
    print(f"\nExtract complete: {len(raw_jobs)} jobs scraped\n")
    
    # ========================================================================
    # STAGE 2: BRONZE STORAGE (Raw data persistence)
    # ========================================================================
    print("="*70)
    print("STAGE 2: BRONZE - Saving raw data to JSON")
    print("="*70 + "\n")
    
    bronze = BronzeStorage(upload_preset="job_scraper_indeed")
    bronze_file = bronze.save_raw_jobs(
        jobs=raw_jobs,
        source="indeed",
        run_date=datetime.now()
    )
    print()
    
    # ========================================================================
    # STAGE 3: TRANSFORM (Normalization and cleaning)
    # ========================================================================
    print("="*70)
    print("STAGE 3: SILVER - Normalizing and deduplicating data")
    print("="*70 + "\n")
    
    normalized_df = JobNormalizer.transform(raw_jobs)
    print()
    
    # ========================================================================
    # STAGE 4: LOAD (Database persistence)
    # ========================================================================
    print("="*70)
    print("STAGE 4: GOLD - Loading data to PostgreSQL")
    print("="*70 + "\n")
    
    loader = DatabaseLoader(database_url=database_url)
    new_jobs_count = loader.load_incremental(normalized_df)
    
    # ========================================================================
    # PIPELINE SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("PIPELINE SUMMARY")
    print("="*70)
    print(f"Jobs scraped:        {len(raw_jobs)}")
    print(f"Jobs normalized:     {len(normalized_df)}")
    print(f"New jobs inserted:   {new_jobs_count}")
    print(f"Bronze file:         {bronze_file}")
    print(f"Completed at:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    print("Pipeline completed successfully!\n")


if __name__ == "__main__":
    run_pipeline()
