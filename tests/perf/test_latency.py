import pytest
import time
import asyncio
from plant import ContentPolishPipeline

async def mock_gateway(prompt: str):
    await asyncio.sleep(0.05) # Simulated network latency
    return "Valid stable response."

@pytest.mark.asyncio
async def test_latency_budget():
    pipeline = ContentPolishPipeline(execution_gateway=mock_gateway)
    start = time.perf_counter()
    await pipeline.execute("Standard throughput test.")
    duration = time.perf_counter() - start
    
    # Assert latency budget of 200ms
    assert duration < 0.200, f"Latency budget exceeded: {duration:.4f}s"
