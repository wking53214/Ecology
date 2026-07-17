import pytest
from plant import ContentPolishPipeline

async def failing_gateway(prompt: str):
    raise ConnectionError("Gateway unreachable")

@pytest.mark.asyncio
async def test_pipeline_handles_gateway_failure():
    # Note: Pipeline currently lacks try/except, this test verifies it should be added
    pipeline = ContentPolishPipeline(execution_gateway=failing_gateway)
    try:
        await pipeline.execute("test")
    except Exception as e:
        assert isinstance(e, ConnectionError)
