import os
import json
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import APIError
from src.governance.registry import register_as_module
from src.rag.retrieval import RAGQueryEngine
from src.telemetry.audit import AuditLogger

logger = logging.getLogger(__name__)

class AnalysisOutput(BaseModel):
    """Pydantic schema to strictly govern the structure of downstream model inferences."""
    analysis_response: str = Field(description="The formal, evidence-based synthesis addressing the query.")
    confidence_score: float = Field(description="Calculated certainty metric between 0.0 and 1.0 based on context density.")
    key_findings: List[str] = Field(description="Extracted focal architectural or governance system components identified.")

@register_as_module(system_auth="GSA_UNIVERSAL_ADAPTER", handshake_version="2.3")
class GeminiProductionClient:
    """Production client wrapper enforcing structured Pydantic outputs via the Google GenAI SDK."""

    def __init__(self, model_id: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        self.model_id = model_id
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        
        # Initialize client only if key exists
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("No API Key detected. GeminiProductionClient running in MOCK mode.")

    def __call__(self, prompt: str) -> str:
        if not self.client:
            return json.dumps({
                "analysis_response": "SIMULATION MODE: Inference bypassed.",
                "confidence_score": 0.0,
                "key_findings": ["System in tuning/simulation mode"]
            })

        try:
            config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
                response_mime_type="application/json",
                response_schema=AnalysisOutput
            )
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            logger.error(f"Inference failure: {e}")
            return '{"analysis_response": "ERROR: INFERENCE FAILURE", "confidence_score": 0.0, "key_findings": []}'

@register_as_module(system_auth="GSA_UNIVERSAL_ADAPTER", handshake_version="2.3")
class RAGGenerationEngine:
    """Orchestrates prompt payload compilation and execution against inference boundaries."""

    def __init__(self, query_engine: RAGQueryEngine, llm_callable: Optional[Callable[[str], str]] = None):
        self.query_engine = query_engine
        self.llm_callable = llm_callable or GeminiProductionClient()
        self.auditor = AuditLogger()

    def compile_prompt(self, query: str, context_window: str) -> str:
        return (
            "=== SYSTEM ARCHITECTURE INSTRUCTIONS ===\n"
            "Review the reference stack nodes below carefully.\n"
            "=== REFERENCE CONTEXT STACK ===\n"
            f"{context_window}\n\n"
            "=== TARGET QUERY RESPONSE REQUEST ===\n"
            f"QUERY: {query}\n\n"
            "ANALYSIS RESPONSE:"
        )

    def execute_synthesis(self, query: str, top_k: int = 3, max_distance: float = 1.2) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        # Retrieval Phase
        retrieval_result = self.query_engine.retrieve_context(
            query=query, top_k=top_k, max_distance=max_distance
        )
        
        # Generation Phase
        compiled_prompt = self.compile_prompt(query, retrieval_result["context_window"])
        raw_response = self.llm_callable(compiled_prompt)
        
        latency = time.perf_counter() - start_time
        
        # Audit Logging
        self.auditor.log_event("synthesis_cycle", {
            "query": query,
            "latency_seconds": latency,
            "hits_retrieved": retrieval_result["hits_count"],
            "top_k_configured": top_k
        })
        
        return {
            "status": "success",
            "generated_response": raw_response,
            "latency": latency
        }
