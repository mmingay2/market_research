#!/usr/bin/env python3
"""
Utility script to list and manage timestamped output files
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import glob

def list_output_files(output_dir="output"):
    """List all output files with their timestamps"""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"Output directory '{output_dir}' does not exist")
        return
    
    print(f"Output files in '{output_dir}':")
    print("=" * 50)
    
    # Find all JSON files
    json_files = list(output_path.glob("*.json"))
    
    if not json_files:
        print("No output files found")
        return
    
    # Group files by type and timestamp
    file_groups = {}
    
    for file in json_files:
        # Extract timestamp from filename
        if "_" in file.stem:
            parts = file.stem.split("_")
            if len(parts) >= 2:
                # Try to parse timestamp
                timestamp_part = "_".join(parts[-2:])  # Last two parts
                try:
                    # Try to parse as timestamp
                    parsed_time = datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")
                    file_type = "_".join(parts[:-2])  # Everything except timestamp
                    if file_type not in file_groups:
                        file_groups[file_type] = []
                    file_groups[file_type].append((file, parsed_time))
                except ValueError:
                    # Not a timestamped file
                    if "untimestamped" not in file_groups:
                        file_groups["untimestamped"] = []
                    file_groups["untimestamped"].append((file, None))
        else:
            # No timestamp
            if "untimestamped" not in file_groups:
                file_groups["untimestamped"] = []
            file_groups["untimestamped"].append((file, None))
    
    # Display files grouped by type
    for file_type, files in file_groups.items():
        if file_type == "untimestamped":
            print(f"\n{file_type.upper()} FILES:")
        else:
            print(f"\n{file_type.upper()} FILES:")
        
        # Sort by timestamp (newest first)
        if files[0][1]:  # Has timestamp
            files.sort(key=lambda x: x[1], reverse=True)
        
        for file, timestamp in files:
            if timestamp:
                print(f"  {file.name} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print(f"  {file.name}")
                
            # Show file size
            size = file.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            print(f"    Size: {size_str}")

def show_latest_summary(output_dir="output"):
    """Show the latest scrape summary"""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"Output directory '{output_dir}' does not exist")
        return
    
    # Find latest summary file
    summary_files = list(output_path.glob("scrape_summary_*.json"))
    
    if not summary_files:
        print("No summary files found")
        return
    
    # Sort by timestamp (newest first)
    summary_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_summary = summary_files[0]
    
    print(f"Latest summary: {latest_summary.name}")
    print("=" * 50)
    
    try:
        with open(latest_summary, 'r') as f:
            summary = json.load(f)
        
        print(f"Total Patents: {summary.get('total_patents', 0)}")
        print(f"Pages Scraped: {len(summary.get('pages_scraped', []))}")
        print(f"Patents with Titles: {summary.get('patents_with_titles', 0)}")
        print(f"Patents with Numbers: {summary.get('patents_with_numbers', 0)}")
        print(f"Unique Organizations: {summary.get('unique_organizations', 0)}")
        print(f"Scrape Date: {summary.get('scrape_date', 'Unknown')}")
        
        if 'raw_file' in summary:
            print(f"Raw File: {summary['raw_file']}")
        if 'cleaned_file' in summary:
            print(f"Cleaned File: {summary['cleaned_file']}")
            
    except Exception as e:
        print(f"Error reading summary: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python list_outputs.py list          # List all output files")
        print("  python list_outputs.py latest        # Show latest summary")
        print("  python list_outputs.py list <dir>    # List files from specific directory")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
        list_output_files(output_dir)
    elif command == "latest":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
        show_latest_summary(output_dir)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, latest")

if __name__ == "__main__":
    main() 