import os
import re
import json
import csv
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pypdf import PdfReader
from src.governance.registry import register_as_module

class BaseParser(ABC):
    """Abstract foundational structure governing format-specific extraction engines."""
    
    @abstractmethod
    def parse(self, file_path: str, max_words: int) -> List[Dict[str, Any]]:
        pass

class MarkdownParser(BaseParser):
    """Isolates markdown YAML attributes and partitions structural content by heading limits."""

    def extract_front_matter(self, content: str) -> tuple[Dict[str, Any], str]:
        front_matter = {}
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if match:
            raw_yaml = match.group(1)
            body = content[match.end():]
            for line in raw_yaml.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    front_matter[k.strip()] = v.strip().strip('"').strip("'")
            return front_matter, body
        return front_matter, content

    def parse(self, file_path: str, max_words: int) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        front_matter, body = self.extract_front_matter(raw_content)
        source_name = os.path.basename(file_path)
        base_metadata = {**front_matter, "source": source_name}

        heading_pattern = r"(^|\n)(?P<level>#{1,6})\s+(?P<title>.+?)\n"
        matches = list(re.finditer(heading_pattern, body))
        
        if not matches:
            words = body.split()
            blocks = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
            return [{"content": b, "metadata": {**base_metadata, "section": "Body", "chunk_segment": idx}} for idx, b in enumerate(blocks)]

        chunks = []
        current_meta = {**base_metadata, "section": "Preamble"}
        
        for i, match in enumerate(matches):
            if i == 0 and match.start() > 0:
                preamble_text = body[:match.start()].strip()
                if preamble_text:
                    chunks.append({"content": preamble_text, "metadata": current_meta.copy()})

            start_idx = match.end()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            section_content = body[start_idx:end_idx].strip()
            
            section_meta = {**base_metadata, "section": match.group("title").strip()}

            if section_content:
                s_words = section_content.split()
                if len(s_words) > max_words:
                    sub_blocks = [" ".join(s_words[i:i + max_words]) for i in range(0, len(s_words), max_words)]
                    for idx, sub_txt in enumerate(sub_blocks):
                        chunks.append({"content": sub_txt, "metadata": {**section_meta, "chunk_segment": idx}})
                else:
                    chunks.append({"content": section_content, "metadata": section_meta})

        return chunks

class TextParser(BaseParser):
    """Processes unformatted plain text files utilizing systematic word-window constraints."""

    def parse(self, file_path: str, max_words: int) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        words = content.split()
        blocks = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
        source = os.path.basename(file_path)
        
        return [{"content": b, "metadata": {"source": source, "section": "Body", "chunk_segment": idx}} for idx, b in enumerate(blocks)]

class JsonParser(BaseParser):
    """Flattens structured configuration assets and array entities into clean text lines."""

    def parse(self, file_path: str, max_words: int) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        source = os.path.basename(file_path)
        chunks = []
        
        if isinstance(data, list):
            for idx, item in enumerate(data):
                content_str = json.dumps(item) if isinstance(item, (dict, list)) else str(item)
                chunks.append({"content": content_str, "metadata": {"source": source, "section": "JSON_List", "item_index": idx}})
        elif isinstance(data, dict):
            for key, val in data.items():
                content_str = f"{key}: {json.dumps(val) if isinstance(val, (dict, list)) else str(val)}"
                chunks.append({"content": content_str, "metadata": {"source": source, "section": f"JSON_Key_{key}"}})
        else:
            chunks.append({"content": str(data), "metadata": {"source": source, "section": "JSON_Primitive"}})
            
        return chunks

class CsvParser(BaseParser):
    """Transforms row segments into descriptive column-value metadata-mapped strings."""

    def parse(self, file_path: str, max_words: int) -> List[Dict[str, Any]]:
        chunks = []
        source = os.path.basename(file_path)
        
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                row_str = "\n".join(f"{k}: {v}" for k, v in row.items())
                chunks.append({"content": row_str, "metadata": {"source": source, "section": "CSV_Row", "row_index": idx}})
                
        return chunks

