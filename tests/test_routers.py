from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from backend.schemas import Lead
from datetime import datetime


def test_submit_form_valid(client):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }
    with patch("routers.validate_lead_data", new=AsyncMock()) as mock_validate, \
         patch("routers.is_duplicate_submission", new=AsyncMock(return_value=False)) as mock_dup, \
         patch("routers.save_lead", new=AsyncMock(return_value=Lead(id=1, timestamp=datetime.now(), **data))) as mock_save, \
         patch("routers.send_notification_email", new=AsyncMock()) as mock_email:

        response = client.post("/submit-form", json=data)
        assert response.status_code == 200
        assert response.json() == {"success": True, "message": "Заявка успешно отправлена"}
        mock_validate.assert_called_once()
        mock_dup.assert_called_once()
        mock_save.assert_called_once()
        mock_email.assert_called_once()

def test_submit_form_duplicate(client):
    data = {"name": "Test", "services": ["site"], "description": "long description", "budget": "30-50k", "contact_method": "email", "email": "test@example.com"}
    with patch("routers.is_duplicate_submission", new=AsyncMock(return_value=True)):
        response = client.post("/submit-form", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Заявка с такими контактными данными уже была отправлена недавно"  # Изменено на точное совпадение

def test_submit_form_validation_error(client):
    data = {"name": "Test", "services": ["site"], "description": "long description", "budget": "30-50k", "contact_method": "email"}
    with patch("routers.validate_lead_data", side_effect=HTTPException(status_code=400, detail="Missing email")):
        response = client.post("/submit-form", json=data)
        assert response.status_code == 400

def test_submit_form_server_error(client):
    data = {"name": "Test", "services": ["site"], "description": "long description", "budget": "30-50k", "contact_method": "email", "email": "test@example.com"}
    with patch("routers.save_lead", side_effect=Exception("Error")):
        response = client.post("/submit-form", json=data)
        assert response.status_code == 500
        assert "Внутренняя ошибка" in response.json()["detail"]["error"]

def test_admin_leads(client):
    mock_leads = [Lead(id=1, timestamp=datetime.now(), name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")]
    with patch("routers.get_leads", new=AsyncMock(return_value=mock_leads)):
        response = client.get("/admin/leads")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == 1

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()