#!/usr/bin/env python3
"""
Demo script for the improved patent scraper
"""

import json
import sys
from pathlib import Path
from patent_scraper import PatentScraper, PatentScraperConfig

def demo_single_page_scrape():
    """Demo scraping a single page"""
    print("=" * 50)
    print("DEMO: Single Page Scraping")
    print("=" * 50)
    
    # Create configuration for single page
    config = PatentScraperConfig()
    config.start_page = 1
    config.end_page = 1
    config.output_dir = Path("demo_output")
    
    # Create scraper
    scraper = PatentScraper(config)
    
    # Scrape single page
    patents = scraper.scrape_all_pages()
    
    if patents:
        print(f"\nFound {len(patents)} patents on page 1")
        for i, patent in enumerate(patents[:3], 1):  # Show first 3
            print(f"\nPatent {i}:")
            print(f"  Title: {patent.title}")
            print(f"  Number: {patent.patent_number}")
            print(f"  Organization: {patent.organization}")
            print(f"  Year: {patent.year}")
        
        # Save demo results
        scraper.save_patents_to_file(patents, 'demo_patents.json')
        print(f"\nDemo results saved to demo_output/demo_patents.json")
    else:
        print("No patents found on page 1")

def demo_configuration():
    """Demo configuration options"""
    print("\n" + "=" * 50)
    print("DEMO: Configuration Options")
    print("=" * 50)
    
    config = PatentScraperConfig()
    
    print(f"Base URL: {config.base_url}")
    print(f"Page Range: {config.start_page} - {config.end_page}")
    print(f"Timeout: {config.timeout} seconds")
    print(f"Rate Limit Delay: {config.rate_limit_delay} seconds")
    print(f"Max Retries: {config.max_retries}")
    print(f"Output Directory: {config.output_dir}")
    print(f"Chrome Options: {len(config.chrome_options)} options")

def demo_data_structures():
    """Demo data structures"""
    print("\n" + "=" * 50)
    print("DEMO: Data Structures")
    print("=" * 50)
    
    from patent_scraper import PatentData
    
    # Create sample patent
    sample_patent = PatentData(
        title="Sample Patent Title",
        patent_number="CA2123456",
        organization="Sample Company Inc.",
        patent_type="Utility Patent",
        year="2023",
        date_added="2023-01-01",
        url="https://example.com/patent",
        description="Sample patent description"
    )
    
    print("Sample Patent Data:")
    print(json.dumps(sample_patent.to_dict(), indent=2))
    
    print(f"\nIs Valid: {sample_patent.is_valid()}")
    
    # Test invalid patent
    invalid_patent = PatentData()
    print(f"Invalid Patent Is Valid: {invalid_patent.is_valid()}")

def main():
    """Main demo function"""
    print("Patent Scraper Demo")
    print("This demo shows the improved patent scraper functionality")
    
    try:
        demo_configuration()
        demo_data_structures()
        
        # Ask user if they want to run single page demo
        response = input("\nWould you like to run a single page scraping demo? (y/n): ")
        if response.lower() in ['y', 'yes']:
            demo_single_page_scrape()
        else:
            print("Skipping scraping demo")
        
        print("\nDemo completed!")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo error: {e}")

if __name__ == "__main__":
    main() 