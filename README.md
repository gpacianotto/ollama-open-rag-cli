# OLLAMA OPEN RAG CLI

## English

OLLAMA OPEN RAG CLI is a small command-line tool for question answering over your own documents using Retrieval-Augmented Generation with Ollama and ChromaDB. It is designed to be easy to run locally, easy to extend, and suitable for open-source reuse.

### Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- Ollama models pulled locally:
  ```bash
  ollama pull deepseek-r1:8b
  ollama pull nomic-embed-text-v2-moe:latest
  ```

### Install

```bash
pip install -r requirements.txt
```

Start Ollama if it is not already running:

```bash
ollama serve
```

### Project Layout

```
rag-ollama/
├── main.py
├── config.py
├── ollama_client.py
├── vector_store.py
├── document_loader.py
├── rag.py
├── preprocessor.py
├── requirements.txt
├── knowledge/
└── vector_store/
```

The application creates `knowledge/` and `vector_store/` automatically when you run any CLI command. Both directories are ignored by git so you can keep local content and local indexes out of the repository.

### Commands

Ask questions about a knowledge base:

```bash
python main.py ask --question "How does a combustion engine work?" --knowledge mecanica
python main.py ask -q "How does a combustion engine work?" -k mecanica
```

Index a knowledge base manually:

```bash
python main.py index --knowledge mecanica
python main.py index --knowledge mecanica --reindex
```

Preprocess `.txt` and `.pdf` files into `.md` files:

```bash
python main.py preprocess --knowledge mecanica
```

List available knowledge bases:

```bash
python main.py list
```

Reset the local vector store:

```bash
python main.py reset
```

### Configuration

Edit `config.py` if you want to change the default model names or chunking behavior.

| Variable | Default | Purpose |
|---|---|---|
| `LLM_MODEL` | `deepseek-r1:8b` | Response generation model |
| `EMBED_MODEL` | `nomic-embed-text-v2-moe:latest` | Embedding model |
| `CHUNK_SIZE` | `500` | Maximum chunk size in characters |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `MAX_MD_FILE_SIZE` | `20000` | Maximum markdown file size before splitting |
| `TOP_K` | `10` | Number of chunks retrieved per query |

### How It Works

1. Put `.md` files inside a subfolder of `knowledge/`.
2. Run `python main.py index --knowledge <folder>` to build the local index.
3. Ask questions with `python main.py ask --question "..." --knowledge <folder>`.

If you have `.txt` or `.pdf` files, run the preprocess command first to convert them into markdown.

## Português

O OLLAMA OPEN RAG CLI é uma ferramenta de linha de comando para consultar seus próprios documentos usando Retrieval-Augmented Generation com Ollama e ChromaDB. O projeto foi pensado para rodar localmente com simplicidade, ser fácil de adaptar e servir bem como base para uso em open source.

### Requisitos

- Python 3.10+
- [Ollama](https://ollama.com) instalado e em execução
- Modelos Ollama baixados localmente:
  ```bash
  ollama pull deepseek-r1:8b
  ollama pull nomic-embed-text-v2-moe:latest
  ```

### Instalação

```bash
pip install -r requirements.txt
```

Se o Ollama ainda não estiver rodando, inicie-o com:

```bash
ollama serve
```

### Estrutura do projeto

```
rag-ollama/
├── main.py
├── config.py
├── ollama_client.py
├── vector_store.py
├── document_loader.py
├── rag.py
├── preprocessor.py
├── requirements.txt
├── knowledge/
└── vector_store/
```

A aplicação cria automaticamente as pastas `knowledge/` e `vector_store/` ao executar qualquer comando da CLI. Ambas ficam ignoradas pelo git para que documentos locais e índices locais não sejam versionados.

### Comandos

Perguntar sobre um conhecimento:

```bash
python main.py ask --question "Como funciona um motor a combustão?" --knowledge mecanica
python main.py ask -q "Como funciona um motor a combustão?" -k mecanica
```

Indexar um conhecimento manualmente:

```bash
python main.py index --knowledge mecanica
python main.py index --knowledge mecanica --reindex
```

Pré-processar arquivos `.txt` e `.pdf` para `.md`:

```bash
python main.py preprocess --knowledge mecanica
```

Listar os conhecimentos disponíveis:

```bash
python main.py list
```

Resetar o vector store local:

```bash
python main.py reset
```

### Configuração

Edite `config.py` se quiser alterar os modelos padrão ou o comportamento de chunking.

| Variável | Padrão | Finalidade |
|---|---|---|
| `LLM_MODEL` | `deepseek-r1:8b` | Modelo de geração de respostas |
| `EMBED_MODEL` | `nomic-embed-text-v2-moe:latest` | Modelo de embeddings |
| `CHUNK_SIZE` | `500` | Tamanho máximo de cada chunk em caracteres |
| `CHUNK_OVERLAP` | `100` | Sobreposição entre chunks |
| `MAX_MD_FILE_SIZE` | `20000` | Tamanho máximo de um arquivo markdown antes de quebrar |
| `TOP_K` | `10` | Quantidade de chunks recuperados por consulta |

### Como funciona

1. Coloque arquivos `.md` dentro de uma subpasta em `knowledge/`.
2. Execute `python main.py index --knowledge <pasta>` para criar o índice local.
3. Faça perguntas com `python main.py ask --question "..." --knowledge <pasta>`.

Se você tiver arquivos `.txt` ou `.pdf`, execute primeiro o comando de preprocessamento para convertê-los em markdown.
