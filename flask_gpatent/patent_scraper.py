#!/usr/bin/env python3
"""
Patent scraper for Canadian IP Marketplace
This script systematically scrapes patent data from the ised-isde.canada.ca patent database
Uses Selenium for JavaScript-rendered content with improved error handling and logging
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GooglePatentScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://patents.google.com/patent/"
    
    def get_patent_info(self, patent_id):
        """
        Extract comprehensive patent information from Google Patents
        
        Args:
            patent_id (str): Patent ID (e.g., 'US20210129107', 'WO2022120498')
            
        Returns:
            dict: Dictionary containing all extracted patent information
        """
        url = f"{self.base_url}{patent_id}"
        
        try:
            logger.info(f"Fetching patent information for {patent_id}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            patent_info = {
                'patent_id': patent_id,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'title': self._extract_title(soup),
                'publication_number': self._extract_publication_number(soup),
                'authority': self._extract_authority(soup),
                'legal_status': self._extract_legal_status(soup),
                'application_number': self._extract_application_number(soup),
                'inventors': self._extract_inventors(soup),
                'assignees': self._extract_assignees(soup),
                'priority_date': self._extract_priority_date(soup),
                'filing_date': self._extract_filing_date(soup),
                'publication_date': self._extract_publication_date(soup),
                'grant_date': self._extract_grant_date(soup),
                'expiration_date': self._extract_expiration_date(soup),
                'abstract': self._extract_abstract(soup),
                'claims': self._extract_claims(soup),
                'description': self._extract_description(soup),
                'prior_art_keywords': self._extract_prior_art_keywords(soup),
                'legal_events': self._extract_legal_events(soup),
                'cited_patents': self._extract_cited_patents(soup),
                'citing_patents': self._extract_citing_patents(soup),
                'family_members': self._extract_family_members(soup),
                'classification_codes': self._extract_classification_codes(soup),
                'raw_html_length': len(response.content)
            }
            
            logger.info(f"Successfully extracted information for {patent_id}")
            return patent_info
            
        except requests.RequestException as e:
            logger.error(f"Error fetching patent {patent_id}: {e}")
            return {'error': str(e), 'patent_id': patent_id}
        except Exception as e:
            logger.error(f"Error processing patent {patent_id}: {e}")
            return {'error': str(e), 'patent_id': patent_id}
    
    def _extract_title(self, soup):
        """Extract patent title"""
        try:
            # Look for title in various possible locations
            title_selectors = [
                'h1',
                '[data-title]',
                '.title',
                'title'
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    title = element.get_text().strip()
                    # Clean up the title
                    title = re.sub(r'\s+', ' ', title)  # Remove extra whitespace
                    title = re.sub(r'-\s*Google Patents', '', title)  # Remove Google Patents suffix
                    return title.strip()
            
            # Fallback: look for any heading that might contain the title
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings:
                text = heading.get_text().strip()
                if text and len(text) > 10:  # Likely a title if it's substantial
                    return text
                    
            return None
        except Exception as e:
            logger.warning(f"Error extracting title: {e}")
            return None
    
    def _extract_publication_number(self, soup):
        """Extract publication number"""
        try:
            # Look for publication number in various formats
            patterns = [
                r'US\d+[A-Z]?\d*',
                r'WO\d+[A-Z]?\d*',
                r'EP\d+[A-Z]?\d*',
                r'CN\d+[A-Z]?\d*',
                r'JP\d+[A-Z]?\d*'
            ]
            
            text = soup.get_text()
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group()
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting publication number: {e}")
            return None
    
    def _extract_authority(self, soup):
        """Extract patent authority (country/office)"""
        try:
            # Look for authority information
            authority_selectors = [
                '[data-authority]',
                '.authority',
                '.country'
            ]
            
            for selector in authority_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
            
            # Try to extract from publication number
            pub_num = self._extract_publication_number(soup)
            if pub_num:
                if pub_num.startswith('US'):
                    return 'United States'
                elif pub_num.startswith('WO'):
                    return 'World Intellectual Property Organization'
                elif pub_num.startswith('EP'):
                    return 'European Patent Office'
                elif pub_num.startswith('CN'):
                    return 'China'
                elif pub_num.startswith('JP'):
                    return 'Japan'
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting authority: {e}")
            return None
    
    def _extract_legal_status(self, soup):
        """Extract legal status"""
        try:
            status_selectors = [
                '[data-status]',
                '.status',
                '.legal-status'
            ]
            
            for selector in status_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting legal status: {e}")
            return None
    
    def _extract_application_number(self, soup):
        """Extract application number"""
        try:
            # Look for application number patterns
            patterns = [
                r'Application number[:\s]+([A-Z]{2}\d+[A-Z]?\d*)',
                r'App\.?\s*No\.?[:\s]+([A-Z]{2}\d+[A-Z]?\d*)'
            ]
            
            text = soup.get_text()
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting application number: {e}")
            return None
    
    def _extract_inventors(self, soup):
        """Extract inventors"""
        try:
            inventors = []
            
            # Look for inventor information in specific sections
            text = soup.get_text()
            
            # Look for inventor patterns in the text
            inventor_patterns = [
                r'Inventor[:\s]+([^,\n]+)',
                r'Inventors[:\s]+([^,\n]+)',
                r'Inventor\s*\(s\)[:\s]+([^,\n]+)'
            ]
            
            for pattern in inventor_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Clean up the match
                    match = re.sub(r'\([^)]*\)', '', match)  # Remove parenthetical text
                    match = re.sub(r'[^\w\s]', '', match)  # Remove special characters
                    names = [name.strip() for name in match.split(',') if name.strip()]
                    inventors.extend(names)
            
            # Also look for specific inventor elements
            inventor_selectors = [
                '[data-inventor]',
                '.inventor',
                '.inventors'
            ]
            
            for selector in inventor_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text and 'inventor' in text.lower():
                        # Extract names from the text
                        names = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
                        inventors.extend(names)
            
            # Clean up and deduplicate
            cleaned_inventors = []
            for inventor in inventors:
                inventor = inventor.strip()
                if inventor and len(inventor) > 2 and inventor not in cleaned_inventors:
                    cleaned_inventors.append(inventor)
            
            return cleaned_inventors if cleaned_inventors else None
        except Exception as e:
            logger.warning(f"Error extracting inventors: {e}")
            return None
    
    def _extract_assignees(self, soup):
        """Extract assignees"""
        try:
            assignees = []
            
            # Look for assignee information in specific sections
            text = soup.get_text()
            
            # Look for assignee patterns in the text
            assignee_patterns = [
                r'Assignee[:\s]+([^,\n]+)',
                r'Assignees[:\s]+([^,\n]+)',
                r'Current Assignee[:\s]+([^,\n]+)',
                r'Original Assignee[:\s]+([^,\n]+)'
            ]
            
            for pattern in assignee_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Clean up the match
                    match = re.sub(r'\([^)]*\)', '', match)  # Remove parenthetical text
                    match = re.sub(r'[^\w\s]', '', match)  # Remove special characters
                    names = [name.strip() for name in match.split(',') if name.strip()]
                    assignees.extend(names)
            
            # Also look for specific assignee elements
            assignee_selectors = [
                '[data-assignee]',
                '.assignee',
                '.assignees'
            ]
            
            for selector in assignee_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text:
                        assignees.append(text)
            
            # Clean up and deduplicate
            cleaned_assignees = []
            for assignee in assignees:
                assignee = assignee.strip()
                if assignee and len(assignee) > 2 and assignee not in cleaned_assignees:
                    # Filter out common non-assignee text
                    if not any(skip in assignee.lower() for skip in [
                        'google', 'patents', 'legal', 'analysis', 'representation', 'warranty', 'accuracy'
                    ]):
                        cleaned_assignees.append(assignee)
            
            return cleaned_assignees if cleaned_assignees else None
        except Exception as e:
            logger.warning(f"Error extracting assignees: {e}")
            return None
    
    def _extract_priority_date(self, soup):
        """Extract priority date"""
        return self._extract_date(soup, 'priority')
    
    def _extract_filing_date(self, soup):
        """Extract filing date"""
        return self._extract_date(soup, 'filing')
    
    def _extract_publication_date(self, soup):
        """Extract publication date"""
        return self._extract_date(soup, 'publication')
    
    def _extract_grant_date(self, soup):
        """Extract grant date"""
        return self._extract_date(soup, 'grant')
    
    def _extract_expiration_date(self, soup):
        """Extract expiration date"""
        return self._extract_date(soup, 'expiration')
    
    def _extract_date(self, soup, date_type):
        """Generic date extraction method"""
        try:
            text = soup.get_text()
            
            # Look for date patterns
            date_patterns = [
                rf'{date_type.title()}\s+date[:\s]+(\d{{4}}-\d{{2}}-\d{{2}})',
                rf'{date_type.title()}\s+date[:\s]+(\d{{2}}/\d{{2}}/\d{{4}})',
                rf'{date_type.title()}\s+date[:\s]+(\w+\s+\d{{1,2}},\s+\d{{4}})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting {date_type} date: {e}")
            return None
    
    def _extract_abstract(self, soup):
        """Extract patent abstract"""
        try:
            abstract_selectors = [
                '[data-abstract]',
                '.abstract',
                '.summary'
            ]
            
            for selector in abstract_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting abstract: {e}")
            return None
    
    def _extract_claims(self, soup):
        """Extract patent claims"""
        try:
            claims_selectors = [
                '[data-claims]',
                '.claims',
                '.claim'
            ]
            
            claims = []
            for selector in claims_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text:
                        claims.append(text)
            
            return claims if claims else None
        except Exception as e:
            logger.warning(f"Error extracting claims: {e}")
            return None
    
    def _extract_description(self, soup):
        """Extract patent description"""
        try:
            desc_selectors = [
                '[data-description]',
                '.description',
                '.specification'
            ]
            
            for selector in desc_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting description: {e}")
            return None
    
    def _extract_prior_art_keywords(self, soup):
        """Extract prior art keywords"""
        try:
            keywords = []
            text = soup.get_text()
            
            # Look for keywords section
            keyword_patterns = [
                r'Prior art keywords[:\s]+([^,\n]+)',
                r'Keywords[:\s]+([^,\n]+)'
            ]
            
            for pattern in keyword_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    words = [word.strip() for word in match.split(',')]
                    keywords.extend(words)
            
            return list(set(keywords)) if keywords else None
        except Exception as e:
            logger.warning(f"Error extracting prior art keywords: {e}")
            return None
    
    def _extract_legal_events(self, soup):
        """Extract legal events timeline"""
        try:
            events = []
            
            # Look for legal events table or timeline
            event_selectors = [
                '.legal-events',
                '.timeline',
                'table'
            ]
            
            for selector in event_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text()
                    if 'legal' in text.lower() or 'event' in text.lower():
                        # Extract date and event information
                        event_patterns = [
                            r'(\d{4}-\d{2}-\d{2})[:\s]+([^,\n]+)',
                            r'(\w+\s+\d{1,2},\s+\d{4})[:\s]+([^,\n]+)'
                        ]
                        
                        for pattern in event_patterns:
                            matches = re.findall(pattern, text)
                            for date, event in matches:
                                events.append({
                                    'date': date.strip(),
                                    'event': event.strip()
                                })
            
            return events if events else None
        except Exception as e:
            logger.warning(f"Error extracting legal events: {e}")
            return None
    
    def _extract_cited_patents(self, soup):
        """Extract cited patents"""
        try:
            cited = []
            
            # Look for cited patents section
            cited_selectors = [
                '.cited-patents',
                '.references',
                '[data-cited]'
            ]
            
            for selector in cited_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text()
                    # Extract patent numbers
                    patent_patterns = [
                        r'US\d+[A-Z]?\d*',
                        r'WO\d+[A-Z]?\d*',
                        r'EP\d+[A-Z]?\d*'
                    ]
                    
                    for pattern in patent_patterns:
                        matches = re.findall(pattern, text)
                        cited.extend(matches)
            
            return list(set(cited)) if cited else None
        except Exception as e:
            logger.warning(f"Error extracting cited patents: {e}")
            return None
    
    def _extract_citing_patents(self, soup):
        """Extract patents that cite this one"""
        try:
            citing = []
            
            # Look for citing patents section
            citing_selectors = [
                '.citing-patents',
                '.cited-by',
                '[data-citing]'
            ]
            
            for selector in citing_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text()
                    # Extract patent numbers
                    patent_patterns = [
                        r'US\d+[A-Z]?\d*',
                        r'WO\d+[A-Z]?\d*',
                        r'EP\d+[A-Z]?\d*'
                    ]
                    
                    for pattern in patent_patterns:
                        matches = re.findall(pattern, text)
                        citing.extend(matches)
            
            return list(set(citing)) if citing else None
        except Exception as e:
            logger.warning(f"Error extracting citing patents: {e}")
            return None
    
    def _extract_family_members(self, soup):
        """Extract patent family members"""
        try:
            family = []
            
            # Look for family members section
            family_selectors = [
                '.family-members',
                '.patent-family',
                '[data-family]'
            ]
            
            for selector in family_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text()
                    # Extract patent numbers
                    patent_patterns = [
                        r'US\d+[A-Z]?\d*',
                        r'WO\d+[A-Z]?\d*',
                        r'EP\d+[A-Z]?\d*'
                    ]
                    
                    for pattern in patent_patterns:
                        matches = re.findall(pattern, text)
                        family.extend(matches)
            
            return list(set(family)) if family else None
        except Exception as e:
            logger.warning(f"Error extracting family members: {e}")
            return None
    
    def _extract_classification_codes(self, soup):
        """Extract classification codes"""
        try:
            codes = []
            
            # Look for classification codes
            code_selectors = [
                '.classification',
                '.ipc-codes',
                '[data-classification]'
            ]
            
            for selector in code_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text()
                    # Extract IPC codes
                    ipc_pattern = r'[A-Z]\d{2}[A-Z]\s+\d{2}/\d{2}'
                    matches = re.findall(ipc_pattern, text)
                    codes.extend(matches)
            
            return list(set(codes)) if codes else None
        except Exception as e:
            logger.warning(f"Error extracting classification codes: {e}")
            return None
    
    def save_to_json(self, patent_info, filename=None):
        """Save patent information to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"patent_{patent_info['patent_id']}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(patent_info, f, indent=2, ensure_ascii=False)
            logger.info(f"Patent information saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return None

def main():
    """Scrape patent information for the provided patent ID"""
    if len(sys.argv) != 2:
        print("Usage: python patent_scraper.py <patent_id>")
        print("Example: python patent_scraper.py US20210129107")
        sys.exit(1)
    
    patent_id = sys.argv[1]
    scraper = GooglePatentScraper()
    
    print(f"\n{'='*50}")
    print(f"Scraping patent: {patent_id}")
    print(f"{'='*50}")
    
    patent_info = scraper.get_patent_info(patent_id)
    
    if 'error' not in patent_info:
        print(f"Title: {patent_info.get('title', 'N/A')}")
        print(f"Publication Number: {patent_info.get('publication_number', 'N/A')}")
        print(f"Authority: {patent_info.get('authority', 'N/A')}")
        print(f"Legal Status: {patent_info.get('legal_status', 'N/A')}")
        print(f"Inventors: {patent_info.get('inventors', 'N/A')}")
        print(f"Assignees: {patent_info.get('assignees', 'N/A')}")
        print(f"Filing Date: {patent_info.get('filing_date', 'N/A')}")
        print(f"Publication Date: {patent_info.get('publication_date', 'N/A')}")
        
        # Save to JSON
        filename = scraper.save_to_json(patent_info)
        if filename:
            print(f"Saved to: {filename}")
    else:
        print(f"Error: {patent_info['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()