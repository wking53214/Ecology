import os
import ollama
from datetime import datetime
from pathlib import Path
from typing import Optional

from code_scanner import discover_files, extract_python_chunks


class ActiveKnowledgeObject:
    def __init__(self, identity, content, timestamp, source):
        self.identity = identity
        self.content = content
        self.timestamp = timestamp
        self.source = source
        self.date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    def receive_message(self, message: str) -> Optional[str]:
        """Ask the model whether this cell's content answers `message`.

        Returns the verified answer text, or None if the cell is irrelevant
        or the model's extraction can't be confirmed as a literal excerpt of
        this cell's own content. That containment check is the evidence
        boundary: it stops a plausible-sounding, ungrounded model answer
        from being treated as if it came from the source material.
        """
        relevance_response = ollama.chat(
            model='llama3.2:1b',
            messages=[
                {'role': 'system', 'content': 'You are a binary classifier. Output exactly YES if the data contains the answer to the query, or NO if it does not. No other text.'},
                {'role': 'user', 'content': 'Data: "The car is red."\nQuery: "What color is the vehicle?"'},
                {'role': 'assistant', 'content': 'YES'},
                {'role': 'user', 'content': 'Data: "The car is red."\nQuery: "How do I cook pasta?"'},
                {'role': 'assistant', 'content': 'NO'},
                {'role': 'user', 'content': f'Data: "{self.content}"\nQuery: "{message}"'}
            ],
            options={'temperature': 0.0, 'top_k': 1}
        )

        relevance = relevance_response['message']['content'].strip().upper()

        if "YES" not in relevance:
            return None

        answer_response = ollama.chat(
            model='llama3.2:1b',
            messages=[
                {'role': 'system', 'content': 'You are a strict text-extraction robot. Extract the exact sentence containing the answer. If the answer is not present, output exactly: UNKNOWN.'},
                {'role': 'user', 'content': 'Data: "The car is red. It has four wheels."\nQuery: "What color is the vehicle?"'},
                {'role': 'assistant', 'content': 'The car is red.'},
                {'role': 'user', 'content': 'Data: "The car is red. It has four wheels."\nQuery: "Who makes the car?"'},
                {'role': 'assistant', 'content': 'UNKNOWN'},
                {'role': 'user', 'content': f'Data: "{self.content}"\nQuery: "{message}"'}
            ],
            options={'temperature': 0.0, 'top_k': 1}
        )

        reply = answer_response['message']['content'].strip()

        blacklist = ["UNKNOWN", "I couldn't find", "I didn't provide", "I can't provide", "I don't have", "If I had to guess"]
        if any(phrase.lower() in reply.lower() for phrase in blacklist):
            return None

        if reply.lower() not in self.content.lower():
            return None

        if len(reply.split()) < 1:
            return None

        return reply


def ingest_directory(directory_path):
    ecology_cluster = []

    if not os.path.exists(directory_path):
        print(f"[System] Directory '{directory_path}' not found.")
        return ecology_cluster

    root = Path(directory_path)
    text_files = discover_files(directory_path, (".md", ".txt"))
    python_files = discover_files(directory_path, (".py",))

    for filepath in text_files:
        rel_path = filepath.relative_to(root).as_posix()
        file_timestamp = filepath.stat().st_mtime

        try:
            raw_dna = filepath.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception as e:
            print(f"[System] Skipping '{rel_path}' due to read error: {e}")
            continue

        segments = [segment.strip() for segment in raw_dna.split('\n\n') if segment.strip()]

        for index, segment in enumerate(segments):
            identity = f"{rel_path}[Cell-{index+1}]"
            cell = ActiveKnowledgeObject(identity=identity, content=segment, timestamp=file_timestamp, source=rel_path)
            ecology_cluster.append(cell)

    for filepath in python_files:
        rel_path = filepath.relative_to(root).as_posix()
        file_timestamp = filepath.stat().st_mtime
        for symbol_name, content in extract_python_chunks(filepath):
            identity = f"{rel_path}::{symbol_name}"
            cell = ActiveKnowledgeObject(identity=identity, content=content, timestamp=file_timestamp, source=rel_path)
            ecology_cluster.append(cell)

    ecology_cluster.sort(key=lambda x: x.timestamp, reverse=True)

    parent_count = len(text_files) + len(python_files)
    print(f"[System] Ecology initialized with {len(ecology_cluster)} active cells descended from {parent_count} parent structures.\n")
    return ecology_cluster
