# Flask Patent Viewer with AI Report Cards

A web interface for viewing patent data scraped from Google Patents with AI-powered commercial potential analysis.

## Features

- **Patent Scraping**: Scrape patent data from Google Patents using patent IDs
- **Patent Viewing**: View detailed patent information including abstract, claims, inventors, and assignees
- **AI Report Cards**: Generate commercial potential analysis using OpenAI's GPT-4o-mini model
- **Modern UI**: Clean, responsive interface with dark/light mode support

## Report Card Features

The AI report card provides:
- **WOW Score**: 0-10 rating of commercial potential (0-2=niche, 3-5=limited, 6-8=strong, 9-10=blockbuster)
- **Headline**: One-line hook that grabs investors' attention
- **Verdict**: Go/No-Go decision in ≤20 words
- **Key Use Cases**: 3-5 crisp use-case phrases investors will understand
- **Rationale**: Detailed explanation of the score (market pull, moat, deployability, etc.)

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API Key** (for report card functionality):
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the Web Interface**:
   Open http://localhost:5001 in your browser

## Usage

### Scraping Patents
1. Enter a patent ID (e.g., `US20210129107`, `CA2865675A1`)
2. Click "Search Patent"
3. The patent data will be scraped and stored locally

### Viewing Patents
1. Browse the list of scraped patents on the home page
2. Click on any patent to view its details
3. View abstract, claims, inventors, and assignees

### Generating Report Cards
1. Navigate to any patent's detail page
2. Click "Generate Report Card" button
3. Wait for the AI analysis to complete
4. View the commercial potential assessment

## API Endpoints

- `GET /` - Home page with patent list
- `POST /search` - Search and scrape a new patent
- `GET /patent/<filename>` - View patent details
- `POST /generate-report-card/<filename>` - Generate AI report card
- `GET /api/patent/<filename>` - Get patent data as JSON
- `POST /delete/<filename>` - Delete a patent file

## File Structure

```
flask_gpatent/
├── app.py                 # Main Flask application
├── patent_scraper.py      # Patent scraping logic
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   └── patent_view.html
└── patent_jsons/        # Stored patent data
    └── *.json
```

## Dependencies

- **Flask**: Web framework
- **LangChain**: AI/LLM integration
- **OpenAI**: GPT-4o-mini model for report cards
- **BeautifulSoup**: HTML parsing for patent scraping
- **Pydantic**: Data validation for report cards

## Notes

- Report card generation requires a valid OpenAI API key
- Patent data is stored locally in JSON format
- The app runs in debug mode by default (not suitable for production)
- All patent data is publicly available from Google Patents

## Troubleshooting

**Report Card Not Available**: Ensure your OpenAI API key is set correctly:
```bash
export OPENAI_API_KEY="sk-..."
```

**Patent Scraping Fails**: Check that the patent ID is valid and exists on Google Patents.

**App Won't Start**: Ensure all dependencies are installed and port 5001 is available. 