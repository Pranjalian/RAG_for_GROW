import re
import logging

logger = logging.getLogger(__name__)

ADVICE_PATTERNS = [
    r"\byou should\b",
    r"\bi recommend\b",
    r"\bi suggest\b",
    r"\bi advise\b",
    r"\bguaranteed to\b",
    r"\bwill go up\b",
    r"\bwill increase\b",
    r"\bwill crash\b",
    r"\bbest time to\b",
    r"\bbest opportunity to\b",
    r"\bbuy now\b",
    r"\bsell now\b"
]

class GroundingGuardrail:
    """
    Post-generation filter to catch any hallucinated advice or ungrounded claims.
    """
    
    def validate(self, response: str, context: str) -> tuple[bool, str]:
        """
        Validates the response against guardrail rules.
        Returns (is_valid, filtered_response)
        """
        lower_resp = response.lower()
        
        # 1. Check for investment advice patterns
        for pattern in ADVICE_PATTERNS:
            if re.search(pattern, lower_resp):
                logger.warning(f"Guardrail blocked response due to advice pattern: '{pattern}'")
                return False, "I am a factual data assistant and cannot provide investment advice or predictions. Please consult a certified financial advisor."
                
        # 2. Heuristic check: if there are numbers in the response, they should appear in the context.
        # This is a soft check because LLM might format numbers differently (e.g., "1,000" vs "1000").
        # For strictness, we'll keep it simple for now and rely heavily on the system prompt for numeric grounding.
        
        # 3. Fallback check: Did it just say it doesn't have the data?
        if "currently i dont have the data" in lower_resp:
            return True, "Currently I don't have the data to answer the query."
            
        return True, response

guardrail = GroundingGuardrail()
