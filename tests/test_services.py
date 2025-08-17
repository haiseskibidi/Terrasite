import pytest
from services import is_duplicate_submission, validate_lead_data, save_lead, send_notification_email, get_leads
from schemas import LeadCreate, Lead
from datetime import datetime, timedelta
import json
from unittest.mock import patch, AsyncMock, ANY
import asyncio

def test_is_duplicate_submission_no_file(mock_aiofiles_open):
    lead_data = LeadCreate(name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")
    mock_aiofiles_open.side_effect = FileNotFoundError
    result = asyncio.run(is_duplicate_submission(lead_data))
    assert result == False

def test_is_duplicate_submission_duplicate(mock_aiofiles_open):
    lead_data = LeadCreate(name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")
    existing_leads = [{
        "id": 1,
        "timestamp": (datetime.now() - timedelta(seconds=1)).isoformat(),  # Добавлено timedelta для гарантии time_diff >0 <300
        "contact_method": "email",
        "email": "test@example.com"
    }]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    result = asyncio.run(is_duplicate_submission(lead_data))
    assert result == True

def test_is_duplicate_submission_not_duplicate_time(mock_aiofiles_open):
    lead_data = LeadCreate(name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")
    old_time = (datetime.now() - timedelta(minutes=6)).isoformat()
    existing_leads = [{
        "id": 1,
        "timestamp": old_time,
        "contact_method": "email",
        "email": "test@example.com"
    }]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    result = asyncio.run(is_duplicate_submission(lead_data))
    assert result == False

def test_is_duplicate_submission_different_method(mock_aiofiles_open):
    lead_data = LeadCreate(name="Test", services=["site"], description="long description", budget="30-50k", contact_method="whatsapp", phone="+123")
    existing_leads = [{
        "id": 1,
        "timestamp": datetime.now().isoformat(),
        "contact_method": "email",
        "email": "test@example.com"
    }]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    result = asyncio.run(is_duplicate_submission(lead_data))
    assert result == False

def test_is_duplicate_submission_no_contact_value():
    lead_data = LeadCreate(name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email")
    result = asyncio.run(is_duplicate_submission(lead_data))
    assert result == False

@pytest.mark.parametrize("contact_method, missing_field", [
    ("whatsapp", "phone"),
    ("telegram", "telegram"),
    ("phone", "phone_number"),
    ("phone", "call_time"),
    ("email", "email")
])
def test_validate_lead_data_missing(contact_method, missing_field):
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "description long",
        "budget": "30-50k",
        "contact_method": contact_method
    }
    if missing_field != "call_time" and contact_method == "phone":
        data["call_time"] = "10:00"
    elif missing_field != "phone_number" and contact_method == "phone":
        data["phone_number"] = "+123"
    lead_data = LeadCreate(**data)
    with pytest.raises(Exception) as exc:
        asyncio.run(validate_lead_data(lead_data))

def test_validate_lead_data_valid():
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "description long",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }
    lead_data = LeadCreate(**data)
    asyncio.run(validate_lead_data(lead_data))

def test_save_lead_new_file(mock_aiofiles_open):
    lead_data = LeadCreate(name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")
    mock_read_file = AsyncMock()
    mock_read_file.read.side_effect = FileNotFoundError
    mock_write_file = AsyncMock()
    mock_aiofiles_open.side_effect = [mock_read_file, mock_write_file]

    lead = asyncio.run(save_lead(lead_data))
    assert lead.id == 1
    mock_write_file.write.assert_called_once()

def test_save_lead_existing(mock_aiofiles_open):
    lead_data = LeadCreate(name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")
    existing_leads = [{"id": 1, "name": "Existing", "services": ["site"], "description": "long description", "budget": "30-50k", "contact_method": "email", "email": "existing@example.com"}]
    mock_read_file = AsyncMock()
    mock_read_file.read.return_value = json.dumps(existing_leads)
    mock_write_file = AsyncMock()
    mock_aiofiles_open.side_effect = [mock_read_file, mock_write_file]

    lead = asyncio.run(save_lead(lead_data))
    assert lead.id == 2
    mock_write_file.write.assert_called_once()

def test_save_lead_error(mock_aiofiles_open):
    lead_data = LeadCreate(name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")
    mock_aiofiles_open.side_effect = Exception("File error")
    with pytest.raises(Exception) as exc:
        asyncio.run(save_lead(lead_data))
    assert "500" in str(exc.value.status_code)

def test_send_notification_email(mock_aiosmtplib):
    lead = Lead(id=1, timestamp=datetime.now(), name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")
    asyncio.run(send_notification_email(lead))
    mock_aiosmtplib.login.assert_called_once()
    mock_aiosmtplib.send_message.assert_called_once()

def test_send_notification_email_error(mock_aiosmtplib):
    lead = Lead(id=1, timestamp=datetime.now(), name="Test", services=["site"], description="long description", budget="30-50k", contact_method="email", email="test@example.com")
    mock_aiosmtplib.send_message.side_effect = Exception("SMTP error")
    asyncio.run(send_notification_email(lead))

@pytest.mark.parametrize("contact_method, contact_fields", [
    ("whatsapp", {"phone": "+123"}),
    ("telegram", {"telegram": "@user"}),
    ("phone", {"phone_number": "+123", "call_time": "10:00"}),
    ("email", {"email": "test@example.com"})
])
def test_send_notification_email_content(contact_method, contact_fields, mock_aiosmtplib):
    lead_data = {"id": 1, "timestamp": datetime.now(), "name": "Test", "services": ["site"], "description": "long description", "budget": "30-50k", "contact_method": contact_method, **contact_fields}
    lead = Lead(**lead_data)
    asyncio.run(send_notification_email(lead))
    sent_msg = mock_aiosmtplib.send_message.call_args[0][0]
    assert "Новая заявка" in sent_msg["Subject"]
    body = sent_msg.get_payload()[0].get_payload(decode=True).decode('utf-8')
    assert lead.name in body
    assert contact_method in body.lower()

def test_get_leads_no_file():
    with patch("aiofiles.open", side_effect=FileNotFoundError):
        leads = asyncio.run(get_leads())
        assert leads == []

def test_get_leads_existing(mock_aiofiles_open):
    existing_leads = [{"id": 1, "timestamp": datetime.now().isoformat(), "name": "Test", "services": ["site"], "description": "long description", "budget": "30-50k", "contact_method": "email", "email": "test@example.com"}]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    leads = asyncio.run(get_leads())
    assert len(leads) == 1
    assert isinstance(leads[0], Lead)
    assert leads[0].id == 1

def test_get_leads_error(mock_aiofiles_open):
    mock_aiofiles_open.side_effect = Exception("Read error")
    with pytest.raises(Exception) as exc:
        asyncio.run(get_leads())
    assert "500" in str(exc.value.status_code)