#!/bin/bash
# Clean artifacts
rm -f execution_audit.jsonl
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Run full test suite
pytest -v tests/
