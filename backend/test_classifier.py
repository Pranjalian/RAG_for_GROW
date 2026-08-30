import asyncio
from app.rag.query_classifier import query_classifier

async def test():
    from app.config import settings
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.GROK_API_KEY, base_url=settings.GROK_API_BASE_URL)
    prompt = """You are a query classifier for a mutual fund RAG application.
Categorize the following user query into EXACTLY ONE of these types:
- fund_lookup
- fund_comparison
- nfo_query
- news_query
- category_search
- metric_search
- freshness_query
- change_query
- advice_request
- general

Output ONLY the exact string from the list above. No other text.
If unsure, output "general".

Query: what is the fund price of hdfc large cap"""
    response = await client.chat.completions.create(model=settings.GROK_MODEL_NAME, messages=[{"role": "user", "content": prompt}], temperature=0.0)
    print("RAW LLM OUTPUT:", repr(response.choices[0].message.content))

asyncio.run(test())
