import os
import io
import json
import hashlib
import zipfile
import logging
from typing import List, Dict, Any, Set

from src.governance.registry import register_as_module
from src.rag.pipeline import RAGOrchestrationPipeline

logger = logging.getLogger(__name__)

@register_as_module(system_auth="GSA_UNIVERSAL_ADAPTER", handshake_version="2.3")
class DirectoryIngestionScanner:
    """Traverses workspace directories with in-memory zip handling and SHA-256 state tracking."""

    def __init__(self, supported_extensions: Set[str] = None, state_file: str = ".living_memory_state.json"):
        if supported_extensions is None:
            self.supported_extensions = {
                ".md", ".txt", ".json", ".csv", ".pdf", ".py", ".diff", ".patch"
            }
        else:
            self.supported_extensions = {ext.lower() for ext in supported_extensions}
        
        self.state_file = state_file
        self.state_registry = self._load_state_registry()

    def _load_state_registry(self) -> Dict[str, str]:
        """Loads the persistent file status database cache from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read file tracking index, starting fresh: {e}")
        return {}

    def _save_state_registry(self):
        """Persists the cryptographic state tracking registry back to disk."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state_registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write state tracking registry to disk: {e}")

    def _compute_sha256(self, file_path: str) -> str:
        """Calculates the cryptographic checksum signature of a target on-disk file."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Failed calculating checksum for {file_path}: {e}")
            return ""

    def scan(self, target_directory: str) -> List[str]:
        """Recursively traverses the directory tree to collect valid non-archive file paths."""
        matched_files = []
        if not os.path.exists(target_directory):
            logger.error(f"Target directory path does not exist: {target_directory}")
            return matched_files

        for root, _, files in os.walk(target_directory):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.supported_extensions:
                    full_path = os.path.join(root, file)
                    matched_files.append(full_path)
        
        return matched_files

    def process_zip_in_memory(self, zip_path: str) -> List[Dict[str, Any]]:
        """Opens a zip file and extracts compliant document contents directly into memory data streams."""
        virtual_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zref:
                for member in zref.namelist():
                    if member.endswith('/'):
                        continue
                        
                    ext = os.path.splitext(member)[1].lower()
                    if ext in self.supported_extensions:
                        with zref.open(member) as f:
                            content_bytes = f.read()
                            
                        # Generate fingerprint for virtual assets to verify in-memory deltas
                        hasher = hashlib.sha256(content_bytes)
                        v_hash = hasher.hexdigest()
                        v_path = f"{zip_path}::{member}"
                        
                        if self.state_registry.get(v_path) == v_hash:
                            continue  # Unmodified virtual node
                            
                        virtual_files.append({
                            "virtual_path": v_path,
                            "content": content_bytes,
                            "extension": ext,
                            "hash": v_hash
                        })
        except Exception as e:
            logger.error(f"Failed to extract target archive file {zip_path}: {e}")
            
        return virtual_files

    def execute_batch_ingestion(self, target_directory: str, pipeline: RAGOrchestrationPipeline) -> Dict[str, Any]:
        """Discovers all modified files and zip records, committing changes onto vector maps."""
        # 1. Gather all whitelisted standard system files
        all_paths = self.scan(target_directory)
        modified_paths = []
        
        # 2. Filter out standard targets that match historical checksum logs
        for p in all_paths:
            current_hash = self._compute_sha256(p)
            if not current_hash:
                continue
            if self.state_registry.get(p) != current_hash:
                modified_paths.append(p)
                # Store the updated fingerprint pending pipeline consumption
                self.state_registry[p] = current_hash

        # 3. Process zip archive payloads, tracking in-memory signature alterations
        all_virtual_files = []
        for root, _, files in os.walk(target_directory):
            for file in files:
                if file.lower().endswith('.zip'):
                    zip_full_path = os.path.join(root, file)
                    extracted = self.process_zip_in_memory(zip_full_path)
                    all_virtual_files.extend(extracted)

        # 4. Direct pipeline ingestion execution pass over modified disk tracks
        pipeline_result = pipeline.orchestrate(modified_paths) if modified_paths else {"cells_ingested": 0, "skipped_files": []}
        
        # 5. Process memory-extracted assets using the preprocessor factory directly
        virtual_cells_count = 0
        preprocessor = pipeline.preprocessor
        
        for v_file in all_virtual_files:
            try:
                parser = preprocessor._parsers.get(v_file["extension"])
                if parser:
                    temp_virtual_path = f"temp_virtual_{os.path.basename(v_file['virtual_path'])}"
                    with open(temp_virtual_path, "wb") as f_tmp:
                        f_tmp.write(v_file["content"])
                        
                    try:
                        chunks = parser.parse(temp_virtual_path, preprocessor.max_words)
                        for chunk in chunks:
                            chunk["metadata"]["source"] = v_file["virtual_path"]
                            pipeline.storage_manager.add_cells([chunk])
                            virtual_cells_count += len(chunks)
                            
                        # Cache verified hash configuration
                        self.state_registry[v_file["virtual_path"]] = v_file["hash"]
                    finally:
                        if os.path.exists(temp_virtual_path):
                            os.remove(temp_virtual_path)
            except Exception as e:
                logger.error(f"Failed to ingest virtual component {v_file['virtual_path']}: {e}")

        # 6. Save verified delta states back to disk index files
        if modified_paths or all_virtual_files:
            self._save_state_registry()

        return {
            "status": "success",
            "files_found": len(all_paths),
            "files_vectorized": len(modified_paths),
            "virtual_files_ingested": len(all_virtual_files),
            "pipeline_result": {
                "cells_ingested": pipeline_result.get("cells_ingested", 0) + virtual_cells_count,
                "skipped_files": pipeline_result.get("skipped_files", [])
            }
        }
