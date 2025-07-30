#!/usr/bin/env python3
"""
Flask Patent Viewer Application
A web interface for viewing patent data scraped from Google Patents
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import logging

# Set environment variables for OpenAI and LangSmith
os.environ["OPENAI_API_KEY"] = ""
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = ""
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_PROJECT"] = "default"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import patent report card functionality
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# 1️⃣  ──  Define the structured-output schema
class PatentReportCard(BaseModel):
    """Commercial-potential snapshot for investors & operators."""
    wow_score: int = Field(..., ge=0, le=1,
        description="0.0-0.2=niche, 0.2-0.4=of-interest, 0.4-0.6=strong, 0.6-0.8=very strong, 0.9-1.0=blockbuster")
    headline: str = Field(..., description="Elevator pitch that grabs investors")
    verdict: str = Field(..., description="Go / No-Go in ≤ 50 words")
    key_use_cases: List[str] = Field(...,
        description="3-5 crisp use-case phrases investors will understand. 1-2 sentences each.")
    rationale: str = Field(...,
        description="Why this score was assigned (market pull, moat, deployability, etc.) write a paragraph")
    
# Initialize the report card chain
def initialize_report_card_chain():
    """Initialize the patent report card generation chain"""
    try:
        # Check if OpenAI API key is available
        if not os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") == "":
            logger.warning("OPENAI_API_KEY not found in environment variables")
            return None
        
        # 2️⃣  ──  Build the prompt (system + human)
        system_template = """
        You are a senior IP & deep-tech analyst at an investment bank with a knack for identifying patents that are likely to be successful in the market and APPEALING TO INVESTORS.
        Audience: investors, banks and business operators.
        Assess the patent below for breadth, market gravity, feasibility, moat, platform scope, and scalability.
        Return ONLY a JSON object that conforms to the `PatentReportCard` schema.
        """


        human_template = "PATENT_INFO_JSON:\n{patent_json}"

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template),
        ])

        # Bind model with structured output
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(PatentReportCard)
        
        # Wire prompt ➜ model into a runnable chain
        return prompt | model
    except Exception as e:
        logger.error(f"Error initializing report card chain: {e}")
        return None

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
PATENT_JSONS_DIR = 'patent_jsons'
ALLOWED_EXTENSIONS = {'json'}

# Ensure the patent_jsons directory exists
os.makedirs(PATENT_JSONS_DIR, exist_ok=True)

# Initialize report card chain
report_card_chain = initialize_report_card_chain()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_patent_files():
    """Get list of patent JSON files"""
    patent_files = []
    if os.path.exists(PATENT_JSONS_DIR):
        for filename in os.listdir(PATENT_JSONS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(PATENT_JSONS_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        patent_data = json.load(f)
                    patent_files.append({
                        'filename': filename,
                        'patent_id': patent_data.get('patent_id', 'Unknown'),
                        'title': patent_data.get('title', 'No title available'),
                        'scraped_at': patent_data.get('scraped_at', 'Unknown'),
                        'filepath': filepath
                    })
                except Exception as e:
                    logger.error(f"Error reading {filename}: {e}")
    return sorted(patent_files, key=lambda x: x['scraped_at'], reverse=True)

def run_patent_scraper(patent_id):
    """Run the patent scraper script"""
    try:
        # Run the patent scraper
        result = subprocess.run([
            sys.executable, 'patent_scraper.py', patent_id
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            # Find the generated JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            expected_filename = f"patent_{patent_id}_{timestamp}.json"
            
            # Look for the most recent file for this patent
            patent_files = [f for f in os.listdir('.') if f.startswith(f"patent_{patent_id}_") and f.endswith('.json')]
            if patent_files:
                latest_file = max(patent_files, key=lambda x: os.path.getctime(x))
                
                # Move the file to patent_jsons directory
                if os.path.exists(latest_file):
                    new_path = os.path.join(PATENT_JSONS_DIR, latest_file)
                    os.rename(latest_file, new_path)
                    return {'success': True, 'filename': latest_file, 'message': 'Patent scraped successfully!'}
            
            return {'success': False, 'message': 'Patent scraped but file not found'}
        else:
            return {'success': False, 'message': f'Error scraping patent: {result.stderr}'}
    
    except Exception as e:
        logger.error(f"Error running patent scraper: {e}")
        return {'success': False, 'message': f'Error: {str(e)}'}

@app.route('/')
def index():
    """Home page"""
    patent_files = get_patent_files()
    return render_template('index.html', patent_files=patent_files)

@app.route('/search', methods=['POST'])
def search_patent():
    """Search for a patent"""
    patent_id = request.form.get('patent_id', '').strip()
    
    if not patent_id:
        flash('Please enter a patent ID', 'error')
        return redirect(url_for('index'))
    
    # Check if patent already exists
    existing_files = [f for f in os.listdir(PATENT_JSONS_DIR) if f.startswith(f"patent_{patent_id}_")]
    if existing_files:
        flash(f'Patent {patent_id} already exists in database', 'info')
        return redirect(url_for('view_patent', filename=existing_files[0]))
    
    # Run the patent scraper
    result = run_patent_scraper(patent_id)
    
    if result['success']:
        flash(f'Patent {patent_id} scraped successfully!', 'success')
        return redirect(url_for('view_patent', filename=result['filename']))
    else:
        flash(f'Error: {result["message"]}', 'error')
        return redirect(url_for('index'))

@app.route('/patent/<filename>')
def view_patent(filename):
    """View a specific patent"""
    filepath = os.path.join(PATENT_JSONS_DIR, filename)
    
    if not os.path.exists(filepath):
        flash('Patent file not found', 'error')
        return redirect(url_for('index'))
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            patent_data = json.load(f)
        
        return render_template('patent_view.html', patent=patent_data, filename=filename)
    
    except Exception as e:
        flash(f'Error reading patent file: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/api/patent/<filename>')
def api_patent(filename):
    """API endpoint to get patent data"""
    filepath = os.path.join(PATENT_JSONS_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Patent file not found'}), 404
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            patent_data = json.load(f)
        
        return jsonify(patent_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-report-card/<filename>', methods=['POST'])
def generate_report_card(filename):
    """Generate a patent report card"""
    filepath = os.path.join(PATENT_JSONS_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Patent file not found'}), 404
    
    if not report_card_chain:
        return jsonify({'error': 'Report card generation not available'}), 500
    
    try:
        # Read patent data
        with open(filepath, 'r', encoding='utf-8') as f:
            patent_data = json.load(f)
        
        # Generate report card
        report_card = report_card_chain.invoke({"patent_json": json.dumps(patent_data)})
        
        # Convert to dict for JSON response
        report_card_dict = {
            'wow_score': report_card.wow_score,
            'headline': report_card.headline,
            'verdict': report_card.verdict,
            'key_use_cases': report_card.key_use_cases,
            'rationale': report_card.rationale
        }
        
        return jsonify({
            'success': True,
            'report_card': report_card_dict
        })
    
    except Exception as e:
        logger.error(f"Error generating report card: {e}")
        return jsonify({'error': f'Error generating report card: {str(e)}'}), 500

@app.route('/delete/<filename>', methods=['POST'])
def delete_patent(filename):
    """Delete a patent file"""
    filepath = os.path.join(PATENT_JSONS_DIR, filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            flash(f'Patent {filename} deleted successfully', 'success')
        except Exception as e:
            flash(f'Error deleting patent: {e}', 'error')
    else:
        flash('Patent file not found', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 