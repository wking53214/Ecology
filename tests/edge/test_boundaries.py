import pytest
from plant import ContentPolishPipeline

async def mock_gateway(prompt: str): return "Valid response."

@pytest.mark.asyncio
async def test_empty_input():
    pipeline = ContentPolishPipeline(execution_gateway=mock_gateway)
    result = await pipeline.execute("")
    assert result.status is not None

@pytest.mark.asyncio
async def test_massive_payload():
    pipeline = ContentPolishPipeline(execution_gateway=mock_gateway)
    result = await pipeline.execute("test" * 200000)
    assert result.status is not None
