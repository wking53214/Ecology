# Ecology

Local **RAG technical memory**: ingest chat exports, PDFs, Python source into chunked, queryable cells with evidence-bound non-answers. Experimental. **Not a stage of the governed action path.**

## 1. Pipeline Position & Role

**SPECIALIZED INLET / TOOLING.** Personal/founder memory over a harvested corpus. Commercial: **NOT COMMERCIALLY RELEVANT**; corpus cannot ship (provenance/license).

## 2. Full System Scope & Architectural Depth

**Two RAG stacks that do not share a store.**

### A — the path that matches STACK.md (working)

1. `ecology.ingest_directory` → `ActiveKnowledgeObject{identity, content, timestamp, source, date_str}`
2. Chroma collection **`living_memory_v3`** (ONNX MiniLM-L6-v2, 384-d). History → `conversation_history_v2`. Git commit history → `commit_history_v1` (`commit_loader.py`, `rag_engine.index_commit_history`, `scripts/run_commit_index.py`): one cell per commit with its real author time, author, message and changed files, so "what changed" sits beside "why it was discussed".
3. `generate_response`: ANN → `containment.verify` (default deterministic) → else **"The retrieved corpus does not contain a verifiable answer"**
4. Else Ollama `llama3.2` (`temperature=0.1`, `num_predict=512`) then `_synthesis_matches_its_own_sources` (`SYNTHESIS_OVERLAP_FLOOR=0.35`)
5. `FindingRecord` duck-typed toward CCC

Containment weights (uncalibrated): `w_coverage=0.40`, `w_anchor=0.25`, …; gates `min_matched_weight=0.40`, `min_anchor_score=0.50`, `min_score=0.68`. LLM-per-cell verifier measured **>120s** and never completed Ecology→CCC on real data — hence deterministic default.

### B — `src/rag/` Gemini + LanceDB

`run_rag.py`, `scripts/ingest_*.py`. `lancedb` / `sentence_transformers` **undeclared** in `requirements.txt`. `--mock` returns a **hardcoded fake GSA registry answer**. Handshake decorator theater (`GSA_UNIVERSAL_ADAPTER` 2.3).

~449 files / 162 py; mass is **corpus/** (~362 harvested files, excluded from license).

## 3. What It Does NOT Do / Non-Goals

- Does not persist identity/relationship/temporal graphs (README ambition).
- Does not govern sentinel_os; it *indexes text about it*.
- Does not share Chroma with LanceDB.

## 4. Brutally Honest Current Status & Gaps

| Gap | Detail |
|---|---|
| README drift | Still says collection `living_memory_v2`; code is v3. Still describes LLM-per-cell as the verifier. |
| Dual stack | Path B does not install from declared deps. |
| Unlicensed corpus | Cannot ship. |
| `plant.py` | Weaker polish duplicate, no signing key. |
| Hard-coded paths | Personal machine shaped. |

Declared: `ollama, chromadb, pydantic, pypdf`. Runtime: local Ollama. Optional `GEMINI_API_KEY`, `ECOLOGY_SIGNING_KEY`.

## 5. Core Invariants & Guarantees

Empty verification → non-answer. Synthesis overlap fail → non-answer. Polish refuses missing signing key. **Not** fail-closed: stale Chroma skip; LanceDB swallows exceptions.

## 6. Inputs, Outputs & Type Contracts

`ActiveKnowledgeObject`; `FindingRecord{conclusion, method, source_material, confidence, verified, evidence, event_start_date, event_end_date}`.

## 7. Stack Integration Topology

```text
harvested portfolio text → Ecology Chroma → optional CCC-shaped findings
observe-perceive / α-ζ-β-δ / sentinel_os  ✗ not imported
```

Apache-2.0 on engine; corpus excluded.
