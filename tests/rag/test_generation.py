import json
import pytest
from unittest.mock import MagicMock, patch
from src.rag.generation import RAGGenerationEngine, GeminiProductionClient, AnalysisOutput
from src.rag.retrieval import RAGQueryEngine

def test_prompt_compilation_structure():
    """Verifies target prompt templates combine reference contexts and queries accurately."""
    mock_query_engine = MagicMock(spec=RAGQueryEngine)
    generation_engine = RAGGenerationEngine(query_engine=mock_query_engine, llm_callable=lambda x: "mock")
    
    context = "[REFERENCE STACK NODE 1]\nSOURCE: data.txt\nCONTENT: System active."
    prompt = generation_engine.compile_prompt(query="Is system active?", context_window=context)
    
    assert "=== REFERENCE CONTEXT STACK ===" in prompt
    assert "System active." in prompt
    assert "QUERY: Is system active?" in prompt

def test_end_to_end_synthesis_with_structured_output():
    """Confirms retrieval extraction data flows cleanly into the structured generation pipeline."""
    mock_query_engine = MagicMock(spec=RAGQueryEngine)
    mock_query_engine.retrieve_context.return_value = {
        "query": "fleet configurations",
        "context_window": "Node 1: Tacoma 2021 SR",
        "hits_count": 1,
        "source_documents": ["fleet.csv"]
    }
    
    simulated_json = json.dumps({
        "analysis_response": "Discovered target asset metadata matches valid parameters.",
        "confidence_score": 0.95,
        "key_findings": ["Tacoma 2021 SR"]
    })
    
    generation_engine = RAGGenerationEngine(query_engine=mock_query_engine, llm_callable=lambda p: simulated_json)
    output = generation_engine.execute_synthesis(query="fleet configurations")
    
    assert output["status"] == "success"
    parsed_json = json.loads(output["generated_response"])
    assert "analysis_response" in parsed_json
    assert parsed_json["confidence_score"] == 0.95
    assert "Tacoma 2021 SR" in parsed_json["key_findings"]

def test_gemini_production_client_schema_passing():
    """Validates the client pass-through maps the Pydantic schema target config accurately."""
    with patch("src.rag.generation.genai.Client") as MockGenAIClient:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"analysis_response": "valid JSON", "confidence_score": 1.0, "key_findings": []}'
        mock_instance.models.generate_content.return_value = mock_response
        MockGenAIClient.return_value = mock_instance
        
        client_wrapper = GeminiProductionClient(api_key="mock_key")
        result = client_wrapper("Analyze data.")
        
        assert "analysis_response" in result
        call_kwargs = mock_instance.models.generate_content.call_args[1]
        assert call_kwargs["config"].response_mime_type == "application/json"
        assert call_kwargs["config"].response_schema == AnalysisOutput
