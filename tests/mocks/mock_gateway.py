import asyncio

_state = {"attempts": 0}

async def mock_gateway(prompt: str):
    await asyncio.sleep(0.01)
    _state["attempts"] += 1
    # Fail on first call, succeed thereafter
    if _state["attempts"] == 1:
        return "I think this is valid."
    return "The system is valid and empirically stable."
