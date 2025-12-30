"""
Bronze Storage Layer
--------------------
Handles storage of raw, immutable job data in JSON format using Cloudinary.

The Bronze layer is the landing zone for all scraped data and follows these principles:
- Data is stored as-is, with no transformations
- Files are partitioned by source and date
- Data is never modified after write (immutable)
- Supports data lineage tracking
- Stored in cloud for Airflow compatibility
"""

import json
import os
import tempfile
import requests
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv


class BronzeStorage:
    """
    Manages raw job data storage in the Bronze layer using Cloudinary.
    
    Attributes:
        upload_preset: Cloudinary upload preset for unsigned uploads
    """
    
    def __init__(self, upload_preset: str = "job_scraper_indeed"):
        """
        Initialize Bronze storage with Cloudinary.
        
        Args:
            upload_preset: Cloudinary upload preset name
        """
        # Load environment variables
        load_dotenv()
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
        
        self.upload_preset = upload_preset
    
    def save_raw_jobs(
        self, 
        jobs: List[Dict], 
        source: str, 
        run_date: datetime = None
    ) -> str:
        """
        Save raw job data to Bronze storage in Cloudinary.
        
        Args:
            jobs: List of raw job dictionaries
            source: Data source name (e.g., 'indeed')
            run_date: Date of the scraping run (defaults to now)
            
        Returns:
            Cloudinary public_id of the saved file
        """
        if run_date is None:
            run_date = datetime.now()
        
        # Prepare data structure
        data = {
            'metadata': {
                'source': source,
                'scraped_at': run_date.isoformat(),
                'job_count': len(jobs)
            },
            'jobs': jobs
        }
        
        # Create temporary file to upload
        # Create a file with a specific name
        filename = f"{source}_{run_date.strftime('%Y%m%d_%H%M%S')}.json"
        tmp_path = os.path.join(tempfile.gettempdir(), filename)

        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        try:
            # Upload to Cloudinary
            response = cloudinary.uploader.unsigned_upload(
                tmp_path,
                upload_preset=self.upload_preset,
                resource_type="raw"
            )
            
            print(f"Bronze: Saved {len(jobs)} raw jobs to Cloudinary")
            print(f"  Public ID: {response['public_id']}")
            print(f"  URL: {response['secure_url']}")
            
            return response['public_id']
            
        except cloudinary.exceptions.Error as e:
            print(f"Error uploading to Cloudinary: {e}")
            raise
        finally:
            # Clean up temporary file
            os.remove(tmp_path)
    
    def load_raw_jobs(self, public_id: str) -> List[Dict]:
        """
        Load raw job data from Bronze storage in Cloudinary.
        
        Args:
            public_id: Cloudinary public_id of the bronze file
            
        Returns:
            List of raw job dictionaries
        """
        try:
            # Get resource details from Cloudinary
            resource = cloudinary.api.resource(public_id, resource_type="raw")
            secure_url = resource['secure_url']
            
            # Download the JSON file
            response = requests.get(secure_url)
            response.raise_for_status()
            
            data = response.json()
            return data.get('jobs', [])
            
        except Exception as e:
            print(f"Error loading from Cloudinary: {e}")
            raise
    
    def list_files(self, source: str = None) -> List[Dict]:
        """
        List all bronze files in Cloudinary.
        
        Args:
            source: Optional source name to filter by (not used, kept for compatibility)
            
        Returns:
            List of dictionaries with file information (public_id, url, created_at)
        """
        try:
            # List all raw resources from Cloudinary
            result = cloudinary.api.resources(
                type="upload",
                resource_type="raw",
                max_results=500
            )
            
            files = []
            for resource in result.get('resources', []):
                files.append({
                    'public_id': resource['public_id'],
                    'url': resource['secure_url'],
                    'created_at': resource['created_at'],
                    'bytes': resource['bytes']
                })
            
            return files
            
        except Exception as e:
            print(f"Error listing files from Cloudinary: {e}")
            return []
