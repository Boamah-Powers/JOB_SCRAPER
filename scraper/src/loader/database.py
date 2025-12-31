"""
Database Loader (Gold Layer)
-----------------------------
Handles loading normalized job data into PostgreSQL database.

The Gold layer represents production-ready data:
- Stored in relational database
- Deduplicated against existing records
- Optimized for queries and analytics
- Tracks data lineage
"""

import pandas as pd
from sqlalchemy import create_engine


class DatabaseLoader:
    """
    Loads job data into PostgreSQL database.
    
    Attributes:
        engine: SQLAlchemy engine for database connections
        table_name: Name of the jobs table
    """
    
    def __init__(self, database_url: str, table_name: str = 'indeed_jobs'):
        """
        Initialize database loader.
        
        Args:
            database_url: PostgreSQL connection string
            table_name: Name of the table to load data into
        """
        self.engine = create_engine(database_url)
        self.table_name = table_name
    
    def load_incremental(self, df: pd.DataFrame) -> int:
        """
        Load only new jobs that don't exist in the database.
        
        Args:
            df: DataFrame with normalized job data
            
        Returns:
            Number of new jobs inserted
        """
        if df.empty:
            print("Gold: No jobs to load")
            return 0
        
        print("="*70)
        print(f"Gold: Loading {len(df)} jobs to database")
        print("Checking for existing records...")
        
        try:
            # Read existing job records from database
            existing_df = pd.read_sql(
                f"SELECT job_title, company_name, company_location FROM {self.table_name}",
                self.engine
            )
            
            # Mark each job as 'new' if it doesn't exist in database
            df['is_new'] = ~df.set_index(
                ['job_title', 'company_name', 'company_location']
            ).index.isin(
                existing_df.set_index(['job_title', 'company_name', 'company_location']).index
            )
            
            # Filter to get only new jobs
            new_jobs = df[df['is_new']].drop('is_new', axis=1)
            
            print(f"New jobs to insert: {len(new_jobs)}")
            
            # Insert new jobs into database
            if len(new_jobs) > 0:
                new_jobs.to_sql(
                    self.table_name, 
                    self.engine, 
                    if_exists='append', 
                    index=False
                )
                print(f"Gold: Successfully inserted {len(new_jobs)} new jobs")
                print("="*70)
                return len(new_jobs)
            else:
                print("No new jobs to insert")
                print("="*70)
                return 0
                
        except Exception as e:
            # Handle case where table doesn't exist yet (first run)
            print(f"Table doesn't exist or error occurred: {e}")
            print("Creating table and inserting all data...")
            
            df.drop('is_new', axis=1, errors='ignore').to_sql(
                self.table_name, 
                self.engine, 
                if_exists='append', 
                index=False
            )
            
            print(f"Gold: Successfully created table and inserted {len(df)} jobs")
            print("="*70)
            return len(df)
    
    def load_replace(self, df: pd.DataFrame) -> int:
        """
        Replace entire table with new data.
        
        Args:
            df: DataFrame with normalized job data
            
        Returns:
            Number of jobs loaded
        """
        if df.empty:
            print("Gold: No jobs to load")
            return 0
        
        df.to_sql(
            self.table_name, 
            self.engine, 
            if_exists='replace', 
            index=False
        )
        
        print(f"Gold: Replaced table with {len(df)} jobs")
        return len(df)
