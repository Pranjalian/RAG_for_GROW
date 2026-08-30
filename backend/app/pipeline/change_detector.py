"""
Content Hashing Utilities.
Architecture reference: §2.4 (Content Hashing)
"""

import json
import hashlib
from typing import Dict, Any

def compute_content_hash(extracted_data: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 hash of the extracted data dictionary.
    Used to detect if the content has changed since the last scrape.
    """
    if not extracted_data:
        return hashlib.sha256(b"").hexdigest()
        
    # Create a deterministic JSON string representation
    # sorting keys ensures identical dictionaries produce the same string
    serialized = json.dumps(extracted_data, sort_keys=True, separators=(',', ':'), default=str)
    
    # Compute SHA-256
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
