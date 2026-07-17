import pytest
import asyncio
from plant import ContentPolishPipeline

async def mock_gateway(prompt: str):
    await asyncio.sleep(0.01)
    return "Valid stable response."

@pytest.mark.asyncio
async def test_concurrent_pipeline_execution():
    pipeline = ContentPolishPipeline(execution_gateway=mock_gateway)
    # Execute 10 simultaneous pipeline calls
    tasks = [pipeline.execute("parallel request") for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    assert all(r.status == "SUCCESS" for r in results), "Pipeline failed to handle concurrency."
