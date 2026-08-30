"""
Mutual Fund page extractor.
Architecture reference: §2.2.1
"""

import json
from typing import Dict, Any
from bs4 import BeautifulSoup
from app.scraper.normalizer import normalize_string, normalize_currency, normalize_percentage, parse_date

def extract_mutual_fund(html: str, url: str) -> Dict[str, Any]:
    """
    Extracts mutual fund details from the rendered HTML of a Groww mutual fund page.
    """
    soup = BeautifulSoup(html, 'lxml')
    data = {}
    
    # 1. Try to extract from __NEXT_DATA__ if available (Groww uses Next.js)
    next_data_script = soup.find('script', id='__NEXT_DATA__')
    if next_data_script and next_data_script.string:
        try:
            next_data = json.loads(next_data_script.string)
            mf_data = next_data.get('props', {}).get('pageProps', {}).get('mfServerSideData', {})
            
            if mf_data:
                data['fund_name'] = mf_data.get('scheme_name') or mf_data.get('fund_name')
                data['nav'] = str(mf_data.get('nav', '')) if mf_data.get('nav') is not None else None
                data['nav_date'] = mf_data.get('nav_date')
                
                # Returns
                returns = mf_data.get('return_stats', [{}])[0] if mf_data.get('return_stats') else {}
                data['returns_1y'] = str(returns.get('return1y', '')) if returns.get('return1y') is not None else None
                data['returns_3y'] = str(returns.get('return3y', '')) if returns.get('return3y') is not None else None
                data['returns_5y'] = str(returns.get('return5y', '')) if returns.get('return5y') is not None else None
                
                # Stats
                data['expense_ratio'] = str(mf_data.get('expense_ratio', '')) if mf_data.get('expense_ratio') is not None else None
                data['exit_load'] = mf_data.get('exit_load')
                data['fund_size_aum'] = str(mf_data.get('aum', '')) if mf_data.get('aum') is not None else None
                
                # Risk and Rating
                data['risk_level'] = mf_data.get('groww_rating') or mf_data.get('crisil_rating') or mf_data.get('risk')
                data['rating'] = str(mf_data.get('groww_rating', '')) if mf_data.get('groww_rating') is not None else None
                
                data['category'] = mf_data.get('category')
                data['amc'] = mf_data.get('amc')
                data['fund_manager'] = mf_data.get('fund_manager')
                
                # Holdings
                holdings = mf_data.get('holdings', [])
                if holdings:
                    data['top_holdings'] = [{'company': h.get('company_name'), 'percentage': h.get('corpus_per')} for h in holdings[:10]]
                    
                data['sector_allocation'] = [] # Could be extracted from holdings if needed
        except json.JSONDecodeError:
            pass

    # 2. Extract from JSON-LD schema (frequently used for SEO)
    ld_scripts = soup.find_all('script', type='application/ld+json')
    for script in ld_scripts:
        if script.string:
            try:
                ld_data = json.loads(script.string)
                if isinstance(ld_data, dict):
                    if ld_data.get('@type') == 'FinancialProduct' or 'name' in ld_data:
                        data['fund_name'] = data.get('fund_name') or ld_data.get('name')
            except json.JSONDecodeError:
                continue
                
    # 3. DOM Parsing (Fallbacks)
    if not data.get('fund_name'):
        h1 = soup.find('h1')
        data['fund_name'] = normalize_string(h1.text) if h1 else None

    # Search for common labels and extract adjacent values if still missing
    labels_to_fields = {
        'NAV': 'nav',
        'Expense Ratio': 'expense_ratio',
        'Exit Load': 'exit_load',
        'Fund Size': 'fund_size_aum',
        'AUM': 'fund_size_aum',
        'Risk': 'risk_level'
    }
    
    for td in soup.find_all(['td', 'div', 'span']):
        text = td.get_text(strip=True)
        for label, field in labels_to_fields.items():
            if label in text and len(text) < len(label) + 15 and not data.get(field):
                sibling = td.find_next_sibling()
                if sibling:
                    val = sibling.get_text(strip=True)
                    if field == 'nav' or field == 'fund_size_aum':
                        data[field] = normalize_currency(val)
                    elif field == 'expense_ratio':
                        data[field] = normalize_percentage(val)
                    else:
                        data[field] = normalize_string(val)
                        
    # Ensure these are initialized if not found
    for key in ['returns_1y', 'returns_3y', 'returns_5y', 'top_holdings', 'sector_allocation']:
        if key not in data:
            data[key] = [] if key in ('top_holdings', 'sector_allocation') else None

    # Fallback missing data to None to let validator handle it
    return {
        'fund_name': data.get('fund_name'),
        'nav': data.get('nav'),
        'nav_date': data.get('nav_date', parse_date(None)), # Optional if found
        'returns_1y': data.get('returns_1y'),
        'returns_3y': data.get('returns_3y'),
        'returns_5y': data.get('returns_5y'),
        'expense_ratio': data.get('expense_ratio'),
        'exit_load': data.get('exit_load'),
        'risk_level': data.get('risk_level'),
        'fund_size_aum': data.get('fund_size_aum'),
        'rating': data.get('rating'),
        'fund_manager': data.get('fund_manager'),
        'category': data.get('category'),
        'amc': data.get('amc'),
        'top_holdings': data.get('top_holdings'),
        'sector_allocation': data.get('sector_allocation'),
        'source_url': url
    }
