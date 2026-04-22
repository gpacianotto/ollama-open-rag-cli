"""
Pipeline RAG: recupera contexto relevante e gera resposta com o LLM.
"""

from typing import List, Dict
from vector_store import query_documents
from ollama_client import generate_response, OllamaError


SYSTEM_PROMPT = """Você é um assistente especializado que responde perguntas com base em documentos de conhecimento fornecidos.

Instruções:
- Responda APENAS com base no contexto fornecido.
- Se a informação não estiver no contexto, diga claramente que não encontrou nos documentos.
- Cite as fontes dos documentos quando relevante (nome do arquivo).
- Responda sempre em português, a menos que a pergunta seja em outro idioma.
- Seja objetivo e preciso."""


def build_prompt(question: str, context_chunks: List[Dict]) -> str:
    """Monta o prompt com contexto para o LLM."""
    context_parts = []
    seen_sources = set()

    for i, chunk in enumerate(context_chunks, 1):
        source = chunk.get("source", "desconhecido")
        text = chunk["text"]
        context_parts.append(f"[Trecho {i} - Fonte: {source}]\n{text}")
        seen_sources.add(source)

    context_str = "\n\n---\n\n".join(context_parts)

    return f"""Com base nos seguintes trechos de documentos:

{context_str}

---

Pergunta: {question}

Resposta:"""


def ask_knowledge(question: str, knowledge_name: str) -> None:
    """
    Executa o pipeline RAG completo para uma pergunta sobre um knowledge.
    Imprime a resposta via streaming.

    Args:
        question: Pergunta do usuário
        knowledge_name: Nome da subpasta de conhecimento
    """
    print(f"\n🔍 Buscando contexto em '{knowledge_name}'...")

    try:
        chunks = query_documents(namespace=knowledge_name, question=question)
    except ValueError as e:
        print(str(e))
        return

    if not chunks:
        print("❌ Nenhum contexto relevante encontrado.")
        return

    print(f"   📄 {len(chunks)} trecho(s) relevante(s) encontrado(s).\n")

    # Mostra fontes consultadas
    sources = list({c["source"] for c in chunks})
    print(f"📚 Fontes consultadas: {', '.join(sources)}\n")
    print("─" * 60)
    print("💬 Resposta:\n")

    prompt = build_prompt(question, chunks)

    try:
        for token in generate_response(prompt=prompt, system=SYSTEM_PROMPT):
            print(token, end="", flush=True)
        print("\n" + "─" * 60)
    except OllamaError as e:
        print(f"\n{e}")
