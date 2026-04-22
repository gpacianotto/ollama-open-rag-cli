"""
Cliente para a API do Ollama (embeddings e geração de texto).
"""

import requests
import json
from typing import List, Generator
from config import OLLAMA_BASE_URL, LLM_MODEL, EMBED_MODEL


class OllamaError(Exception):
    pass


def _check_ollama() -> None:
    """Verifica se o Ollama está rodando."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise OllamaError(
            "❌ Não foi possível conectar ao Ollama.\n"
            "   Certifique-se de que o Ollama está rodando: https://ollama.com"
        )
    except Exception as e:
        raise OllamaError(f"❌ Erro ao verificar Ollama: {e}")


def get_embedding(text: str) -> List[float]:
    """Gera embedding para um texto usando nomic-embed-text."""
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": text},
            timeout=60,
        )
        resp.raise_for_status()

        length = len(resp.json().get("embeddings", []))

        if length > 1:
            print("embedding length: ", length)

        return resp.json()["embeddings"][0]
    except requests.exceptions.ConnectionError:
        raise OllamaError("❌ Ollama offline. Inicie o Ollama antes de usar a aplicação.")
    except (KeyError, IndexError, TypeError):
        raise OllamaError(f"❌ Resposta inesperada do Ollama ao gerar embedding: {resp.text}")


def generate_response(prompt: str, system: str = "") -> Generator[str, None, None]:
    """
    Gera resposta via streaming usando deepseek-r1:8b.
    Yield de cada fragmento de texto recebido.
    """
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": True,
    }
    if system:
        payload["system"] = system

    try:
        with requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=300,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        yield chunk["response"]
                    if chunk.get("done"):
                        break
    except requests.exceptions.ConnectionError:
        raise OllamaError("❌ Ollama offline durante a geração de resposta.")
    except Exception as e:
        raise OllamaError(f"❌ Erro ao gerar resposta: {e}")
