import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import config
import os
from unittest.mock import AsyncMock

@pytest.fixture(scope="session")
def test_app():
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

@pytest.fixture(autouse=True)
def mock_leads_file(tmp_path):
    leads_file = tmp_path / "leads.json"
    config.LEADS_FILE = str(leads_file)
    yield leads_file
    if os.path.exists(leads_file):
        os.remove(leads_file)

@pytest.fixture
def mock_aiofiles_open(monkeypatch):
    mock_open = AsyncMock()
    monkeypatch.setattr("aiofiles.open", mock_open)
    return mock_open

@pytest.fixture
def mock_aiosmtplib(monkeypatch):
    mock_smtp = AsyncMock()
    mock_server = AsyncMock()
    mock_smtp.return_value.__aenter__.return_value = mock_server
    monkeypatch.setattr("aiosmtplib.SMTP", mock_smtp)
    return mock_server