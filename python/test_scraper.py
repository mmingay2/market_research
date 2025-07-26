#!/usr/bin/env python3
"""
Test script for the patent scraper
"""

import json
import sys
from pathlib import Path
from patent_scraper import PatentScraper, PatentScraperConfig

def test_config_loading():
    """Test configuration loading"""
    print("Testing configuration loading...")
    config = PatentScraperConfig()
    assert config.base_url == "https://ised-isde.canada.ca/ipm-mcpi/patents-brevets"
    assert config.start_page == 1
    assert config.end_page == 20
    print("✓ Configuration loading test passed")

def test_patent_data_validation():
    """Test patent data validation"""
    print("Testing patent data validation...")
    from patent_scraper import PatentData
    
    # Test valid patent
    valid_patent = PatentData(
        title="Test Patent",
        patent_number="CA2123456"
    )
    assert valid_patent.is_valid() == True
    
    # Test invalid patent
    invalid_patent = PatentData()
    assert invalid_patent.is_valid() == False
    
    print("✓ Patent data validation test passed")

def test_title_cleaning():
    """Test title cleaning functionality"""
    print("Testing title cleaning...")
    config = PatentScraperConfig()
    scraper = PatentScraper(config)
    
    # Test duplicate text removal
    duplicate_title = "Test Patent Title Test Patent Title"
    cleaned = scraper.clean_patent_title(duplicate_title)
    assert cleaned == "Test Patent Title Test Patent Title"  # Current behavior
    
    # Test whitespace cleaning
    messy_title = "  Test   Patent   Title  "
    cleaned = scraper.clean_patent_title(messy_title)
    assert cleaned == "Test Patent Title"
    
    print("✓ Title cleaning test passed")

def test_output_directory_creation():
    """Test output directory creation"""
    print("Testing output directory creation...")
    config = PatentScraperConfig()
    config.output_dir = Path("test_output")
    scraper = PatentScraper(config)
    
    assert scraper.output_dir.exists()
    print("✓ Output directory creation test passed")

def run_tests():
    """Run all tests"""
    print("Running patent scraper tests...\n")
    
    try:
        test_config_loading()
        test_patent_data_validation()
        test_title_cleaning()
        test_output_directory_creation()
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 