import pytest
from tarxemo_django_graphene_utils.responses import (
    ResponseRegistry, 
    build_success_response, 
    build_error_response
)

def test_response_registry_default():
    res = ResponseRegistry.get_response_data(1)
    assert res["id"] == 1
    assert res["status"] is True
    assert res["code"] == 2000

def test_response_registry_unknown():
    # Should default to unexpected error (id 3)
    res = ResponseRegistry.get_response_data(999)
    assert res["id"] == 3
    assert res["status"] is False

def test_build_success_response():
    response = build_success_response(message="Custom Success")
    assert response.status is True
    assert response.message == "Custom Success"
    assert response.code == 2000

def test_build_error_response():
    response = build_error_response(message="Custom Error", code=5000)
    assert response.status is False
    assert response.message == "Custom Error"
    assert response.code == 5000
