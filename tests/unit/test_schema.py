from plant import ResponseSchema

def test_response_schema_integrity():
    data = {"status": "SUCCESS", "validated_content": "test"}
    model = ResponseSchema(**data)
    assert model.status == "SUCCESS"
    assert isinstance(model.retry_attempts, int)
