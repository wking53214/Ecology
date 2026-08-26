import ast
from pathlib import Path
from typing import List, Tuple


class Gitignore:
    def __init__(self, root: Path):
        self.root = root
        self.patterns = self._load_patterns()

    def _load_patterns(self):
        gitignore = self.root / ".gitignore"
        if not gitignore.exists():
            return []

        patterns = []
        for line in gitignore.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line)
        return patterns

    def ignores(self, path: Path) -> bool:
        rel = path.relative_to(self.root)

        for pattern in self.patterns:
            if pattern.endswith("/") and pattern[:-1] in rel.parts:
                return True
            if rel.name == pattern:
                return True
            if "*" in pattern and rel.match(pattern):
                return True

        return False


def discover_files(root_path: str, extensions: Tuple[str, ...]) -> List[Path]:
    """Recursively find files under root_path with the given extensions, respecting .gitignore."""
    root = Path(root_path)
    gitignore = Gitignore(root)

    files = []
    for ext in extensions:
        for path in root.rglob(f"*{ext}"):
            if gitignore.ignores(path):
                continue
            files.append(path)
    return files


def extract_python_chunks(file_path: Path) -> List[Tuple[str, str]]:
    """Split a Python file into per-function/class source chunks.

    Returns (identity, content) pairs, e.g. ("bar.py::foo", "<source of foo>"),
    so code can be ingested as addressable memory cells instead of opaque text.
    """
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    chunks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            segment = ast.get_source_segment(source, node)
            if segment:
                identity = f"{file_path.name}::{node.name}"
                chunks.append((identity, segment))
    return chunks
