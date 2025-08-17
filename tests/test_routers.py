import pytest
import pytest_asyncio
from fastapi import HTTPException
from unittest.mock import AsyncMock
from backend.schemas import Lead, LeadCreate
from backend.services import LeadService
from datetime import datetime


@pytest_asyncio.fixture
async def mock_lead_service(monkeypatch):
    mock_service = AsyncMock(spec=LeadService)
    monkeypatch.setattr("backend.routers.get_lead_service", lambda: mock_service)
    return mock_service


@pytest.mark.asyncio
async def test_submit_form_valid(client, mock_lead_service):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }
    lead_data = LeadCreate(**data)
    mock_lead = Lead(id=1, timestamp=datetime.now(), **data)
    mock_lead_service.process_lead.return_value = mock_lead

    response = client.post("/submit-form", json=data)
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Заявка успешно отправлена"}
    mock_lead_service.process_lead.assert_called_once_with(lead_data)


@pytest.mark.asyncio
async def test_submit_form_duplicate(client, mock_lead_service):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }
    mock_lead_service.process_lead.side_effect = HTTPException(
        status_code=400, detail="Заявка с такими контактными данными уже была отправлена недавно"
    )

    response = client.post("/submit-form", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Заявка с такими контактными данными уже была отправлена недавно"


@pytest.mark.asyncio
async def test_submit_form_validation_error(client, mock_lead_service):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation",
        "budget": "30-50k",
        "contact_method": "email"
    }
    mock_lead_service.process_lead.side_effect = HTTPException(status_code=400, detail="Введите email адрес")

    response = client.post("/submit-form", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Введите email адрес"


@pytest.mark.asyncio
async def test_submit_form_server_error(client, mock_lead_service):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }
    mock_lead_service.process_lead.side_effect = Exception("Server error")

    response = client.post("/submit-form", json=data)
    assert response.status_code == 500
    assert "Внутренняя ошибка" in response.json()["detail"]["error"]


@pytest.mark.asyncio
async def test_admin_leads(client, mock_lead_service):
    mock_leads = [
        Lead(
            id=1,
            timestamp=datetime.now(),
            name="Test",
            services=["site"],
            description="long description with enough words to pass validation",
            budget="30-50k",
            contact_method="email",
            email="test@example.com"
        )
    ]
    mock_lead_service.get_all_leads.return_value = mock_leads

    response = client.get("/admin/leads")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1


@pytest.mark.asyncio
async def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()