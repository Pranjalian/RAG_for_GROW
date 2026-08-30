"""
Filter page extractor (Fund Listing).
Architecture reference: §2.2.5
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup
from app.scraper.normalizer import normalize_string

def extract_filter_page(html: str, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'lxml')
    
    funds = []
    
    # Typically filter pages display a list or table of funds
    for row in soup.find_all('tr'):
        cells = row.find_all(['td', 'th'])
        if len(cells) < 2:
            continue
            
        fund_name_tag = cells[0].find('a')
        if not fund_name_tag:
            continue
            
        fund_name = normalize_string(fund_name_tag.text)
        link = fund_name_tag.get('href')
        
        # We grab all cell texts as basic info
        details = [normalize_string(c.text) for c in cells[1:]]
        
        funds.append({
            'fund_name': fund_name,
            'link': link,
            'details': details
        })
        
    return {
        'source_url': url,
        'funds_listed': funds,
        'page_title': normalize_string(soup.title.string) if soup.title else None
    }