class PdfParser(BaseParser):
    """Unpacks binary PDF pages, extracts textual strings, and splits data into standardized chunks."""

    def parse(self, file_path: str, max_words: int) -> List[Dict[str, Any]]:
        chunks = []
        source = os.path.basename(file_path)
        
        reader = PdfReader(file_path)
        
        for page_idx, page in enumerate(reader.pages):
            text_content = page.extract_text()
            if not text_content:
                continue
                
            p_words = text_content.split()
            blocks = [" ".join(p_words[i:i + max_words]) for i in range(0, len(p_words), max_words)]
            
            for block_idx, block in enumerate(blocks):
                chunks.append({
                    "content": block,
                    "metadata": {
                        "source": source,
                        "section": f"Page_{page_idx + 1}",
                        "chunk_segment": block_idx
                    }
                })
                
        return chunks

class PythonParser(BaseParser):
    """Extracts source code components matching functional object boundaries."""

    def parse(self, file_path: str, max_words: int) -> List[Dict[str, Any]]:
        chunks = []
        source = os.path.basename(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            
        current_chunk = []
        current_words = 0
        
        for line in lines:
            line_words = len(line.split())
            # Split instantly when hitting a top-level def/class if content exists
            if (line.startswith("class ") or line.startswith("def ")) and current_chunk:
                chunks.append({
                    "content": "\n".join(current_chunk),
                    "metadata": {"source": source, "section": "Code_Block"}
                })
                current_chunk = []
                current_words = 0
                
            current_chunk.append(line)
            current_words += line_words
            
            if current_words >= max_words:
                chunks.append({
                    "content": "\n".join(current_chunk),
                    "metadata": {"source": source, "section": "Code_Segment"}
                })
                current_chunk = []
                current_words = 0
                
        if current_chunk:
            chunks.append({
                "content": "\n".join(current_chunk),
                "metadata": {"source": source, "section": "Code_Remainder"}
            })
            
        return chunks

class DiffPatchParser(BaseParser):
    """Parses structural tracking modifications using target file patch entries."""

    def parse(self, file_path: str, max_words: int) -> List[Dict[str, Any]]:
        chunks = []
        source = os.path.basename(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            
        current_chunk = []
        current_words = 0
        
        for line in lines:
            line_words = len(line.split())
            # Split instantly when hitting a new diff tracker target if content exists
            if (line.startswith("diff --git ") or line.startswith("--- ")) and current_chunk:
                chunks.append({
                    "content": "\n".join(current_chunk),
                    "metadata": {"source": source, "section": "Diff_File"}
                })
                current_chunk = []
                current_words = 0
                
            current_chunk.append(line)
            current_words += line_words
            
            if current_words >= max_words:
                chunks.append({
                    "content": "\n".join(current_chunk),
                    "metadata": {"source": source, "section": "Diff_Segment"}
                })
                current_chunk = []
                current_words = 0
                
        if current_chunk:
            chunks.append({
                "content": "\n".join(current_chunk),
                "metadata": {"source": source, "section": "Diff_Remainder"}
            })
            
        return chunks

@register_as_module(system_auth="GSA_UNIVERSAL_ADAPTER", handshake_version="2.3")
class UniversalPreprocessor:
    """Factory controller orchestrating targeted ingestion routines by routing extension paths."""

    def __init__(self, max_words: int = 400):
        self.max_words = max_words
        self._parsers = {
            ".md": MarkdownParser(),
            ".txt": TextParser(),
            ".json": JsonParser(),
            ".csv": CsvParser(),
            ".pdf": PdfParser(),
            ".py": PythonParser(),
            ".diff": DiffPatchParser(),
            ".patch": DiffPatchParser()
        }

    def chunk_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Identifies extensions and targets proper execution parsers for text chunk generation."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Target document missing: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        parser = self._parsers.get(ext)
        if not parser:
            raise ValueError(f"Unsupported file format extension: {ext}")
            
        return parser.parse(file_path, self.max_words)

class MarkdownPreprocessor(UniversalPreprocessor):
    """Legacy interface token preserve layer to ensure regression compatibility with test scripts."""
    pass
