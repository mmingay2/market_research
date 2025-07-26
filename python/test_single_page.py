#!/usr/bin/env python3
"""
Test script to debug patent scraping on a single page
"""

import json
import time
from patent_scraper import PatentScraper, PatentScraperConfig

def test_single_page():
    """Test scraping a single page to debug issues"""
    config = PatentScraperConfig()
    config.start_page = 1
    config.end_page = 1
    config.timeout = 30
    config.rate_limit_delay = 2
    
    scraper = PatentScraper(config)
    
    if not scraper.setup_driver():
        print("Failed to setup driver")
        return
    
    try:
        # Test the wait_for_content_load method
        url = "https://ised-isde.canada.ca/ipm-mcpi/patents-brevets?search=querystring%3D%26advanced%3Dfalse&sort=%2Blicensing-order&page=1&lang=en"
        print(f"Navigating to: {url}")
        scraper.driver.get(url)
        
        # Wait and check content
        print("Waiting for content to load...")
        content_loaded = scraper.wait_for_content_load(1)
        print(f"Content loaded: {content_loaded}")
        
        # Get page source and analyze
        page_source = scraper.driver.page_source
        print(f"Page source length: {len(page_source)}")
        
        # Check for specific content
        if "Searching..." in page_source:
            print("Found 'Searching...' text - page may still be loading")
        
        if "Your search found no results" in page_source:
            print("Found 'Your search found no results' - no patents on this page")
        
        # Try to scrape the page
        patents = scraper.scrape_patent_page(1)
        print(f"Found {len(patents)} patents")
        
        for i, patent in enumerate(patents):
            print(f"Patent {i+1}:")
            print(f"  Title: {patent.title}")
            print(f"  Number: {patent.patent_number}")
            print(f"  Organization: {patent.organization}")
            print(f"  Year: {patent.year}")
            print()
        
        # Save results
        if patents:
            with open('test_output.json', 'w') as f:
                json.dump([p.to_dict() for p in patents], f, indent=2)
            print("Saved test results to test_output.json")
        
    finally:
        scraper.driver.quit()

if __name__ == "__main__":
    test_single_page()