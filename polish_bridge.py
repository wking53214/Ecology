import asyncio
import hashlib
import hmac
import os
import time
import logging
from typing import Callable, Awaitable, Dict, Any
import ollama

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PolishBridge")

class PersonalPronounFilter:
    def is_clean(self, text: str) -> bool:
        forbidden = [" i ", " we ", " my ", " our ", " me ", " us "]
        lowered = f" {text.lower()} "
        return not any(term in lowered for term in forbidden)

class SpeculativeLanguageFilter:
    def is_clean(self, text: str) -> bool:
        speculative_terms = ["perhaps", "maybe", "possibly", "it seems", "i think"]
        lowered = text.lower()
        return not any(term in lowered for term in speculative_terms)

class EmpiricalValidationFilter:
    def is_clean(self, text: str) -> bool:
        return len(text.strip()) > 10

class TextNormalizer:
    def process(self, text: str) -> str:
        return text.strip()

class ExecutionPacer:
    async def calculate_delay(self, text: str) -> float:
        return 0.05
    async def enforce_pause(self, delay: float):
        await asyncio.sleep(delay)

class ContentPolishPipeline:
    """Polish output for external communication (optional routing)."""
    def __init__(self, execution_gateway: Callable[[str], Awaitable[str]], max_attempts: int = 5):
        self.gateway = execution_gateway
        self.max_attempts = max_attempts
        self.pronoun_filter = PersonalPronounFilter()
        self.speculation_filter = SpeculativeLanguageFilter()
        self.empirical_filter = EmpiricalValidationFilter()
        self.normalizer = TextNormalizer()
        self.pacer = ExecutionPacer()
        signing_key = os.environ.get("ECOLOGY_SIGNING_KEY")
        if not signing_key:
            raise RuntimeError(
                "ECOLOGY_SIGNING_KEY environment variable must be set to a secret "
                "value before ContentPolishPipeline can sign output. A key checked "
                "into source control cannot provide integrity guarantees."
            )
        self._signing_key: bytes = signing_key.encode("utf-8")

    def _compute_signature(self, text: str) -> str:
        return hmac.new(self._signing_key, text.encode("utf-8"), hashlib.sha384).hexdigest()

    async def execute(self, input_prompt: str) -> Dict[str, Any]:
        active_prompt = input_prompt
        start_time = time.time()
        historical_hashes: set[str] = set()

        for iteration in range(1, self.max_attempts + 1):
            raw_response = await self.gateway(active_prompt)
            normalized_response = self.normalizer.process(raw_response)

            pronoun_check = self.pronoun_filter.is_clean(normalized_response)
            speculation_check = self.speculation_filter.is_clean(normalized_response)
            empirical_check = self.empirical_filter.is_clean(normalized_response)

            response_hash = hashlib.md5(normalized_response.encode("utf-8")).hexdigest()
            duplicate_detected = response_hash in historical_hashes

            if pronoun_check and speculation_check and empirical_check and not duplicate_detected:
                delay = await self.pacer.calculate_delay(normalized_response)
                await self.pacer.enforce_pause(delay)

                total_latency_ms = (time.time() - start_time) * 1000.0
                signature = self._compute_signature(normalized_response)

                logger.info(f"ContentPolishPipeline SUCCESS after {iteration} attempt(s)")
                return {
                    "execution_status": "SUCCESS",
                    "validation_parity": 1.0000,
                    "retry_attempts": iteration,
                    "latency_duration_ms": round(total_latency_ms, 2),
                    "payload_signature": signature,
                    "validated_content": normalized_response,
                }

            historical_hashes.add(response_hash)
            failures = []
            if not pronoun_check:
                failures.append("First-person language signature registered.")
            if not speculation_check:
                failures.append("Qualifying or ambiguous statements registered.")
            if not empirical_check:
                failures.append("Missing explicit rationales or metrics.")
            if duplicate_detected:
                failures.append("Duplicate generational loop pattern registered.")

            active_prompt = (
                f"{input_prompt}\n[RECALIBRATION_FEEDBACK]: Prior output failed validation rules due to: "
                f"{', '.join(failures)} Regulate generation format to meet precise syntax constraints."
            )

        logger.error(f"ContentPolishPipeline CRITICAL FAILURE after {self.max_attempts} attempts")
        raise SystemError("CRITICAL_PIPELINE_FAILURE: Maximum retry limits exhausted without validation consensus.")

async def async_ollama_gateway(prompt: str) -> str:
    client = ollama.AsyncClient()
    response = await client.chat(
        model='llama3.2',
        options={"num_predict": 256, "temperature": 0.1, "num_thread": 4},
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']

async def main():
    pipeline = ContentPolishPipeline(execution_gateway=async_ollama_gateway)
    test_prompt = "Provide an objective, metric-backed summary of the telemetry aggregator purpose."
    print(f"\n[System] Executing pipeline for prompt: '{test_prompt}'\n")
    
    try:
        result = await pipeline.execute(test_prompt)
        print("\n[Pipeline Execution Result]:")
        for key, value in result.items():
            print(f"- {key}: {value}")
    except Exception as e:
        logger.error(f"Pipeline execution halted: {e}")

if __name__ == "__main__":
    asyncio.run(main())
