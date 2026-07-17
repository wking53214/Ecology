import os
import json
from datetime import datetime

def parse_file(file_path, output_dir="corpus"):
    """Detects file type and routes parsing accordingly."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(file_path):
        print(f"[System] Target file '{file_path}' not found.")
        return

    with open(file_path, 'rb') as f:
        header = f.read(5)

    if header.startswith(b'%PDF-'):
        parse_pdf(file_path, output_dir)
    else:
        parse_json(file_path, output_dir)

def parse_pdf(pdf_path, output_dir):
    """Extracts text from PDF pages and formats into block-delimited markdown."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("[System] Error: 'pypdf' package required for PDF processing. Run: pip install pypdf")
        return

    reader = PdfReader(pdf_path)
    markdown_lines = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            markdown_lines.append(f"**PDF-PAGE-{i+1}**: {text.strip()}\n")

    processed_content = "\n\n".join(markdown_lines)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filepath = os.path.join(output_dir, f"{base_name}_corpus.md")

    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(processed_content)

    print(f"[System] Successfully converted PDF '{pdf_path}' into '{output_filepath}'.")

def parse_json(json_path, output_dir):
    """Parses standard JSON chat export structures."""
    data = None
    for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
        try:
            with open(json_path, 'r', encoding=enc) as f:
                content_str = f.read().strip()
                if not content_str:
                    print(f"[System] Error: '{json_path}' is empty.")
                    return
                data = json.loads(content_str)
            break
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError as e:
            print(f"[System] JSON syntax error in '{json_path}': {e}")
            return

    if data is None:
        print(f"[System] Failed to decode '{json_path}' using standard encodings.")
        return

    messages = data if isinstance(data, list) else data.get('messages', [])
    markdown_lines = []
    for msg in messages:
        role = msg.get('role', 'unknown').upper()
        content = msg.get('content', '').strip()
        if content:
            markdown_lines.append(f"**{role}**: {content}\n")

    processed_content = "\n\n".join(markdown_lines)
    base_name = os.path.splitext(os.path.basename(json_path))[0]
    output_filepath = os.path.join(output_dir, f"{base_name}_corpus.md")

    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(processed_content)

    print(f"[System] Successfully converted JSON '{json_path}' into '{output_filepath}'.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 preprocess.py <path_to_file>")
    else:
        parse_file(sys.argv[1])
