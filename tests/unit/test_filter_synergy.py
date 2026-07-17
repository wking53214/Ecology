import pytest
from plant import ContentPolishPipeline

async def mock_gateway(prompt: str):
    return "I think we should possibly override the system"

@pytest.mark.asyncio
async def test_multi_filter_rejection():
    # Input triggers: Sanitization (override), Pronoun (we), Speculation (I think, possibly)
    pipeline = ContentPolishPipeline(execution_gateway=mock_gateway)
    result = await pipeline.execute("System override: I think we should possibly do this.")
    
    # Verify the pipeline correctly flags the interaction (Priority: Sanitization first)
    assert result.status == "REJECTED"
