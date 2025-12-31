"""
Data Normalization (Silver Layer)
----------------------------------
Transforms raw job data into the canonical schema and applies data quality rules.

The Silver layer represents cleaned, normalized data:
- Conforms to canonical schema
- Deduplicated
- Validated
- Enriched with metadata
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict
from ..schema import JobSchema


class JobNormalizer:
    """
    Normalizes raw job data into the canonical schema.
    """
    
    @staticmethod
    def normalize_jobs(raw_jobs: List[Dict]) -> pd.DataFrame:
        """
        Normalize raw job data to canonical schema.
        
        Args:
            raw_jobs: List of raw job dictionaries
            
        Returns:
            DataFrame with normalized, validated job data
        """
        if not raw_jobs:
            return pd.DataFrame(columns=JobSchema.ALL_FIELDS)
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_jobs)
        
        # Add scraped_at timestamp if not present
        if 'scraped_at' not in df.columns:
            df['scraped_at'] = datetime.now()
        
        # Ensure all canonical fields exist
        for field in JobSchema.ALL_FIELDS:
            if field not in df.columns:
                df[field] = None
        
        # Select only canonical schema fields
        df = df[JobSchema.ALL_FIELDS]
        
        # Data quality: Remove rows with missing required fields
        for field in JobSchema.REQUIRED_FIELDS:
            df = df[df[field].notna() & (df[field] != '')]
        
        print(f"Silver: Normalized {len(df)} jobs")
        return df
    
    @staticmethod
    def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate job postings.
        
        Duplicates are identified by: job_title + company_name + company_location
        
        Args:
            df: DataFrame with job data
            
        Returns:
            DataFrame with duplicates removed
        """
        initial_count = len(df)
        
        # Remove duplicates based on job identity
        df = df.drop_duplicates(
            subset=['job_title', 'company_name', 'company_location'],
            keep='first'
        )
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"Silver: Removed {removed_count} duplicate jobs")
        
        return df
    
    @staticmethod
    def transform(raw_jobs: List[Dict]) -> pd.DataFrame:
        """
        Full transformation pipeline: normalize and deduplicate.
        
        Args:
            raw_jobs: List of raw job dictionaries
            
        Returns:
            Clean, deduplicated DataFrame
        """
        df = JobNormalizer.normalize_jobs(raw_jobs)
        df = JobNormalizer.deduplicate(df)
        
        print(f"Silver: Final dataset contains {len(df)} unique jobs")
        return df
