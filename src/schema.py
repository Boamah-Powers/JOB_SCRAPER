"""
Canonical Job Schema
--------------------
Defines the standard schema for all job postings in the system.

This schema ensures consistency across different job sources and serves
as the foundation for the data warehouse.
"""

from typing import Optional
from datetime import datetime


class JobSchema:
    """
    Canonical job posting schema.
    
    Fields:
        job_title: Position title
        company_name: Company/organization name
        company_location: Geographic location of the job
        job_url: URL to the job posting
        search_position: The search term used to find this job
        search_location: The location searched for this job
        domain: The Indeed domain (uk, ae, sg)
        scraped_at: Timestamp when the job was scraped
    """
    
    REQUIRED_FIELDS = [
        'job_title',
        'company_name',
        'company_location',
        'job_url'
    ]
    
    OPTIONAL_FIELDS = [
        'search_position',
        'search_location',
        'domain',
        'scraped_at'
    ]
    
    ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS
    
    @staticmethod
    def validate(job_record: dict) -> bool:
        """
        Validate that a job record contains all required fields.
        
        Args:
            job_record: Dictionary containing job data
            
        Returns:
            True if valid, False otherwise
        """
        return all(field in job_record for field in JobSchema.REQUIRED_FIELDS)
    
    @staticmethod
    def create_record(
        job_title: str,
        company_name: str,
        company_location: str,
        job_url: str,
        search_position: Optional[str] = None,
        search_location: Optional[str] = None,
        domain: Optional[str] = None,
        scraped_at: Optional[datetime] = None
    ) -> dict:
        """
        Create a job record following the canonical schema.
        
        Args:
            job_title: Position title
            company_name: Company name
            company_location: Job location
            job_url: URL to job posting
            search_position: Search term used
            search_location: Location searched
            domain: Indeed domain
            scraped_at: Timestamp of scrape
            
        Returns:
            Dictionary conforming to JobSchema
        """
        return {
            'job_title': job_title,
            'company_name': company_name,
            'company_location': company_location,
            'job_url': job_url,
            'search_position': search_position,
            'search_location': search_location,
            'domain': domain,
            'scraped_at': scraped_at or datetime.now()
        }
