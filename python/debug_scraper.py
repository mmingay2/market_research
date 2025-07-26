#!/usr/bin/env python3
"""
Debug script to examine HTML structure of patent pages
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

def debug_page_structure(page_num):
    """Debug the HTML structure of a patent page"""
    base_url = "https://ised-isde.canada.ca/ipm-mcpi/patents-brevets"
    params = {
        'search': 'querystring%3D%26advanced%3Dfalse',
        'sort': '%2Blicensing-order',
        'page': str(page_num),
        'lang': 'en'
    }
    
    url = f"{base_url}?{urlencode(params, safe='%')}"
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for any elements that might contain patent data
        print("\n=== Searching for potential patent containers ===")
        
        # Common patterns
        patterns = [
            'div[class*="patent"]',
            'tr[class*="patent"]',
            'li[class*="patent"]',
            'div[class*="item"]',
            'tr[class*="item"]',
            'div[class*="result"]',
            'tr[class*="result"]',
            'div[class*="listing"]',
            'tr[class*="listing"]'
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            if elements:
                print(f"Found {len(elements)} elements matching '{pattern}'")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    print(f"  Element {i+1}: {elem.name} class='{elem.get('class', [])}'")
                    print(f"    Text preview: {elem.get_text()[:100]}...")
        
        # Look for any tables
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables")
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"  Table {i+1}: {len(rows)} rows")
            if rows:
                print(f"    First row classes: {rows[0].get('class', [])}")
        
        # Look for Angular-specific content
        print("\n=== Angular/Dynamic Content Indicators ===")
        ng_elements = soup.find_all(attrs={'ng-repeat': True})
        print(f"Found {len(ng_elements)} ng-repeat elements")
        
        ui_view = soup.find_all(attrs={'ui-view': True})
        print(f"Found {len(ui_view)} ui-view elements")
        
        # Check for any script tags that might load data
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")
        
        # Look for any divs with IDs or classes that might be containers
        print("\n=== Main content containers ===")
        main_content = soup.find('main') or soup.find('div', id='content') or soup.find('div', class_='container')
        if main_content:
            print(f"Main content: {main_content.name} id='{main_content.get('id')}' class='{main_content.get('class')}'")
            print(f"Content preview: {main_content.get_text()[:200]}...")
        
        return soup
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    debug_page_structure(2)