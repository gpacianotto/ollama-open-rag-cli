"""
Pré-processador de arquivos.
Converte .txt e .pdf em arquivos .md, quebrando arquivos grandes em partes menores.
"""

import os
import re
from typing import Optional
from config import KNOWLEDGE_DIR, MAX_MD_FILE_SIZE, SUPPORTED_INPUT_EXTENSIONS


# ─── Extração de texto ────────────────────────────────────────────────────────

def _extract_txt(filepath: str) -> str:
    """Lê conteúdo de arquivo .txt."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não foi possível decodificar o arquivo: {filepath}")


def _extract_pdf(filepath: str) -> str:
    """Extrai texto de arquivo .pdf usando pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "❌ pdfplumber não instalado.\n"
            "   Execute: pip install pdfplumber"
        )

    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                text_parts.append(f"<!-- Página {page_num} -->\n{text}")

    return "\n\n".join(text_parts)


def _clean_text(text: str) -> str:
    """Limpeza básica do texto extraído."""
    # Remove múltiplas linhas em branco
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove espaços no fim das linhas
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def _text_to_markdown(text: str, title: str) -> str:
    """Converte texto puro para markdown simples."""
    lines = text.split("\n")
    md_lines = [f"# {title}\n"]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            md_lines.append("")
            continue
        # Tenta detectar títulos simples (linha curta em maiúsculas ou seguida de linha em branco)
        if len(stripped) < 80 and stripped.isupper() and len(stripped) > 3:
            md_lines.append(f"\n## {stripped.title()}\n")
        else:
            md_lines.append(stripped)

    return "\n".join(md_lines)


# ─── Chunking de arquivos .md ─────────────────────────────────────────────────

def _split_markdown_content(content: str, max_size: int = MAX_MD_FILE_SIZE) -> list[str]:
    """
    Divide conteúdo markdown em partes menores,
    respeitando quebras de seção (headings).
    """
    if len(content) <= max_size:
        return [content]

    parts = []
    current = ""
    lines = content.split("\n")

    for line in lines:
        # Novo heading de nível 1 ou 2 → nova parte (se já tem conteúdo)
        if line.startswith("# ") or line.startswith("## "):
            if current.strip() and len(current) + len(line) > max_size:
                parts.append(current.strip())
                current = line + "\n"
                continue
        current += line + "\n"

        # Se ultrapassou o limite, força quebra na próxima linha em branco
        if len(current) >= max_size:
            # Tenta quebrar em parágrafo
            last_break = current.rfind("\n\n")
            if last_break > max_size // 2:
                parts.append(current[:last_break].strip())
                current = current[last_break:].strip() + "\n"
            else:
                parts.append(current.strip())
                current = ""

    if current.strip():
        parts.append(current.strip())

    return parts


# ─── Processamento principal ──────────────────────────────────────────────────

def preprocess_knowledge(knowledge_name: str) -> None:
    """
    Processa todos os arquivos .txt e .pdf de uma subpasta de conhecimento,
    convertendo-os para .md. Arquivos grandes são quebrados em partes numeradas.

    Args:
        knowledge_name: Nome da subpasta em ./knowledge
    """
    folder = os.path.join(KNOWLEDGE_DIR, knowledge_name)

    if not os.path.isdir(folder):
        print(f"❌ Pasta não encontrada: {folder}")
        print(f"   Crie a pasta e adicione seus arquivos antes de pré-processar.")
        return

    # Busca arquivos suportados
    files_to_process = []
    for fname in os.listdir(folder):
        ext = os.path.splitext(fname)[1].lower()
        if ext in SUPPORTED_INPUT_EXTENSIONS:
            files_to_process.append(os.path.join(folder, fname))

    if not files_to_process:
        print(f"⚠️  Nenhum arquivo {SUPPORTED_INPUT_EXTENSIONS} encontrado em: {folder}")
        return

    print(f"\n🔄 Pré-processando {len(files_to_process)} arquivo(s) em '{knowledge_name}'...\n")

    total_md_created = 0

    for filepath in sorted(files_to_process):
        fname = os.path.basename(filepath)
        ext = os.path.splitext(fname)[1].lower()
        base_name = os.path.splitext(fname)[0]

        print(f"  📄 Processando: {fname}")

        try:
            # Extrai texto conforme o tipo
            if ext == ".txt":
                raw_text = _extract_txt(filepath)
            elif ext == ".pdf":
                raw_text = _extract_pdf(filepath)
            else:
                print(f"     ⚠️  Extensão não suportada: {ext}")
                continue

            raw_text = _clean_text(raw_text)

            if not raw_text.strip():
                print(f"     ⚠️  Arquivo vazio ou sem texto extraível.")
                continue

            # Converte para markdown
            md_content = _text_to_markdown(raw_text, title=base_name.replace("_", " ").replace("-", " ").title())

            # Quebra se necessário
            parts = _split_markdown_content(md_content)

            if len(parts) == 1:
                out_path = os.path.join(folder, f"{base_name}.md")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(parts[0])
                print(f"     ✅ Criado: {base_name}.md ({len(parts[0])} chars)")
                total_md_created += 1
            else:
                for i, part in enumerate(parts, 1):
                    out_path = os.path.join(folder, f"{base_name}_parte{i:02d}.md")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(part)
                    total_md_created += 1
                print(f"     ✅ Criado em {len(parts)} partes: {base_name}_parte01.md ... {base_name}_parte{len(parts):02d}.md")

        except Exception as e:
            print(f"     ❌ Erro ao processar {fname}: {e}")

    print(f"\n✅ Pré-processamento concluído! {total_md_created} arquivo(s) .md criado(s).")
    print(f"   Agora execute: python main.py index --knowledge {knowledge_name}")
