from unittest.mock import MagicMock
from src.rag.retrieval import RAGQueryEngine

def test_query_engine_retrieval_flow():
    """Validates that the hybrid query engine chains the vector and full-text search handlers."""
    # Create a mock table structure that simulates the LanceDB hybrid fluent interface
    mock_table = MagicMock()
    mock_query = MagicMock()
    
    # Configure the fluent hybrid call chain: query() -> hybrid() -> limit() -> to_list()
    mock_table.query.return_value = mock_query
    mock_query.hybrid.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.to_list.return_value = [
        {"content": "Hybrid System Core", "metadata": {"source": "system.py"}}
    ]
    
    engine = RAGQueryEngine(table=mock_table)
    results = engine.retrieve_context("system core", top_k=3)
    
    # Verify results
    assert "Hybrid System Core" in results["context_window"]
    assert "system.py" in results["source_documents"]
    assert results["hits_count"] == 1
    
    # Assert hybrid search was specifically invoked
    mock_query.hybrid.assert_called_with(query="system core")
