import pytest
from plant import ContentPolishPipeline

async def failing_gateway(prompt: str):
    raise ConnectionError("Gateway unreachable")

@pytest.mark.asyncio
async def test_pipeline_propagates_gateway_failure():
    # Documents actual current behavior: the pipeline has no try/except
    # around the gateway call, so a gateway error propagates unhandled
    # rather than being caught and reported as a REJECTED/FAILED result.
    pipeline = ContentPolishPipeline(execution_gateway=failing_gateway)
    with pytest.raises(ConnectionError):
        await pipeline.execute("test")
