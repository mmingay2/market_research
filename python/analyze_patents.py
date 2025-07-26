#!/usr/bin/env python3
"""
Patent data analysis utility
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

def load_patents(filepath: str) -> list:
    """Load patent data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filepath}")
        return []

def analyze_patents(patents: list) -> dict:
    """Analyze patent data and return statistics"""
    if not patents:
        return {}
    
    analysis = {
        'total_patents': len(patents),
        'patents_with_titles': len([p for p in patents if p.get('title', '').strip()]),
        'patents_with_numbers': len([p for p in patents if p.get('patent_number', '').strip()]),
        'patents_with_organizations': len([p for p in patents if p.get('organization', '').strip()]),
        'patents_with_years': len([p for p in patents if p.get('year', '').strip()]),
        'unique_organizations': len(set(p.get('organization', '') for p in patents if p.get('organization', '').strip())),
        'year_distribution': Counter(p.get('year', '') for p in patents if p.get('year', '').strip()),
        'organization_distribution': Counter(p.get('organization', '') for p in patents if p.get('organization', '').strip()),
        'patent_type_distribution': Counter(p.get('patent_type', '') for p in patents if p.get('patent_type', '').strip())
    }
    
    return analysis

def print_analysis(analysis: dict):
    """Print analysis results"""
    if not analysis:
        print("No data to analyze")
        return
    
    print("=" * 50)
    print("PATENT DATA ANALYSIS")
    print("=" * 50)
    
    print(f"\nTotal Patents: {analysis['total_patents']}")
    print(f"Patents with Titles: {analysis['patents_with_titles']}")
    print(f"Patents with Numbers: {analysis['patents_with_numbers']}")
    print(f"Patents with Organizations: {analysis['patents_with_organizations']}")
    print(f"Patents with Years: {analysis['patents_with_years']}")
    print(f"Unique Organizations: {analysis['unique_organizations']}")
    
    # Year distribution
    if analysis['year_distribution']:
        print(f"\nYear Distribution:")
        for year, count in sorted(analysis['year_distribution'].items()):
            print(f"  {year}: {count}")
    
    # Top organizations
    if analysis['organization_distribution']:
        print(f"\nTop Organizations:")
        for org, count in analysis['organization_distribution'].most_common(10):
            print(f"  {org}: {count}")
    
    # Patent types
    if analysis['patent_type_distribution']:
        print(f"\nPatent Types:")
        for ptype, count in analysis['patent_type_distribution'].items():
            print(f"  {ptype}: {count}")

def export_to_csv(patents: list, output_file: str):
    """Export patent data to CSV"""
    if not patents:
        print("No data to export")
        return
    
    df = pd.DataFrame(patents)
    df.to_csv(output_file, index=False)
    print(f"Data exported to {output_file}")

def main():
    """Main analysis function"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_patents.py <patent_file.json>")
        print("Example: python analyze_patents.py output/cleaned_patents.json")
        sys.exit(1)
    
    filepath = sys.argv[1]
    patents = load_patents(filepath)
    
    if not patents:
        print("No patent data found. Please run the scraper first.")
        sys.exit(1)
    
    # Analyze the data
    analysis = analyze_patents(patents)
    print_analysis(analysis)
    
    # Export to CSV if requested
    if len(sys.argv) > 2 and sys.argv[2] == '--export':
        output_file = filepath.replace('.json', '.csv')
        export_to_csv(patents, output_file)

if __name__ == "__main__":
    main() 