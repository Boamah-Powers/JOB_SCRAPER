"""
Indeed Job Scraper
------------------
This script scrapes job listings from Indeed across multiple locations and positions,
then stores the results in a PostgreSQL database.

The script:
1. Iterates through configured locations (UK, UAE, Singapore)
2. For each location, searches for multiple job positions
3. Extracts job details (title, company, location, URL)
4. Handles pagination to scrape all available pages
5. Checks for duplicates before inserting into the database

Dependencies:
- seleniumbase: For web scraping with bot detection bypass
- pandas: For data manipulation
- sqlalchemy: For database connections
- python-dotenv: For environment variable management
"""

import os
import pandas as pd
from re import search
from seleniumbase import SB
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration - pulled from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/database_name")
engine = create_engine(DATABASE_URL)

# Configuration: Indeed domains mapped to their respective locations
locations = {
    "uk": "United Kingdom",
    "ae": "UAE",
    "sg": "Singapore"
}

# Configuration: Job positions to search for
positions = ["software engineer", "data engineer"]

# Master list to store all jobs across all locations and positions
all_jobs = []

# Iterate through each location (UK, UAE, Singapore)
for domain, location in locations.items():
    print("="*70)
    print(f"Scraping jobs in: {location} ({domain})")
    print("="*70)
    
    # For each location, search for all configured job positions
    for position in positions:
        print("-"*50)
        print(f"Position: {position}")
        print("-"*50)
        
        # Initialize SeleniumBase with undetected mode to bypass bot detection
        # uc=True: Enables undetected-chromedriver mode
        # headless=True: Runs browser without GUI (faster, good for automation)
        # test=True: Enables test mode features
        # locale="en": Sets browser locale to English
        with SB(uc=True, headless=True, test=True, locale="en") as sb:
            # Build Indeed URL with search parameters
            # fromage=3: Jobs posted within last 3 days
            url = "https://{}.indeed.com/jobs?q={}&l={}&fromage=3".format(domain, position.replace(" ", "+"), location.replace(" ", "+"))
            
            # Activate CDP (Chrome DevTools Protocol) mode for better control
            sb.activate_cdp_mode(url)
            sb.sleep(2)  # Wait for page to load
            
            # Solve any CAPTCHA that might appear
            sb.solve_captcha()
            sb.sleep(2)  # Wait after CAPTCHA resolution

            # Extract total job count from page (handles formats like "50+" or "1,000")
            job_count_text = sb.find_element(".jobsearch-JobCountAndSortPane-jobCount").text.split(" ")[0]
            job_count = int(job_count_text.replace('+', '').replace(',', ''))  # Remove + and commas
            
            # List to store jobs for this specific position/location combination
            jobs = []

            # Pagination loop: Continue scraping until no more pages
            while True:
                # Extract all job elements from current page using CSS selectors
                job_titles = sb.find_elements(".jobTitle")
                company_names = sb.find_elements(".css-19eicqx")
                company_locations = sb.find_elements(".css-1f06pz4")
                urls = sb.find_elements("h2.jobTitle > a")

                # Iterate through each job listing on the current page
                # zip() combines all 4 lists element-by-element
                for job_data in zip(job_titles, company_names, company_locations, urls):
                    # Extract text content from each element
                    job_title = job_data[0].text
                    company_name = job_data[1].text
                    company_location = job_data[2].text
                    job_url = "https://{}.indeed.com".format(domain) + job_data[3].get_attribute("href")

                    # Display extracted job information
                    print("-"*10)
                    print("Job title:", job_title)
                    print("Company name:", company_name)
                    print("Company location:", company_location)
                    print("Indeed Url:", job_url)

                    # Filter: Only keep URLs with '/rc/clk?jk=' pattern (valid job links)
                    # This excludes sponsored posts and other non-standard listings
                    if search(r'/rc/clk\?jk=', job_url):
                        # Create job record dictionary with all relevant fields
                        job_record = {
                            'job_title': job_title,
                            'company_name': company_name,
                            'company_location': company_location,
                            'job_url': job_url,
                            'search_position': position,  # Track what position we searched for
                            'search_location': location,   # Track what location we searched in
                            'domain': domain               # Track which Indeed domain (uk/ae/sg)
                        }
                        jobs.append(job_record)          # Add to position-specific list
                        all_jobs.append(job_record)      # Add to master list

                print("-"*10)
                
                # Pagination: Check if "Next" button exists on current page
                if sb.is_element_present('a[data-testid="pagination-page-next"]'):
                    print("Next page button present, clicking...")
                    sb.click('a[data-testid="pagination-page-next"]')  # Navigate to next page
                    sb.sleep(2)  # Wait for next page to load
                else:
                    # No more pages available - exit pagination loop
                    print("No more pages")
                    break

            # Summary statistics for this position/location combination
            print("-"*10)
            print("Extracted job count:", job_count)
            print(f"Number of jobs scraped for '{position}' in {location}:", len(jobs))
            print()

            # Disconnect browser session
            sb.disconnect()
        
    print("="*70)
    print()

# ============================================================================
# DATABASE OPERATIONS: Save scraped jobs to PostgreSQL
# ============================================================================

if all_jobs:
    # Convert list of dictionaries to pandas DataFrame
    df = pd.DataFrame(all_jobs)
    
    # Add timestamp to track when data was scraped
    df['scraped_at'] = datetime.now()
    
    # Remove duplicates within current scrape session
    # Duplicates are identified by: job_title + company_name + company_location
    df = df.drop_duplicates(subset=['job_title', 'company_name', 'company_location'])
    
    print("="*70)
    print(f"Total unique jobs scraped: {len(df)}")
    print("Checking for existing records...")
    
    # Check database for existing jobs to avoid inserting duplicates
    try:
        # Read existing job records from database (only the columns needed for comparison)
        existing_df = pd.read_sql(
            "SELECT job_title, company_name, company_location FROM indeed_jobs",
            engine
        )
        
        # Compare current scrape with existing records
        # Mark each job as 'new' if it doesn't exist in database
        df['is_new'] = ~df.set_index(['job_title', 'company_name', 'company_location']).index.isin(
            existing_df.set_index(['job_title', 'company_name', 'company_location']).index
        )
        
        # Filter to get only new jobs (not in database)
        new_jobs = df[df['is_new']].drop('is_new', axis=1)
        
        print(f"New jobs to insert: {len(new_jobs)}")
        
        # Insert new jobs into database
        if len(new_jobs) > 0:
            new_jobs.to_sql('indeed_jobs', engine, if_exists='append', index=False)
            print("New data successfully saved to PostgreSQL!")
        else:
            print("No new jobs to insert.")
            
    except Exception as e:
        # Handle case where table doesn't exist yet (first run)
        print(f"Table doesn't exist or error occurred: {e}")
        print("Creating table and inserting all data...")
        df.drop('is_new', axis=1, errors='ignore').to_sql('indeed_jobs', engine, if_exists='append', index=False)
    
    print("="*70)
else:
    print("No jobs scraped.")