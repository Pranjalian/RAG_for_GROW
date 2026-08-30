import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)

class Embedder:
    """
    Manages ChromaDB vector store and sentence-transformers embedding model.
    """
    
    def __init__(self):
        logger.info(f"Initializing ChromaDB at {settings.CHROMA_PERSIST_DIR}")
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # We use a single collection for all data types for easier retrieval 
        # based on source_type filter.
        self.collection = self.chroma_client.get_or_create_collection(
            name="groww_funds",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_and_store(
        self, 
        source_url_id: int, 
        source_type: str, 
        chunks: List[str], 
        metadatas: List[Dict[str, Any]]
    ):
        """
        Embeds text chunks and stores them in ChromaDB.
        Assumes old chunks for this source_url_id have been deleted if it's an update.
        """
        if not chunks:
            logger.warning(f"No chunks provided for source_url_id {source_url_id}")
            return

        logger.debug(f"Encoding {len(chunks)} chunks for source_url_id {source_url_id}")
        embeddings = self.model.encode(chunks, show_progress_bar=False).tolist()

        # Generate unique IDs for chunks: e.g., "source_url_id-chunk_index"
        ids = [f"{source_url_id}-{i}" for i in range(len(chunks))]

        # Ensure all metadatas have source_url_id and source_type for filtering
        for i, meta in enumerate(metadatas):
            meta["source_url_id"] = source_url_id
            meta["source_type"] = source_type
            
            # ChromaDB metadatas cannot contain None or complex objects.
            # Convert values to strings, ints, floats, or bools.
            clean_meta = {}
            for k, v in meta.items():
                if v is None:
                    continue
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)
            metadatas[i] = clean_meta

        logger.debug(f"Adding {len(chunks)} vectors to ChromaDB")
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

    def delete_by_source(self, source_url_id: int):
        """
        Deletes all chunks associated with a specific source URL ID.
        """
        logger.debug(f"Deleting vectors for source_url_id {source_url_id}")
        self.collection.delete(
            where={"source_url_id": source_url_id}
        )

# Global singleton instance
embedder = Embedder()
