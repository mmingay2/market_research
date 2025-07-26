import pandas as pd
import json
import glob
from datetime import datetime
import sys

def combine_json_files(json_files=None):
    """
    Combine multiple JSON files into a single DataFrame and save with timestamp.
    
    Args:
        json_files: List of JSON file paths. If None, will use all .json files in current directory.
    """
    # If no files specified, get all JSON files in current directory
    if json_files is None:
        json_files = glob.glob("*.json")
    
    if not json_files:
        print("No JSON files found!")
        return
    
    print(f"Processing {len(json_files)} JSON files...")
    
    # Load and combine all JSON files
    all_data = []
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                all_data.extend(data)
                print(f"Loaded {len(data)} records from {file_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if not all_data:
        print("No data found in JSON files!")
        return
    
    # Create DataFrame and remove duplicates
    df = pd.json_normalize(all_data).drop_duplicates()
    print(f"Combined DataFrame has {len(df)} unique records")
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"combined_patents_{timestamp}.txt"
    
    # Save to file
    df.to_csv(output_filename, sep="\t", index=False, header=False)
    print(f"Saved combined data to: {output_filename}")
    
    return df

if __name__ == "__main__":
    # If command line arguments provided, use them as file paths
    if len(sys.argv) > 1:
        json_files = sys.argv[1:]
        combine_json_files(json_files)
    else:
        # Use all JSON files in current directory
        combine_json_files()