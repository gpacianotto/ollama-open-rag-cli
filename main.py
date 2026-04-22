"""
RAG CLI - Linha de comando para consultas com RAG usando Ollama.

Uso:
    python main.py ask        --question "..." --knowledge mecanica
    python main.py index      --knowledge mecanica [--reindex]
    python main.py preprocess --knowledge mecanica
    python main.py list
    python main.py reset
"""

import sys
import os
import argparse
import shutil

# Garante que o diretório do script está no path para imports relativos funcionarem
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import KNOWLEDGE_DIR, VECTOR_STORE_DIR
from document_loader import load_knowledge_chunks, list_knowledge_folders
from vector_store import index_documents, collection_exists, delete_collection
from rag import ask_knowledge
from preprocessor import preprocess_knowledge


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _banner():
    print("""
╔══════════════════════════════════════════╗
║          RAG CLI  •  Ollama + DeepSeek   ║
╚══════════════════════════════════════════╝
""")


def _require_knowledge_arg(args) -> str:
    """Valida e retorna o argumento --knowledge."""
    if not args.knowledge:
        print("❌ Argumento obrigatório: --knowledge <nome>")
        print("   Use 'python main.py list' para ver os conhecimentos disponíveis.")
        sys.exit(1)
    return args.knowledge.strip().lower()


def _ensure_workspace_dirs() -> None:
    """Garante que os diretórios raiz usados pela CLI existam."""
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)


# ─── Comandos ─────────────────────────────────────────────────────────────────

def cmd_ask(args):
    """Pergunta com RAG sobre um conhecimento específico."""
    if not args.question:
        print("❌ Argumento obrigatório: --question \"sua pergunta\"")
        sys.exit(1)

    knowledge = _require_knowledge_arg(args)

    # Verifica se já foi indexado
    if not collection_exists(knowledge):
        print(f"⚠️  O conhecimento '{knowledge}' ainda não foi indexado.")
        print(f"   Indexando agora...\n")
        cmd_index_knowledge(knowledge, reindex=False)

    ask_knowledge(question=args.question, knowledge_name=knowledge)


def cmd_index(args):
    """Indexa (ou re-indexa) um conhecimento."""
    knowledge = _require_knowledge_arg(args)
    reindex = getattr(args, "reindex", False)
    cmd_index_knowledge(knowledge, reindex=reindex)


def cmd_index_knowledge(knowledge_name: str, reindex: bool = False):
    """Lógica de indexação (reutilizável internamente)."""
    if collection_exists(knowledge_name) and not reindex:
        print(f"ℹ️  Conhecimento '{knowledge_name}' já está indexado.")
        print(f"   Use --reindex para forçar a re-indexação.")
        return

    if reindex:
        print(f"🗑️  Removendo índice anterior de '{knowledge_name}'...")
        delete_collection(knowledge_name)

    print(f"\n📂 Carregando documentos de '{knowledge_name}'...")
    try:
        chunks = load_knowledge_chunks(knowledge_name)
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)

    print(f"   📄 {len(chunks)} chunk(s) carregado(s).")
    print(f"\n⚙️  Gerando embeddings e indexando...")
    index_documents(namespace=knowledge_name, chunks=chunks)
    print(f"\n✅ Conhecimento '{knowledge_name}' indexado com sucesso!")


def cmd_preprocess(args):
    """Pré-processa arquivos .txt/.pdf → .md."""
    knowledge = _require_knowledge_arg(args)
    preprocess_knowledge(knowledge)


def cmd_list(args):
    """Lista conhecimentos disponíveis e seus status."""
    folders = list_knowledge_folders()

    if not folders:
        print(f"📂 Nenhuma subpasta encontrada em '{KNOWLEDGE_DIR}'.")
        print(f"   Crie subpastas com arquivos .md para começar.")
        return

    print(f"\n📚 Conhecimentos disponíveis em '{KNOWLEDGE_DIR}':\n")

    for folder in sorted(folders):
        folder_path = os.path.join(KNOWLEDGE_DIR, folder)
        md_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".md")]
        indexed = collection_exists(folder)
        status = "✅ indexado" if indexed else "⚠️  não indexado"
        print(f"  • {folder:<25} {len(md_files):>3} arquivo(s) .md   [{status}]")

    print(f"\n💡 Para indexar: python main.py index --knowledge <nome>")
    print(f"💡 Para perguntar: python main.py ask --question \"...\" --knowledge <nome>")


def cmd_reset(args):
    """Remove todo o vector store para resetar os índices persistidos."""
    if not os.path.isdir(VECTOR_STORE_DIR):
        print(f"ℹ️  Pasta de índices não encontrada: '{VECTOR_STORE_DIR}'")
        print("   Nada para resetar.")
        return

    try:
        shutil.rmtree(VECTOR_STORE_DIR)
        print(f"🗑️  Pasta '{VECTOR_STORE_DIR}' removida com sucesso.")
        print("   ✅ Índices resetados. Eles serão recriados automaticamente na próxima indexação.")
    except Exception as e:
        print(f"❌ Falha ao remover '{VECTOR_STORE_DIR}': {e}")
        sys.exit(1)


# ─── Parser principal ─────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="RAG CLI — Consultas inteligentes com Ollama + DeepSeek",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py ask --question "Como funciona um motor de combustão?" --knowledge mecanica
  python main.py index --knowledge mecanica
  python main.py index --knowledge mecanica --reindex
  python main.py preprocess --knowledge mecanica
  python main.py list
  python main.py reset
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # ── ask ──────────────────────────────────────────────────────────────────
    ask_parser = subparsers.add_parser(
        "ask",
        help="Faz uma pergunta usando RAG sobre um conhecimento",
    )
    ask_parser.add_argument(
        "--question", "-q",
        required=True,
        help="Pergunta a ser respondida",
    )
    ask_parser.add_argument(
        "--knowledge", "-k",
        required=True,
        help="Nome da subpasta de conhecimento (ex: mecanica)",
    )

    # ── index ─────────────────────────────────────────────────────────────────
    index_parser = subparsers.add_parser(
        "index",
        help="Indexa (ou re-indexa) os documentos de um conhecimento",
    )
    index_parser.add_argument(
        "--knowledge", "-k",
        required=True,
        help="Nome da subpasta de conhecimento",
    )
    index_parser.add_argument(
        "--reindex",
        action="store_true",
        help="Força re-indexação mesmo que já indexado",
    )

    # ── preprocess ───────────────────────────────────────────────────────────
    pre_parser = subparsers.add_parser(
        "preprocess",
        help="Converte arquivos .txt/.pdf em .md (com chunking automático)",
    )
    pre_parser.add_argument(
        "--knowledge", "-k",
        required=True,
        help="Nome da subpasta de conhecimento",
    )

    # ── list ──────────────────────────────────────────────────────────────────
    subparsers.add_parser(
        "list",
        help="Lista os conhecimentos disponíveis e seus status",
    )

    # ── reset ─────────────────────────────────────────────────────────────────
    subparsers.add_parser(
        "reset",
        help="Reseta os índices removendo a pasta do vector store",
    )

    return parser


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    _banner()
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    _ensure_workspace_dirs()

    commands = {
        "ask": cmd_ask,
        "index": cmd_index,
        "preprocess": cmd_preprocess,
        "list": cmd_list,
        "reset": cmd_reset,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
