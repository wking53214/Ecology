import pytest
import asyncio
from plant import ContentPolishPipeline
from tests.mocks.mock_gateway import mock_gateway

@pytest.mark.asyncio
async def test_pipeline_retry_loop():
    # pipeline must catch speculative failure and succeed on re-evaluation
    pipeline = ContentPolishPipeline(execution_gateway=mock_gateway)
    
    # trigger fail case
    result = await pipeline.execute("fail")
    
    assert result.status == "SUCCESS"
    assert result.validated_content is not None
