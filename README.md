# Canadian Patent Scraper

A robust web scraper for extracting patent data from the Canadian IP Marketplace (ised-isde.canada.ca).

## Features

- **Object-Oriented Design**: Clean, maintainable code structure using classes and dataclasses
- **Comprehensive Logging**: Detailed logging to both file and console for debugging
- **Error Handling**: Robust error handling with retry mechanisms
- **Configuration Management**: External configuration file for easy customization
- **Data Validation**: Patent data validation and cleaning
- **Anti-Detection**: Chrome options to avoid bot detection
- **Rate Limiting**: Respectful scraping with configurable delays
- **Output Management**: Organized output with summary statistics

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure Chrome and ChromeDriver are installed

## Usage

### Basic Usage

```bash
python patent_scraper.py
```

### Configuration

Edit `config.json` to customize:
- Page range to scrape
- Timeout settings
- Rate limiting delays
- Output directory
- Chrome options
- Timestamp settings (enable/disable, format)

### Output Files

The scraper generates several output files in the `output/` directory with timestamps to prevent overwriting:

- `raw_patents_YYYYMMDD_HHMMSS.json`: Raw scraped patent data
- `cleaned_patents_YYYYMMDD_HHMMSS.json`: Cleaned and validated patent data
- `scrape_summary_YYYYMMDD_HHMMSS.json`: Summary statistics of the scraping session
- `scraper.log`: Detailed logging information

**Example filenames:**
- `raw_patents_20241201_143022.json`
- `cleaned_patents_20241201_143022.json`
- `scrape_summary_20241201_143022.json`

## Usage Examples

### Basic Usage
```bash
python patent_scraper.py
```

### Testing
```bash
python test_scraper.py
```

### Analysis
```bash
python analyze_patents.py output/cleaned_patents_YYYYMMDD_HHMMSS.json
```

### Demo
```bash
python demo_scraper.py
```

### List Output Files
```bash
# List all output files with timestamps
python list_outputs.py list

# Show latest scrape summary
python list_outputs.py latest

# List files from specific directory
python list_outputs.py list custom_output_dir
```

## Patent Data Structure

Each patent record contains:

```json
{
  "title": "Patent title",
  "patent_number": "CA2123456",
  "organization": "Company/Inventor name",
  "patent_type": "Utility Patent",
  "year": "2023",
  "date_added": "2023-01-01",
  "url": "Patent URL",
  "description": "Patent description"
}
```

## Key Improvements

### 1. **Better Code Structure**
- Used dataclasses for type safety
- Separated configuration from logic
- Object-oriented design for maintainability

### 2. **Enhanced Error Handling**
- Retry mechanism for failed requests
- Comprehensive exception handling
- Graceful degradation when elements aren't found

### 3. **Improved Data Extraction**
- Multiple regex patterns for patent numbers
- Better title cleaning algorithms
- More robust element selection strategies

### 4. **Logging and Monitoring**
- Detailed logging to file and console
- Progress tracking
- Summary statistics generation

### 5. **Configuration Management**
- External configuration file
- Easy customization without code changes
- Environment-specific settings

### 6. **Anti-Detection Measures**
- Updated user agent strings
- Disabled automation flags
- Additional Chrome options to avoid detection

## Timestamp Configuration

The scraper automatically adds timestamps to output filenames to prevent overwriting. You can configure this behavior in `config.json`:

```json
{
  "output": {
    "use_timestamps": true,
    "timestamp_format": "%Y%m%d_%H%M%S"
  }
}
```

**Options:**
- `use_timestamps`: Set to `false` to disable timestamps (files will overwrite)
- `timestamp_format`: Customize the timestamp format (default: `%Y%m%d_%H%M%S`)

**Common timestamp formats:**
- `%Y%m%d_%H%M%S` → `20241201_143022`
- `%Y-%m-%d_%H-%M-%S` → `2024-12-01_14-30-22`
- `%Y%m%d` → `20241201`

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Install ChromeDriver and ensure it's in PATH
   - Or use `webdriver-manager` for automatic management

2. **No patents found**
   - Check if the website structure has changed
   - Review the log file for detailed error messages
   - Verify the URL is still accessible

3. **Timeout errors**
   - Increase timeout in config.json
   - Check internet connection
   - Verify the website is responding

### Debug Mode

Set logging level to DEBUG in config.json for more detailed output:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect the website's terms of service and robots.txt file when using this scraper. 