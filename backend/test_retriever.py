import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rag.retriever import retriever

async def main():
    docs = await retriever.retrieve('who is the fund manager of hdfc flexi cap', 'fund_lookup')
    for doc in docs:
        print('---')
        print(doc)

asyncio.run(main())
