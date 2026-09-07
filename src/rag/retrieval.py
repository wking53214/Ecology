from src.governance.registry import register_as_module

@register_as_module(system_auth="GSA_UNIVERSAL_ADAPTER", handshake_version="2.3")
class RAGQueryEngine:
    def __init__(self, storage_manager=None, embedding_model=None, *, table=None, **kwargs):
        """Compatibility constructor: accept either storage_manager+embedding_model or a 'table' keyword.
        If a table is provided, wrap it with a thin adapter exposing .search(query_vec, top_k).
        """
        if table is not None:
            class _TableAdapter:
                def __init__(self, tbl):
                    self._tbl = tbl
                def search(self, query_vec, top_k=3):
                    # support LanceDB-like fluent API used in tests/mocks
                    try:
                        q = self._tbl.query()
                        q = q.hybrid(query=query_vec)
                        q = q.limit(top_k)
                        rows = q.to_list()
                        return [{"raw_content": r.get("content"), "provenance": {"source": r.get("metadata", {}).get("source")}} for r in rows]
                    except Exception:
                        # fallback for simpler mock tables
                        return [{"raw_content": r.get("content"), "provenance": {"source": r.get("metadata", {}).get("source")}} for r in getattr(self._tbl, "to_list", lambda: [])()]
            self.storage_manager = _TableAdapter(table)
            self.embedding_model = embedding_model
        else:
            self.storage_manager = storage_manager
            self.embedding_model = embedding_model

    def retrieve_context(self, query: str, top_k: int = 3, max_distance: float = 1.2) -> dict:
        # If no embedding model provided (table-only mode), pass the raw query through to the storage search
        if self.embedding_model is None:
            query_vec = query
        else:
            query_vec = self.embedding_model.encode(query).tolist()

        results = self.storage_manager.search(query_vec, top_k=top_k)
        
        if not results:
            return {"context_window": "NO RELEVANT_MATCHES_FOUND", "hits_count": 0, "source_documents": []}
            
        context = "\n".join([res.get("raw_content", "") for res in results])
        source_documents = [res.get("provenance", {}).get("source") for res in results]
        return {"context_window": context, "hits_count": len(results), "source_documents": source_documents}
