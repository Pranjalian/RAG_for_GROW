import json
from typing import Dict, Any, List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Chunker:
    """
    Handles chunking of extracted JSON data based on the source type.
    Architecture reference: §3.3 (Content Chunking)
    """

    def __init__(self):
        # Setup the recursive character text splitter for AMC pages
        # Token-based chunking could use a tiktoken length function, but character-based is sufficient for now.
        # We assume 1 token ~ 4 characters, so 800 tokens ~ 3200 chars, 100 overlap ~ 400 chars.
        self.amc_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3200,
            chunk_overlap=400,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def chunk_data(self, source_type: str, extracted_data: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Takes extracted data and returns a tuple of (chunks, metadatas).
        """
        if not extracted_data:
            return [], []

        if source_type == "mutual_fund":
            return self._chunk_mutual_fund(extracted_data)
        elif source_type == "amc":
            return self._chunk_amc(extracted_data)
        elif source_type == "nfo":
            return self._chunk_nfo(extracted_data)
        elif source_type == "market_news":
            return self._chunk_market_news(extracted_data)
        elif source_type == "filter":
            return self._chunk_filter(extracted_data)
        else:
            return self._chunk_generic(extracted_data)

    def _chunk_mutual_fund(self, data: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Single-Document Textification."""
        # Convert the entire data dictionary into a readable text format
        text_parts = []
        for key, value in data.items():
            if value is not None and value != "":
                if isinstance(value, dict):
                    val_str = ", ".join(f"{k}: {v}" for k, v in value.items())
                    text_parts.append(f"{key.replace('_', ' ').title()}: {val_str}")
                elif isinstance(value, list):
                    val_str = ", ".join(str(v) for v in value)
                    text_parts.append(f"{key.replace('_', ' ').title()}: {val_str}")
                else:
                    text_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        chunk = "\n".join(text_parts)
        
        # We can extract some key metadata for the chunk
        metadata = {
            "fund_name": data.get("fund_name", ""),
            "category": data.get("category", ""),
            "amc": data.get("amc", "")
        }
        return [chunk], [metadata]

    def _chunk_amc(self, data: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Recursive text splitter."""
        # Extract the main text content, ignoring lists for now or serializing them
        text_content = json.dumps(data, indent=2, default=str)
        chunks = self.amc_splitter.split_text(text_content)
        metadatas = [{"amc_name": data.get("amc_name", "")} for _ in chunks]
        return chunks, metadatas

    def _chunk_nfo(self, data: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Per-NFO item chunking."""
        chunks = []
        metadatas = []
        
        # Assuming data contains a list of NFOs under a key like 'nfos'
        nfos = data.get("nfos_listed", data.get("nfos", []))
        if not isinstance(nfos, list):
            nfos = [data] # Fallback if single object
            
        for nfo in nfos:
            text_parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in nfo.items() if v]
            chunks.append("\n".join(text_parts))
            metadatas.append({
                "nfo_name": nfo.get("nfo_name", ""),
                "amc": nfo.get("amc", "")
            })
            
        return chunks, metadatas

    def _chunk_market_news(self, data: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Per-article chunking."""
        chunks = []
        metadatas = []
        
        # Assuming data contains a list of articles under 'articles' or similar
        articles = data.get("articles", [])
        if not isinstance(articles, list):
            articles = [data]
            
        for article in articles:
            text_parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in article.items() if v]
            chunks.append("\n".join(text_parts))
            metadatas.append({
                "title": article.get("title", ""),
                "published_at": article.get("published_at", "")
            })
            
        return chunks, metadatas

    def _chunk_filter(self, data: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Generic chunking for filter pages."""
        text_content = json.dumps(data, indent=2, default=str)
        chunks = self.amc_splitter.split_text(text_content)
        metadatas = [{} for _ in chunks]
        return chunks, metadatas

    def _chunk_generic(self, data: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Fallback chunking."""
        text_content = json.dumps(data, indent=2, default=str)
        chunks = self.amc_splitter.split_text(text_content)
        metadatas = [{} for _ in chunks]
        return chunks, metadatas

chunker = Chunker()
