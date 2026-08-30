"""
Data Normalization utilities.
Architecture reference: §2.3 (Data Normalizer)
"""

import re
from datetime import datetime
from typing import Optional, Any

def normalize_string(text: Optional[str]) -> Optional[str]:
    """Strip whitespace and newlines, handle N/A."""
    if not text:
        return None
    # Replace unicode non-breaking spaces and normalize
    cleaned = re.sub(r'\s+', ' ', text.replace('\xa0', ' ')).strip()
    if cleaned.upper() in ("N/A", "NA", "-", ""):
        return None
    return cleaned

def normalize_currency(text: Optional[str]) -> Optional[str]:
    """Strip ₹ and commas from currency strings, return as clean string (e.g., '120.50')."""
    cleaned = normalize_string(text)
    if not cleaned:
        return None
    cleaned = cleaned.replace('₹', '').replace(',', '').strip()
    return cleaned if cleaned else None

def normalize_percentage(text: Optional[str]) -> Optional[str]:
    """Strip % sign and return clean number string (e.g., '1.5')."""
    cleaned = normalize_string(text)
    if not cleaned:
        return None
    cleaned = cleaned.replace('%', '').strip()
    return cleaned if cleaned else None

def parse_date(date_str: Optional[str], format_str: str = "%d %b %Y") -> Optional[str]:
    """
    Parse a date string and return ISO 8601 formatted date (YYYY-MM-DD).
    Default format handles '12 Oct 2023'.
    """
    cleaned = normalize_string(date_str)
    if not cleaned:
        return None
    try:
        dt = datetime.strptime(cleaned, format_str)
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return cleaned  # Return original if parsing fails, but it's risky
