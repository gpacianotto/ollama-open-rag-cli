"""
Carregamento e chunking de arquivos .md para indexação.
"""

import os
from typing import List, Dict
from config import KNOWLEDGE_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def _chunk_text(text: str, source: str) -> List[Dict]:
    """
    Divide texto em chunks com sobreposição.
    Tenta quebrar em parágrafos antes de cortar por tamanho.
    """
    chunks = []
    paragraphs = text.split("\n\n")
    current = ""
    chunk_index = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Se o parágrafo sozinho já é grande demais, quebra por tamanho
        if len(para) > CHUNK_SIZE:
            # Salva o que estava acumulado primeiro
            if current.strip():
                chunks.append({"text": current.strip(), "source": source, "chunk_index": chunk_index})
                chunk_index += 1
                current = ""

            # Quebra o parágrafo grande em sub-chunks
            start = 0
            while start < len(para):
                end = start + CHUNK_SIZE
                sub = para[start:end]
                chunks.append({"text": sub.strip(), "source": source, "chunk_index": chunk_index})
                chunk_index += 1
                start = end - CHUNK_OVERLAP
            continue

        # Adiciona ao chunk atual
        if len(current) + len(para) + 2 > CHUNK_SIZE:
            if current.strip():
                chunks.append({"text": current.strip(), "source": source, "chunk_index": chunk_index})
                chunk_index += 1
                # Mantém sobreposição
                words = current.split()
                overlap_words = words[-max(1, CHUNK_OVERLAP // 6):]
                current = " ".join(overlap_words) + "\n\n"
        current += para + "\n\n"

    if current.strip():
        chunks.append({"text": current.strip(), "source": source, "chunk_index": chunk_index})

    return chunks


def load_knowledge_chunks(knowledge_name: str) -> List[Dict]:
    """
    Carrega todos os arquivos .md de uma subpasta de conhecimento
    e retorna seus chunks.

    Args:
        knowledge_name: Nome da subpasta (ex: "mecanica")

    Returns:
        Lista de chunks prontos para indexação
    """
    folder = os.path.join(KNOWLEDGE_DIR, knowledge_name)

    if not os.path.isdir(folder):
        raise FileNotFoundError(
            f"❌ Pasta de conhecimento não encontrada: {folder}\n"
            f"   Crie a pasta e adicione arquivos .md antes de indexar."
        )

    md_files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".md")
    ]

    if not md_files:
        raise FileNotFoundError(
            f"❌ Nenhum arquivo .md encontrado em: {folder}\n"
            f"   Use 'python main.py preprocess --knowledge {knowledge_name}' para converter arquivos."
        )

    all_chunks = []
    for filepath in sorted(md_files):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            if content.strip():
                rel_path = os.path.relpath(filepath, KNOWLEDGE_DIR)
                chunks = _chunk_text(content, source=rel_path)
                all_chunks.extend(chunks)
        except Exception as e:
            print(f"   ⚠️  Erro ao ler {filepath}: {e}")

    return all_chunks


def list_knowledge_folders() -> List[str]:
    """Lista as subpastas disponíveis em ./knowledge."""
    if not os.path.isdir(KNOWLEDGE_DIR):
        return []
    return [
        d for d in os.listdir(KNOWLEDGE_DIR)
        if os.path.isdir(os.path.join(KNOWLEDGE_DIR, d))
    ]
