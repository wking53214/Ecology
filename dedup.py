import os
import hashlib

def deduplicate_corpus(directory_path="corpus"):
    if not os.path.exists(directory_path):
        print(f"[System] Directory '{directory_path}' not found.")
        return

    seen_signatures = set()
    total_removed = 0

    for filename in os.listdir(directory_path):
        if not filename.endswith((".md", ".txt")):
            continue

        filepath = os.path.join(directory_path, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"[System] Error reading {filename}: {e}")
            continue

        segments = [seg.strip() for seg in content.split('\n\n') if seg.strip()]
        unique_segments = []
        file_removed = 0

        for segment in segments:
            normalized = " ".join(segment.split())
            sig = hashlib.sha256(normalized.encode('utf-8')).hexdigest()

            if sig not in seen_signatures:
                seen_signatures.add(sig)
                unique_segments.append(segment)
            else:
                file_removed += 1

        total_removed += file_removed

        if file_removed > 0:
            new_content = "\n\n".join(unique_segments) + "\n"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[Deduplication] Cleaned '{filename}': removed {file_removed} redundant segments.")

    print(f"\n[System] Deduplication complete. Total redundant cells purged: {total_removed}")

if __name__ == "__main__":
    deduplicate_corpus()
