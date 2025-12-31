"""
Indeed Job Scraper
------------------
Extracts job listings from Indeed across multiple locations and positions.

This module handles:
- Browser automation with bot detection bypass
- Pagination through search results
- Extraction of job details from listing pages
- Filtering of valid job URLs
- Graceful error handling for failed scrapes
"""

import logging
from re import search
from seleniumbase import SB
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndeedScraper:
    """
    Scraper for Indeed job postings.
    
    Attributes:
        locations: Dictionary mapping domain codes to location names
        positions: List of job positions to search for
        headless: Whether to run browser in headless mode
    """
    
    def __init__(
        self, 
        locations: Dict[str, str], 
        positions: List[str],
        headless: bool = True
    ):
        """
        Initialize the Indeed scraper.
        
        Args:
            locations: Dict of domain codes to location names (e.g., {"uk": "United Kingdom"})
            positions: List of job positions to search for
            headless: Whether to run browser without GUI
        """
        self.locations = locations
        self.positions = positions
        self.headless = headless
    
    def scrape_position(
        self, 
        domain: str, 
        location: str, 
        position: str
    ) -> List[Dict]:
        """
        Scrape jobs for a specific position and location.
        
        Args:
            domain: Indeed domain code (uk, ae, sg)
            location: Full location name
            position: Job position to search for
            
        Returns:
            List of raw job dictionaries (empty list if scrape fails)
        """
        jobs = []
        
        try:
            # Initialize SeleniumBase with undetected mode to bypass bot detection
            # uc=True: Enables undetected-chromedriver mode
            # headless: Runs browser without GUI (faster, good for automation)
            # test=True: Enables test mode features
            # locale="en": Sets browser locale to English
            with SB(uc=True, headless=self.headless, test=False, locale="en") as sb:
                # Build Indeed URL with search parameters
                # fromage=3: Jobs posted within last 3 days
                url = "https://{}.indeed.com/jobs?q={}&l={}&fromage=3".format(
                    domain, 
                    position.replace(" ", "+"), 
                    location.replace(" ", "+")
                )
                
                # Activate CDP (Chrome DevTools Protocol) mode for better control
                sb.activate_cdp_mode(url)
                sb.sleep(2)  # Wait for page to load
                
                # Solve any CAPTCHA that might appear
                sb.solve_captcha()
                sb.sleep(2)  # Wait after CAPTCHA resolution

                # Pagination loop: Continue scraping until no more pages
                page_count = 0
                max_pages = 10  # Safety limit to prevent infinite loops
                
                while page_count < max_pages:
                    page_count += 1
                    
                    try:
                        # Extract all job elements from current page using CSS selectors
                        job_titles = sb.find_elements(".jobTitle")
                        company_names = sb.find_elements(".css-19eicqx")
                        company_locations = sb.find_elements(".css-1f06pz4")
                        urls = sb.find_elements("h2.jobTitle > a")
                        
                        # Check if we found any jobs
                        if not job_titles:
                            logger.warning(f"No job listings found on page {page_count} for '{position}' in {location}")
                            break

                        # Iterate through each job listing on the current page
                        # zip() combines all 4 lists element-by-element
                        for job_data in zip(job_titles, company_names, company_locations, urls):
                            try:
                                # Extract text content from each element
                                job_title = job_data[0].text
                                company_name = job_data[1].text
                                company_location = job_data[2].text
                                job_url = "https://{}.indeed.com".format(domain) + job_data[3].get_attribute("href")

                                # Filter: Only keep URLs with '/rc/clk?jk=' pattern (valid job links)
                                # This excludes sponsored posts and other non-standard listings
                                if search(r'/rc/clk\?jk=', job_url):
                                    # Create raw job record
                                    job_record = {
                                        'job_title': job_title,
                                        'company_name': company_name,
                                        'company_location': company_location,
                                        'job_url': job_url,
                                        'search_position': position,
                                        'search_location': location,
                                        'domain': domain
                                    }
                                    jobs.append(job_record)
                            except Exception as e:
                                logger.warning(f"Failed to extract job data: {e}")
                                continue

                        # Pagination: Check if "Next" button exists on current page
                        if sb.is_element_present('a[data-testid="pagination-page-next"]'):
                            logger.info(f"  Scraping page {page_count + 1}...")
                            sb.click('a[data-testid="pagination-page-next"]')
                            sb.sleep(2)  # Wait for next page to load
                        else:
                            # No more pages available - exit pagination loop
                            break
                            
                    except Exception as e:
                        logger.error(f"Error scraping page {page_count} for '{position}' in {location}: {e}")
                        break

                # Disconnect browser session
                sb.disconnect()
            
            logger.info(f"  Scraped {len(jobs)} jobs for '{position}' in {location}")
            
        except Exception as e:
            logger.error(f"Failed to scrape '{position}' in {location} ({domain}): {e}")
            logger.info(f"  Returning {len(jobs)} jobs scraped before error")
        
        return jobs
    
    def scrape_all(self) -> List[Dict]:
        """
        Scrape all configured locations and positions.
        
        Returns:
            List of all raw job dictionaries
        """
        all_jobs = []
        total_attempts = len(self.locations) * len(self.positions)
        successful_scrapes = 0
        failed_scrapes = 0
        
        # Iterate through each location
        for domain, location in self.locations.items():
            print("="*70)
            print(f"Scraping jobs in: {location} ({domain})")
            print("="*70)
            
            # For each location, search for all configured job positions
            for position in self.positions:
                print("-"*50)
                print(f"Position: {position}")
                print("-"*50)
                
                try:
                    jobs = self.scrape_position(domain, location, position)
                    
                    if jobs:
                        all_jobs.extend(jobs)
                        successful_scrapes += 1
                    else:
                        logger.warning(f"No jobs found for '{position}' in {location}")
                        failed_scrapes += 1
                        
                except Exception as e:
                    logger.error(f"Unexpected error scraping '{position}' in {location}: {e}")
                    failed_scrapes += 1
                
                print()
            
            print("="*70)
            print()
        
        # Print summary
        print("="*70)
        print("SCRAPING SUMMARY")
        print("="*70)
        print(f"Total attempts:      {total_attempts}")
        print(f"Successful scrapes:  {successful_scrapes}")
        print(f"Failed scrapes:      {failed_scrapes}")
        print(f"Total jobs scraped:  {len(all_jobs)}")
        print("="*70)
        print()
        
        return all_jobs
