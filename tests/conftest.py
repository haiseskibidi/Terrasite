import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import config
import os
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture(scope="session")
def test_app():
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

@pytest_asyncio.fixture(autouse=True)
async def mock_leads_file(tmp_path):
    leads_file = tmp_path / "leads.json"
    config.leads_file = str(leads_file)
    yield leads_file
    if os.path.exists(leads_file):
        os.remove(leads_file)

@pytest_asyncio.fixture
async def mock_aiofiles_open(monkeypatch):
    mock_open = AsyncMock()
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_context
    mock_context.__aexit__.return_value = None
    mock_context.read = AsyncMock()
    mock_context.write = AsyncMock()
    mock_open.return_value = mock_context
    monkeypatch.setattr("aiofiles.open", mock_open)
    return mock_open

@pytest_asyncio.fixture
async def mock_aiosmtplib(monkeypatch):
    mock_smtp = AsyncMock()
    mock_server = AsyncMock()
    mock_smtp.return_value.__aenter__.return_value = mock_server
    mock_smtp.return_value.__aexit__.return_value = None
    monkeypatch.setattr("aiosmtplib.SMTP", mock_smtp)
    return mock_server