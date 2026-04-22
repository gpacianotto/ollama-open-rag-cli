"""
Gerenciamento do vector store (ChromaDB).
Cada subpasta de knowledge tem sua própria coleção isolada.
"""

import os
import hashlib
from typing import List, Dict, Tuple
import chromadb
from chromadb import Settings

from config import VECTOR_STORE_DIR, TOP_K
from ollama_client import get_embedding


def _get_client() -> chromadb.PersistentClient:
    """Retorna cliente ChromaDB persistente."""
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    return chromadb.PersistentClient(
        path=VECTOR_STORE_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def _collection_name(namespace: str) -> str:
    """Normaliza nome da coleção (ChromaDB tem restrições de caracteres)."""
    safe = namespace.replace(os.sep, "_").replace("/", "_").replace("\\", "_")
    return f"rag_{safe}"


def _doc_id(filepath: str, chunk_index: int) -> str:
    """ID único para um chunk de documento."""
    key = f"{filepath}::{chunk_index}"
    return hashlib.md5(key.encode()).hexdigest()


def index_documents(namespace: str, chunks: List[Dict]) -> None:
    """
    Indexa chunks no vector store.

    Args:
        namespace: Nome da subpasta/coleção (ex: "mecanica", "code::./projeto")
        chunks: Lista de dicts com {"text": str, "source": str, "chunk_index": int}
    """
    client = _get_client()
    col_name = _collection_name(namespace)
    collection = client.get_or_create_collection(name=col_name)

    if not chunks:
        print("   ⚠️  Nenhum chunk para indexar.")
        return

    ids, embeddings, documents, metadatas = [], [], [], []

    for i, chunk in enumerate(chunks):
        print(f"Processando chunk {i+1}/{len(chunks)}") 
        text = chunk["text"].strip()
        if not text:
            print(f"⚠️  Chunk {i} vazio, pulando.")
            continue

        doc_id = _doc_id(chunk.get("source", "unknown"), chunk.get("chunk_index", i))
        embedding = get_embedding(text)

        ids.append(doc_id)
        embeddings.append(embedding)
        documents.append(text)
        metadatas.append({"source": chunk.get("source", ""), "chunk_index": chunk.get("chunk_index", i)})

    # Upsert em lotes para evitar timeouts
    batch_size = 50
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.upsert(
            ids=ids[start:end],
            embeddings=embeddings[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    print(f"   ✅ {len(ids)} chunks indexados na coleção '{col_name}'.")


def query_documents(namespace: str, question: str, top_k: int = TOP_K) -> List[Dict]:
    """
    Busca os chunks mais relevantes para a pergunta.

    Returns:
        Lista de dicts com {"text": str, "source": str, "distance": float}
    """
    client = _get_client()
    col_name = _collection_name(namespace)

    try:
        collection = client.get_collection(name=col_name)
    except Exception:
        raise ValueError(
            f"❌ Coleção '{namespace}' não encontrada.\n"
            f"   Execute primeiro: python main.py index --knowledge {namespace}"
        )

    count = collection.count()
    if count == 0:
        raise ValueError(f"❌ A coleção '{namespace}' está vazia. Re-indexe os documentos.")

    embedding = get_embedding(question)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({"text": doc, "source": meta.get("source", ""), "distance": dist})

    return output


def collection_exists(namespace: str) -> bool:
    """Verifica se uma coleção já foi indexada."""
    client = _get_client()
    col_name = _collection_name(namespace)
    try:
        col = client.get_collection(name=col_name)
        return col.count() > 0
    except Exception:
        return False


def delete_collection(namespace: str) -> None:
    """Remove uma coleção do vector store."""
    client = _get_client()
    col_name = _collection_name(namespace)
    try:
        client.delete_collection(name=col_name)
        print(f"   🗑️  Coleção '{col_name}' removida.")
    except Exception:
        print(f"   ⚠️  Coleção '{col_name}' não existia.")
