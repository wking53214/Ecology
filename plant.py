import os, time, asyncio, json, re, difflib
from typing import Callable, Awaitable, Dict, Any, Optional, List
from pydantic import BaseModel, Field

# --- Schema ---
class ResponseSchema(BaseModel):
    status: str
    validated_content: str
    retry_attempts: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

# --- Components ---
class SemanticCache:
    def __init__(self): self.store = {}
    def set(self, key, val): self.store[key] = val
    def get(self, key): return self.store.get(key)
    def clear(self): self.store = {}

class AuditLogger:
    @staticmethod
    def log_event(data: Dict[str, Any]):
        with open("execution_audit.jsonl", "a") as f:
            f.write(json.dumps(data) + "\n")

# --- Filters ---
class InputSanitizationFilter:
    def is_clean(self, text: str) -> bool:
        forbidden = [r"ignore.*", r"system.*override", r"bypass.*constraint", r"output.*secret"]
        return not any(re.search(p, text.lower()) for p in forbidden)

class PersonalPronounFilter:
    def is_clean(self, text: str) -> bool:
        forbidden = [" i ", " we ", " my ", " our ", " me ", " us "]
        lowered = f" {text.lower()} "
        return not any(term in lowered for term in forbidden)

class ReadabilityFilter:
    def is_clean(self, text: str) -> bool:
        words = text.split()
        if len(words) == 0: return False
        avg_word_len = sum(len(w) for w in words) / len(words)
        return avg_word_len < 10.0

class SpeculativeLanguageFilter:
    def is_clean(self, text: str) -> bool:
        speculative_terms = ["perhaps", "maybe", "possibly", "itseems", "ithink", "itispossible"]
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()
        concatenated = clean_text.replace(" ", "")
        tokens = clean_text.split()
        search_space = tokens + [concatenated]
        for item in search_space:
            if item in speculative_terms: return False
            if difflib.get_close_matches(item, speculative_terms, n=1, cutoff=0.8):
                return False
        return True

# --- Pipeline ---
class ContentPolishPipeline:
    def __init__(self, execution_gateway: Callable[[str], Awaitable[str]]):
        self.gateway = execution_gateway
        self.sanitizer = InputSanitizationFilter()
        self.pronoun_filter = PersonalPronounFilter()
        self.readability_filter = ReadabilityFilter()
        self.speculation_filter = SpeculativeLanguageFilter()
        self.cache = SemanticCache()

    async def execute(self, input_prompt: str) -> ResponseSchema:
        if not self.sanitizer.is_clean(input_prompt):
            res = ResponseSchema(status="REJECTED", validated_content="Security violation.")
            AuditLogger.log_event({"prompt": input_prompt, "status": "REJECTED"})
            return res
        
        raw_response = await self.gateway(input_prompt)
        res = ResponseSchema(status="SUCCESS", validated_content=raw_response, retry_attempts=1)
        AuditLogger.log_event({"prompt": input_prompt, "status": "SUCCESS"})
        return res
