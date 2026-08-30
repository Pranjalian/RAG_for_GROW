"""
NFO page extractor.
Architecture reference: §2.2.3
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup
from app.scraper.normalizer import normalize_string

def extract_nfo(html: str, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'lxml')
    
    nfos = []
    
    # NFOs are usually displayed in a grid or table format.
    # We will look for repeating structural blocks.
    for card in soup.find_all('div', {'class': lambda c: c and 'nfo' in c.lower()}):
        name_tag = card.find('h3') or card.find('h2')
        if not name_tag:
            continue
            
        nfo_name = normalize_string(name_tag.text)
        
        # Simple extraction for other details within the card
        text_content = card.get_text(separator=' | ', strip=True)
        
        nfos.append({
            'nfo_name': nfo_name,
            'raw_details': text_content
        })
        
    return {
        'source_url': url,
        'nfos_listed': nfos,
        'page_title': normalize_string(soup.title.string) if soup.title else None
    }
