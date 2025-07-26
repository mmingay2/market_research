#!/usr/bin/env python3
"""
Debug script to examine the page structure and find correct selectors
"""

import json
import time
from patent_scraper import PatentScraper, PatentScraperConfig
from bs4 import BeautifulSoup

def debug_page_structure():
    """Debug the page structure to find correct selectors"""
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
        url = "https://ised-isde.canada.ca/ipm-mcpi/patents-brevets?search=querystring%3D%26advanced%3Dfalse&sort=%2Blicensing-order&page=1&lang=en"
        print(f"Navigating to: {url}")
        scraper.driver.get(url)
        
        # Wait for content to load
        content_loaded = scraper.wait_for_content_load(1)
        print(f"Content loaded: {content_loaded}")
        
        # Get page source and analyze
        soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')
        
        # Look for patent elements with more detail
        patent_elements = soup.find_all('div', class_=lambda x: x and 'patent' in x)
        print(f"Found {len(patent_elements)} patent elements")
        
        if patent_elements:
            # Examine the first patent element in detail
            first_patent = patent_elements[0]
            print("\n=== First Patent Element Structure ===")
            print(f"Classes: {first_patent.get('class')}")
            print(f"ID: {first_patent.get('id')}")
            
            # Look for all text content
            all_text = first_patent.get_text(separator='\n', strip=True)
            print(f"\nAll text content:\n{all_text}")
            
            # Look for specific elements that might contain patent numbers
            patent_number_elements = first_patent.find_all(['span', 'div', 'p'], string=lambda text: text and any(char.isdigit() for char in text))
            print(f"\nElements with numbers: {len(patent_number_elements)}")
            for elem in patent_number_elements[:5]:  # Show first 5
                print(f"  - {elem.name}: {elem.get_text().strip()}")
            
            # Look for organization elements
            org_keywords = ['organization', 'inventor', 'assignee', 'owner', 'company', 'applicant']
            org_elements = []
            for keyword in org_keywords:
                elements = first_patent.find_all(['span', 'div', 'p'], class_=lambda x: x and keyword in x.lower())
                org_elements.extend(elements)
            
            print(f"\nOrganization-related elements: {len(org_elements)}")
            for elem in org_elements[:5]:
                print(f"  - {elem.name} ({elem.get('class')}): {elem.get_text().strip()}")
            
            # Look for date elements
            date_elements = first_patent.find_all(['span', 'div', 'p'], string=lambda text: text and any(year in text for year in ['2024', '2025', '2023']))
            print(f"\nDate-related elements: {len(date_elements)}")
            for elem in date_elements[:5]:
                print(f"  - {elem.name}: {elem.get_text().strip()}")
            
            # Look for links that might contain patent numbers
            links = first_patent.find_all('a', href=True)
            print(f"\nLinks: {len(links)}")
            for link in links[:5]:
                print(f"  - {link.get('href')}: {link.get_text().strip()}")
            
            # Look for any elements with specific patterns
            all_elements = first_patent.find_all(['span', 'div', 'p', 'strong', 'b'])
            print(f"\nAll text elements: {len(all_elements)}")
            for elem in all_elements[:10]:
                text = elem.get_text().strip()
                if text and len(text) > 5:
                    print(f"  - {elem.name} ({elem.get('class')}): {text[:100]}...")
        
        # Save the page source for manual inspection
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(scraper.driver.page_source)
        print("\nSaved page source to debug_page_source.html")
        
    finally:
        scraper.driver.quit()

if __name__ == "__main__":
    debug_page_structure() 