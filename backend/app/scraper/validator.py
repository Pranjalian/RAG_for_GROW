"""
Data Validation utilities.
Architecture reference: §2.3 (Data Validator)
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def validate_extracted_data(data: Dict[str, Any], mandatory_fields: List[str], source_url: str) -> bool:
    """
    Validates that extracted data contains all mandatory fields.
    Logs warnings for missing data.
    
    Returns:
        True if valid (all mandatory fields present and not None), False otherwise.
    """
    if not data:
        logger.error(f"Validation failed: No data extracted from {source_url}")
        return False
        
    is_valid = True
    for field in mandatory_fields:
        val = data.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            logger.error(f"Validation failed: Mandatory field '{field}' missing for {source_url}")
            is_valid = False
            
    # Check if completely empty
    non_empty = [k for k, v in data.items() if v is not None and v != ""]
    if not non_empty:
        logger.error(f"Validation failed: Extracted data is completely empty for {source_url}")
        return False
        
    return is_valid
