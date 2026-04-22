"""
Configurações centrais da aplicação RAG CLI.
Ajuste as variáveis abaixo conforme necessário.
"""

# ─── Modelos Ollama ───────────────────────────────────────────────────────────
LLM_MODEL = "deepseek-r1:8b"
# EMBED_MODEL = "nomic-embed-text"
EMBED_MODEL = "nomic-embed-text-v2-moe:latest"
OLLAMA_BASE_URL = "http://localhost:11434"

# ─── Caminhos ─────────────────────────────────────────────────────────────────
KNOWLEDGE_DIR = "./knowledge"
VECTOR_STORE_DIR = "./vector_store"

# ─── Chunking ─────────────────────────────────────────────────────────────────
# Tamanho máximo de cada chunk em caracteres (para quebrar arquivos grandes)
CHUNK_SIZE = 500
# Sobreposição entre chunks para manter contexto
CHUNK_OVERLAP = 100
# Tamanho máximo de arquivo .md antes de quebrar (em caracteres)
MAX_MD_FILE_SIZE = 20000

# ─── RAG ──────────────────────────────────────────────────────────────────────
# Número de chunks mais relevantes a recuperar
TOP_K = 10

# ─── Preprocessador ───────────────────────────────────────────────────────────
# Extensões que o preprocessador converte para .md
SUPPORTED_INPUT_EXTENSIONS = [".txt", ".pdf"]
