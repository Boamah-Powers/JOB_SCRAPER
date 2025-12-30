"""
Indeed Job Scraper
------------------
Extracts job listings from Indeed across multiple locations and positions.

This module handles:
- Browser automation with bot detection bypass
- Pagination through search results
- Extraction of job details from listing pages
- Filtering of valid job URLs
"""

from re import search
from seleniumbase import SB
from typing import List, Dict


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
            List of raw job dictionaries
        """
        jobs = []
        
        # Initialize SeleniumBase with undetected mode to bypass bot detection
        # uc=True: Enables undetected-chromedriver mode
        # headless: Runs browser without GUI (faster, good for automation)
        # test=True: Enables test mode features
        # locale="en": Sets browser locale to English
        with SB(uc=True, headless=self.headless, test=True, locale="en") as sb:
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

                # Pagination: Check if "Next" button exists on current page
                if sb.is_element_present('a[data-testid="pagination-page-next"]'):
                    print(f"  Scraping next page...")
                    sb.click('a[data-testid="pagination-page-next"]')
                    sb.sleep(2)  # Wait for next page to load
                else:
                    # No more pages available - exit pagination loop
                    break

            # Disconnect browser session
            sb.disconnect()
        
        print(f"  Scraped {len(jobs)} jobs for '{position}' in {location}")
        return jobs
    
    def scrape_all(self) -> List[Dict]:
        """
        Scrape all configured locations and positions.
        
        Returns:
            List of all raw job dictionaries
        """
        all_jobs = []
        
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
                
                jobs = self.scrape_position(domain, location, position)
                all_jobs.extend(jobs)
                print()
            
            print("="*70)
            print()
        
        return all_jobs
