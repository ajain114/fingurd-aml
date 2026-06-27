"""
Knowledge Base Loader — loads AML typology documents into ChromaDB.
Mirrors Amazon Bedrock Knowledge Base with vector embeddings.

In production (Bedrock):
  - Documents stored in S3
  - Embeddings via Amazon Titan Embeddings v2
  - Vector store: OpenSearch Serverless or Aurora pgvector
  - Chunking and sync managed by Bedrock Knowledge Base API

Here (demo):
  - Documents as local .txt files
  - Embeddings via ChromaDB default (all-MiniLM-L6-v2 ONNX, no API key needed)
  - In-memory ChromaDB (ephemeral, re-initialised on app start)
"""

import os
import chromadb
from chromadb.utils import embedding_functions

_TYPOLOGIES_DIR = os.path.join(os.path.dirname(__file__), "typologies")

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.Client()  # in-memory
    ef = embedding_functions.DefaultEmbeddingFunction()
    _collection = _client.create_collection(
        name="aml_typologies",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # Load all typology documents
    docs, ids, metadatas = [], [], []
    for fname in os.listdir(_TYPOLOGIES_DIR):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(_TYPOLOGIES_DIR, fname)
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Chunk into paragraphs (simple chunking strategy)
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 80]
        for i, para in enumerate(paragraphs):
            chunk_id = f"{fname}_{i}"
            docs.append(para)
            ids.append(chunk_id)
            metadatas.append({
                "source": fname,
                "typology": fname.replace(".txt", "").replace("_", " ").title(),
                "chunk_index": i,
            })

    if docs:
        _collection.add(documents=docs, ids=ids, metadatas=metadatas)

    return _collection


def search_typologies(query: str, n_results: int = 3) -> dict:
    """
    Semantic search over AML typology knowledge base.
    Returns most relevant typology chunks with source attribution.

    Bedrock equivalent: RetrieveAndGenerate API on a Bedrock Knowledge Base
    """
    collection = _get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "content": doc,
            "typology": meta.get("typology", "Unknown"),
            "source": meta.get("source", ""),
            "relevance_score": round(1 - dist, 3),  # cosine similarity
        })

    return {
        "query": query,
        "results": hits,
        "total_chunks_searched": collection.count(),
    }


def get_kb_stats() -> dict:
    collection = _get_collection()
    return {"total_chunks": collection.count(), "collection_name": "aml_typologies"}
