"""
AMC page extractor.
Architecture reference: §2.2.2
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
from app.scraper.normalizer import normalize_string

def extract_amc(html: str, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'lxml')
    data = {}
    
    h1 = soup.find('h1')
    data['amc_name'] = normalize_string(h1.text) if h1 else None
    
    # Try to find description
    desc_tag = soup.find('div', {'class': lambda c: c and 'description' in c.lower()})
    if not desc_tag:
        # Fallback to first paragraph after h1
        if h1:
            desc_tag = h1.find_next('p')
            
    data['description'] = normalize_string(desc_tag.text) if desc_tag else None
    
    # Fund list
    funds = []
    for a in soup.find_all('a', href=True):
        if '/mutual-funds/' in a['href'] and a.text:
            funds.append(normalize_string(a.text))
            
    data['funds_listed'] = list(set(funds))  # deduplicate
    data['source_url'] = url
    
    return data
