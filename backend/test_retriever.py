import asyncio
from app.rag.retriever import retriever

async def main():
    print("Searching ChromaDB for 'franklin india multi cap'...")
    res = await retriever.retrieve("what is the fund price of franklin india multi cap", "fund_lookup")
    for idx, doc in enumerate(res):
        print(f"\n--- Document {idx+1} ---")
        print("Metadata:", doc['metadata'])
        print("Content:", doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])

if __name__ == "__main__":
    asyncio.run(main())
