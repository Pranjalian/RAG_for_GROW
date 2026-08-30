import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

QUERY_TYPES = [
    "fund_lookup",       # "What is the NAV of HDFC Mid Cap Fund?"
    "fund_comparison",   # "Compare HDFC Small Cap and Nippon India Small Cap"
    "nfo_query",         # "What new NFOs are available?"
    "news_query",        # "What are the latest market news?"
    "category_search",   # "Which funds are in the pharma category?"
    "metric_search",     # "Which fund has the lowest expense ratio?"
    "freshness_query",   # "When was this data last updated?"
    "change_query",      # "What changed since last refresh?"
    "advice_request",    # "Should I buy HDFC Mid Cap Fund?"
    "general",           # Anything else
]

CLASSIFIER_PROMPT = """
You are a query classifier for a mutual fund RAG application.
Categorize the following user query into EXACTLY ONE of these types:
{types}

Output ONLY the exact string from the list above. No other text.
If unsure, output "general".

Query: {query}
"""

class QueryClassifier:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.GROK_API_KEY,
            base_url=settings.GROK_API_BASE_URL
        )

    async def classify(self, query: str) -> str:
        """Classify a user query using GROK LLM."""
        if not settings.GROK_API_KEY:
            logger.warning("GROK_API_KEY not set, defaulting to 'general' classification")
            return "general"
            
        try:
            prompt = CLASSIFIER_PROMPT.format(
                types="\n".join(f"- {qt}" for qt in QUERY_TYPES),
                query=query
            )
            
            response = await self.client.chat.completions.create(
                model=settings.GROK_MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            
            result = response.choices[0].message.content.strip().lower()
            
            # Validation
            for qt in QUERY_TYPES:
                if qt in result:
                    return qt
                    
            return "general"
        except Exception as e:
            logger.error(f"Failed to classify query: {e}")
            return "general"

query_classifier = QueryClassifier()
