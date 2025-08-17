import pytest
from datetime import datetime
from fastapi import HTTPException
from backend.schemas import LeadCreate, Lead
from backend.services import LeadService
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_submit_form_valid(client, mock_lead_service):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation for the test case",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }
    lead_data = LeadCreate(**data)
    mock_lead = Lead(id=1, timestamp=datetime.now(), **data)
    mock_lead_service.process_lead.return_value = mock_lead

    response = client.post("/submit-form", json=data)
    assert response.status_code == 200
    assert response.json() == mock_lead.model_dump()

@pytest.mark.asyncio
async def test_submit_form_duplicate(client, mock_lead_service):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation for the test case",
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
async def test_submit_form_invalid(client):
    data = {
        "name": "",
        "services": [],
        "description": "short",
        "budget": "invalid",
        "contact_method": "invalid",
        "email": "invalid"
    }
    response = client.post("/submit-form", json=data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_submit_form_server_error(client, mock_lead_service):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation for the test case",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }
    mock_lead_service.process_lead.side_effect = Exception("Server error")

    response = client.post("/submit-form", json=data)
    assert response.status_code == 500
    assert "Ошибка обработки заявки" in response.json()["detail"]

@pytest.mark.asyncio
async def test_admin_leads(client, mock_lead_service):
    mock_leads = [
        Lead(
            id=1,
            timestamp=datetime.now(),
            name="Test",
            services=["site"],
            description="long description with enough words to pass validation for the test case",
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