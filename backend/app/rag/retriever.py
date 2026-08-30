import logging
from typing import List, Dict, Any, Optional

from app.pipeline.embedder import embedder

logger = logging.getLogger(__name__)

class GroundedRetriever:
    """
    Retrieves grounded context from ChromaDB based on the query type.
    Reference: Architecture §9.2 and Phase 4 Implementation Plan.
    """

    async def retrieve(
        self, 
        query: str, 
        query_type: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves relevant documents. Returns a list of dicts with 'content' and 'metadata'.
        """
        logger.info(f"Retrieving context for query_type='{query_type}'")
        
        where_filter = {}
        n_results = 5
        
        # Merge explicitly passed filters (if any)
        if filters:
            where_filter.update(filters)
            
        # Adjust retrieval strategy based on query type
        if query_type == "fund_lookup":
            where_filter["source_type"] = "mutual_fund"
            n_results = 5
        elif query_type == "fund_comparison":
            where_filter["source_type"] = "mutual_fund"
            n_results = 10 # We might need more results to capture multiple funds
        elif query_type == "nfo_query":
            where_filter["source_type"] = "nfo"
            n_results = 10
        elif query_type == "news_query":
            where_filter["source_type"] = "market_news"
            n_results = 10
        elif query_type == "category_search":
            where_filter["source_type"] = "mutual_fund"
            n_results = 15
        elif query_type == "metric_search":
            where_filter["source_type"] = "mutual_fund"
            n_results = 20
        elif query_type in ["freshness_query", "change_query"]:
            # These are handled specially via DB / Snapshots, not ChromaDB
            return []
            
        # Clean up empty where_filter
        if not where_filter:
            where_filter = None
            
        query_embedding = embedder.model.encode(query, show_progress_bar=False).tolist()
        
        results = embedder.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        formatted_results = []
        if results and results['documents'] and len(results['documents']) > 0:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            
            for i in range(len(docs)):
                formatted_results.append({
                    "content": docs[i],
                    "metadata": metas[i]
                })
                
        logger.info(f"Retrieved {len(formatted_results)} documents")
        return formatted_results

retriever = GroundedRetriever()
