#!/usr/bin/env python3
"""
Patent scraper for Canadian IP Marketplace
This script systematically scrapes patent data from the ised-isde.canada.ca patent database
Uses Selenium for JavaScript-rendered content with improved error handling and logging
"""

import json
import time
import logging
import os
from urllib.parse import urlencode
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PatentData:
    """Data class for patent information"""
    title: str = ""
    patent_number: str = ""
    organization: str = ""
    patent_type: str = ""
    year: str = ""
    date_added: str = ""
    url: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def is_valid(self) -> bool:
        """Check if patent data has minimum required fields"""
        return bool(self.title.strip() or self.patent_number.strip())

class PatentScraperConfig:
    """Configuration class for the patent scraper"""
    
    def __init__(self):
        # Load configuration from config.json
        try:
            with open('config.json', 'r') as f:
                config_data = json.load(f)
            
            scraper_config = config_data.get('scraper', {})
            self.base_url = scraper_config.get('base_url', "https://ised-isde.canada.ca/ipm-mcpi/patents-brevets")
            self.start_page = scraper_config.get('start_page', 1)
            self.end_page = scraper_config.get('end_page', 20)
            self.timeout = scraper_config.get('timeout', 30)
            self.rate_limit_delay = scraper_config.get('rate_limit_delay', 5)
            self.max_retries = scraper_config.get('max_retries', 3)
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load config.json: {e}. Using default values.")
            # Fallback to default values
            self.base_url = "https://ised-isde.canada.ca/ipm-mcpi/patents-brevets"
            self.start_page = 1
            self.end_page = 20
            self.timeout = 30
            self.rate_limit_delay = 5
            self.max_retries = 3
        
        self.output_dir = Path("output")
        self.use_timestamps = True
        self.timestamp_format = "%Y%m%d_%H%M%S"
        self.chrome_options = [
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-features=VizDisplayCompositor',
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

class PatentScraper:
    """Main patent scraper class"""
    
    def __init__(self, config: PatentScraperConfig):
        self.config = config
        self.driver = None
        self.output_dir = config.output_dir
        self.output_dir.mkdir(exist_ok=True)
        
    def setup_driver(self) -> bool:
        """Setup Chrome driver with appropriate options"""
        try:
            chrome_options = Options()
            for option in self.config.chrome_options:
                chrome_options.add_argument(option)
            
            # Add additional preferences to avoid detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            })
            
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set additional headers
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            logger.info("Chrome driver setup successful")
            return True
            
        except WebDriverException as e:
            logger.error(f"Error setting up Chrome driver: {e}")
            logger.error("Please ensure Chrome is installed")
            return False
    
    def wait_for_content_load(self, page_num: int) -> bool:
        """Wait for dynamic content to load and verify it's not placeholder text"""
        wait = WebDriverWait(self.driver, self.config.timeout)
        
        # Wait for any loading indicators to disappear
        try:
            # Wait for "Searching..." text to disappear
            wait.until_not(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Searching..."))
        except TimeoutException:
            logger.warning(f"Page {page_num} may still be loading after timeout")
        
        # Additional wait for dynamic content
        time.sleep(5)
        
        # Check if we have actual content vs placeholder
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        placeholder_indicators = [
            "Searching...",
            "Your search found no results",
            "Please note that ExploreIP does not provide a search of all known patents"
        ]
        
        has_placeholder = any(indicator in page_text for indicator in placeholder_indicators)
        if has_placeholder:
            logger.warning(f"Page {page_num} still contains placeholder text")
            return False
        
        return True
    
    def extract_patent_from_element(self, item) -> Optional[PatentData]:
        """Extract patent data from a single HTML element"""
        patent = PatentData()
        
        # Get all text content
        text_content = item.get_text().strip()
        
        # Skip if this looks like navigation or header content
        skip_indicators = [
            "Searching...", "Keyword search", "Save your search", 
            "Collaboration Opportunities", "Licensing Opportunity",
            "Your search found no results", "Please note that ExploreIP"
        ]
        
        if any(indicator in text_content for indicator in skip_indicators):
            return None
        
        # Extract title from result-title class
        title_elem = item.select_one('.result-title')
        if title_elem:
            title_text = title_elem.get_text().strip()
            if title_text and not any(skip in title_text for skip in skip_indicators):
                patent.title = self.clean_patent_title(title_text)
        
        # Extract patent number from publication-number class
        patent_number_elem = item.select_one('.publication-number')
        if patent_number_elem:
            patent.patent_number = patent_number_elem.get_text().strip()
        
        # Extract organization from organisation class
        org_elem = item.select_one('.organisation a')
        if org_elem:
            patent.organization = org_elem.get_text().strip()
        
        # Extract patent type from ip-type class
        type_elem = item.select_one('.ip-type span')
        if type_elem:
            patent.patent_type = type_elem.get_text().strip()
        
        # Extract year from filed class
        year_elem = item.select_one('.filed')
        if year_elem:
            patent.year = year_elem.get_text().strip()
        
        # Extract date added from date-added class
        date_elem = item.select_one('.date-added')
        if date_elem:
            patent.date_added = date_elem.get_text().strip()
        
        # Extract description from invention-description class
        desc_elem = item.select_one('.invention-description')
        if desc_elem:
            patent.description = desc_elem.get_text().strip()
        
        # Extract URL from the title link
        title_link = item.select_one('.desktop-display')
        if title_link and title_link.get('href'):
            patent.url = "https://ised-isde.canada.ca" + title_link.get('href')
        
        # If we didn't find structured data, try to parse from text content
        if not patent.title and text_content:
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            if lines:
                # Skip lines that are clearly not patent titles
                for line in lines:
                    if not any(skip in line for skip in skip_indicators) and len(line) > 10:
                        patent.title = self.clean_patent_title(line)
                        break
        
        return patent if patent.is_valid() else None
    
    def clean_patent_title(self, title: str) -> str:
        """Clean duplicate text from patent titles"""
        if not title:
            return ""
        
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title.strip())
        
        # Remove duplicate text (common issue where title appears twice)
        words = title.split()
        if len(words) > 10:
            midpoint = len(words) // 2
            first_half = " ".join(words[:midpoint])
            second_half = " ".join(words[midpoint:])
            
            # If first half equals second half, use only first half
            if first_half.strip() == second_half.strip():
                title = first_half.strip()
        
        return title
    
    def scrape_patent_page(self, page_num: int) -> List[PatentData]:
        """Scrape a single page of patents using Selenium"""
        params = {
            'search': 'querystring%3D%26advanced%3Dfalse',
            'sort': '%2Blicensing-order',
            'page': str(page_num),
            'lang': 'en'
        }
        
        url = f"{self.config.base_url}?{urlencode(params, safe='%')}"
        
        try:
            logger.info(f"Scraping page {page_num}...")
            self.driver.get(url)
            
            # Wait for content to load and verify it's not placeholder
            if not self.wait_for_content_load(page_num):
                logger.warning(f"Page {page_num} may not have loaded properly")
                return []
            
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            patents = []
            
            # Look for patent table rows - the patents are in table rows with specific structure
            patent_rows = soup.find_all('tr', class_=lambda x: x and 'ng-scope' in x)
            
            if patent_rows:
                logger.info(f"Found {len(patent_rows)} potential patent rows")
                for row in patent_rows:
                    # Check if this row contains patent data by looking for result-title
                    if row.select_one('.result-title'):
                        patent = self.extract_patent_from_element(row)
                        if patent:
                            patents.append(patent)
            
            # Fallback: try to extract from any div with substantial text
            if not patents:
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text().strip()
                    if len(text) > 50 and not any(skip in text for skip in ["Searching...", "Keyword search"]):
                        patent = self.extract_patent_from_element(div)
                        if patent:
                            patents.append(patent)
            
            logger.info(f"Found {len(patents)} patents on page {page_num}")
            return patents
            
        except TimeoutException:
            logger.error(f"Timeout waiting for content to load on page {page_num}")
            return []
        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {e}")
            return []
    
    def save_patents_to_file(self, patents: List[PatentData], filename: str):
        """Save patent data to JSON file"""
        filepath = self.output_dir / filename
        
        # Convert PatentData objects to dictionaries
        patents_dict = [patent.to_dict() for patent in patents]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(patents_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(patents)} patents to {filepath}")
    
    def scrape_all_pages(self) -> List[PatentData]:
        """Scrape all configured pages"""
        if not self.setup_driver():
            logger.error("Failed to setup Chrome driver. Exiting.")
            return []
        
        all_patents = []
        
        try:
            for page in range(self.config.start_page, self.config.end_page + 1):
                retries = 0
                while retries < self.config.max_retries:
                    try:
                        patents = self.scrape_patent_page(page)
                        all_patents.extend(patents)
                        break
                    except Exception as e:
                        retries += 1
                        logger.warning(f"Retry {retries}/{self.config.max_retries} for page {page}: {e}")
                        if retries >= self.config.max_retries:
                            logger.error(f"Failed to scrape page {page} after {self.config.max_retries} retries")
                        time.sleep(self.config.rate_limit_delay * 2)
                
                # Be respectful with rate limiting
                time.sleep(self.config.rate_limit_delay)
            
            logger.info(f"Total patents scraped: {len(all_patents)}")
            return all_patents
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Chrome driver closed")

def main():
    """Main function to run the patent scraper"""
    config = PatentScraperConfig()
    scraper = PatentScraper(config)
    
    # Generate timestamp for unique filenames if enabled
    timestamp = datetime.now().strftime(config.timestamp_format) if config.use_timestamps else ""
    
    # Scrape all pages
    all_patents = scraper.scrape_all_pages()
    
    if all_patents:
        # Generate filenames with or without timestamp
        if config.use_timestamps:
            raw_filename = f'raw_patents_{timestamp}.json'
            cleaned_filename = f'cleaned_patents_{timestamp}.json'
            summary_filename = f'scrape_summary_{timestamp}.json'
        else:
            raw_filename = 'raw_patents.json'
            cleaned_filename = 'cleaned_patents.json'
            summary_filename = 'scrape_summary.json'
        
        # Save raw data
        scraper.save_patents_to_file(all_patents, raw_filename)
        
        # Save cleaned data
        scraper.save_patents_to_file(all_patents, cleaned_filename)
        
        # Save summary
        summary = {
            'total_patents': len(all_patents),
            'scrape_date': datetime.now().isoformat(),
            'pages_scraped': list(range(config.start_page, config.end_page + 1)),
            'patents_with_titles': len([p for p in all_patents if p.title]),
            'patents_with_numbers': len([p for p in all_patents if p.patent_number]),
            'unique_organizations': len(set(p.organization for p in all_patents if p.organization)),
            'raw_file': raw_filename,
            'cleaned_file': cleaned_filename,
            'summary_file': summary_filename,
            'timestamp': timestamp if config.use_timestamps else None
        }
        
        with open(scraper.output_dir / summary_filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Scraping completed. Summary: {summary}")
        logger.info(f"Files saved: {raw_filename}, {cleaned_filename}, {summary_filename}")
    else:
        logger.error("No patents were scraped")

if __name__ == "__main__":
    main()