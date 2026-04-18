import os
import hashlib
import re
from pathlib import Path

import chromadb
from app.config import settings

_client = None
_collection = None

DOCUMENTS_DIR = Path(__file__).parent / "documents"
COLLECTION_NAME = "acme_corp_docs_local"


class LocalEmbeddingFunction:
    @staticmethod
    def name() -> str:
        return "local-hash-embedding"

    def get_config(self) -> dict[str, object]:
        return {
            "name": self.name(),
            "default_space": self.default_space(),
            "supported_spaces": self.supported_spaces(),
        }

    @staticmethod
    def default_space() -> str:
        return "cosine"

    @staticmethod
    def supported_spaces() -> list[str]:
        return ["cosine", "l2", "ip"]

    def is_legacy(self) -> bool:
        return False

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in input]

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in documents]

    def embed_query(self, input: str | list[str]) -> list[float] | list[list[float]]:
        if isinstance(input, str):
            return self._embed_text(input)

        return [self._embed_text(text) for text in input]

    def _embed_text(self, text: str, dimensions: int = 256) -> list[float]:
        vector = [0.0] * dimensions
        tokens = re.findall(r"\b\w+\b", text.lower())

        for token in tokens:
            bucket = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % dimensions
            vector[bucket] += 1.0

        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0:
            return vector

        return [value / norm for value in vector]


_embedding_function = LocalEmbeddingFunction()

def get_chroma_client() -> chromadb.Client:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
    return _client

def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Acme Corp internal documents"},
            embedding_function=_embedding_function,
        )
        
    return _collection

def ingest_documents():
    collection = get_collection()
    if collection.count() > 0:
        return collection
    
    doc_dir = DOCUMENTS_DIR
    if not doc_dir.exists():
        raise FileNotFoundError(f"Documents directory not found: {doc_dir}")
    
    for filepath in sorted(doc_dir.glob("*.txt")):
        content = filepath.read_text(encoding="utf-8")
        chunks = _chunk_text(content, chunk_size=500, overlap=50)

        for i, chunk in enumerate(chunks):
            doc_id = f"{filepath.stem}_chunk_{i}"
            collection.add(
                ids = [doc_id],
                documents = [chunk],
                metadatas = [{"source": filepath.name, "chunk_index": i}])
    return collection

def retrieve_context(query: str, n_results: int = 3) -> list[dict]:
    collection = get_collection()
    if collection.count() == 0:
        ingest_documents()
    results = collection.query(
        query_texts = [query],
        n_results = n_results)
    
    documents = []

    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i] if results["distances"] else None
        documents.append({
            "content": doc,
            "source": metadata.get("source"),
            "chunk_index": metadata.get("chunk_index"),
            "distance": distance
        })
    return documents

def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks