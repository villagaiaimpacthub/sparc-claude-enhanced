"""Authentication tests"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com", 
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
