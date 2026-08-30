"""
Market News page extractor.
Architecture reference: §2.2.4
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup
from app.scraper.normalizer import normalize_string

def extract_market_news(html: str, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'lxml')
    
    news_items = []
    
    # Search for news articles, often wrapped in 'a' or 'article' tags
    for article in soup.find_all(['article', 'div'], {'class': lambda c: c and ('news' in c.lower() or 'article' in c.lower())}):
        title_tag = article.find(['h2', 'h3'])
        if not title_tag:
            continue
            
        title = normalize_string(title_tag.text)
        
        # Link
        link_tag = article.find('a', href=True)
        link = link_tag['href'] if link_tag else None
        
        # Summary
        summary_tag = article.find('p')
        summary = normalize_string(summary_tag.text) if summary_tag else None
        
        # Date
        time_tag = article.find('time')
        published_at = normalize_string(time_tag.text) if time_tag else None
        
        if title:
            news_items.append({
                'title': title,
                'link': link,
                'summary': summary,
                'published_at': published_at
            })
            
    return {
        'source_url': url,
        'news_articles': news_items,
        'page_title': normalize_string(soup.title.string) if soup.title else None
    }
