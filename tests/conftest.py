import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app


@pytest.fixture  # Create a fixture to create a test client and reuse it across tests
def client():
    return TestClient(app)
