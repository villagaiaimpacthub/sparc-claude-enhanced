"""User endpoint tests"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"

def test_get_users():
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
