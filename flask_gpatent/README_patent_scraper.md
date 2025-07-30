# Google Patents Scraper

A comprehensive Python tool to extract patent information from Google Patents pages.

## Features

- Extracts comprehensive patent information including:
  - Title and publication number
  - Inventors and assignees
  - Filing, publication, and grant dates
  - Abstract and claims
  - Legal status and events
  - Cited and citing patents
  - Patent family members
  - Classification codes
  - Prior art keywords

- Supports multiple patent formats (US, WO, EP, CN, JP)
- Saves data to JSON format
- Includes error handling and logging
- Rate limiting to be respectful to Google's servers

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_patent_scraper.txt
```

## Usage

### Basic Usage

```python
from patent_scraper import GooglePatentScraper

# Create scraper instance
scraper = GooglePatentScraper()

# Extract patent information
patent_info = scraper.get_patent_info('US20210129107')

# Save to JSON file
filename = scraper.save_to_json(patent_info)
print(f"Saved to: {filename}")
```

### Command Line Usage

Run the scraper directly to test with sample patents:

```bash
python patent_scraper.py
```

This will test the scraper with two sample patents:
- US20210129107 (Nucleic acid amplification patent)
- WO2022120498 (Helmet patent)

### Supported Patent Formats

The scraper supports various patent formats:
- **US**: United States patents (e.g., US20210129107)
- **WO**: World Intellectual Property Organization patents (e.g., WO2022120498)
- **EP**: European Patent Office patents
- **CN**: Chinese patents
- **JP**: Japanese patents

## Output Format

The scraper returns a dictionary with the following structure:

```json
{
  "patent_id": "US20210129107",
  "url": "https://patents.google.com/patent/US20210129107",
  "scraped_at": "2025-07-29T16:00:49.596322",
  "title": "US20210129107A1 - Compositions and methods for the amplification of nucleic acids",
  "publication_number": "US20210129107A1",
  "authority": "United States",
  "legal_status": null,
  "application_number": "US17",
  "inventors": ["JianBing Fan"],
  "assignees": ["Illumina Inc"],
  "priority_date": null,
  "filing_date": "2020-11-16",
  "publication_date": "2021-05-06",
  "grant_date": null,
  "expiration_date": null,
  "abstract": "The present disclosure relates to systems and methods...",
  "claims": ["1.-119. (canceled)", "120. A method of preparing..."],
  "description": "RELATED APPLICATIONS\nThis application is a continuation...",
  "prior_art_keywords": null,
  "legal_events": null,
  "cited_patents": null,
  "citing_patents": null,
  "family_members": null,
  "classification_codes": null,
  "raw_html_length": 123456
}
```

## Error Handling

The scraper includes comprehensive error handling:
- Network errors are caught and logged
- Missing data fields return `null` instead of causing errors
- Invalid patent IDs are handled gracefully
- Rate limiting prevents overwhelming the server

## Rate Limiting

The scraper includes a 2-second delay between requests to be respectful to Google's servers. For production use, consider implementing more sophisticated rate limiting.

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `lxml`: XML/HTML parser backend

## Example Output

When you run the scraper, you'll see output like:

```
==================================================
Scraping patent: US20210129107
==================================================
Title: US20210129107A1 - Compositions and methods for the amplification of nucleic acids
Publication Number: US20210129107A1
Authority: United States
Legal Status: None
Inventors: ['JianBing Fan']
Assignees: ['Illumina Inc']
Filing Date: 2020-11-16
Publication Date: 2021-05-06
Saved to: patent_US20210129107_20250729_160050.json
```

## Notes

- The scraper extracts data from the public Google Patents pages
- Some fields may be `null` if the information is not available on the page
- The scraper is designed to be robust and handle various page layouts
- Always respect the website's terms of service and robots.txt when scraping

## License

This tool is provided for educational and research purposes. Please ensure you comply with Google Patents' terms of service when using this scraper. 