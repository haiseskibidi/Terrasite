import pytest
import pytest_asyncio
import json
from backend.services import (
    JsonLeadRepository,
    ContactMethodValidator,
    TimeBasedDuplicateChecker,
    EmailNotifier,
    LeadService
)
from backend.schemas import LeadCreate, Lead
from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_json_lead_repository_no_file(mock_aiofiles_open):
    repo = JsonLeadRepository("leads.json")
    mock_aiofiles_open.side_effect = FileNotFoundError
    leads = await repo.get_all()
    assert leads == []


@pytest.mark.asyncio
async def test_json_lead_repository_existing(mock_aiofiles_open):
    repo = JsonLeadRepository("leads.json")
    existing_leads = [{
        "id": 1,
        "timestamp": datetime.now().isoformat(),
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation for the test case",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    leads = await repo.get_all()
    assert len(leads) == 1
    assert leads[0]["id"] == 1


@pytest.mark.asyncio
async def test_json_lead_repository_add(mock_aiofiles_open):
    repo = JsonLeadRepository("leads.json")
    lead_data = {
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation for the test case",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }
    mock_read_file = AsyncMock()
    mock_read_file.read.side_effect = FileNotFoundError
    mock_write_file = AsyncMock()
    mock_aiofiles_open.side_effect = [mock_read_file, mock_write_file]

    await repo.add(lead_data)
    mock_write_file.write.assert_called_once()


@pytest.mark.asyncio
async def test_contact_method_validator_valid():
    validator = ContactMethodValidator()
    lead_data = LeadCreate(
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="email",
        email="test@example.com"
    )
    await validator.validate(lead_data)


@pytest.mark.parametrize(
    "contact_method, missing_field",
    [
        ("whatsapp", "phone"),
        ("telegram", "telegram"),
        ("phone", "phone_number"),
        ("phone", "call_time"),
        ("email", "email")
    ]
)
@pytest.mark.asyncio
async def test_contact_method_validator_missing(contact_method, missing_field):
    validator = ContactMethodValidator()
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "description long enough to pass validation for the test case to ensure it works",
        "budget": "30-50k",
        "contact_method": contact_method
    }
    if missing_field != "call_time" and contact_method == "phone":
        data["call_time"] = "10:00"
    elif missing_field != "phone_number" and contact_method == "phone":
        data["phone_number"] = "+79261234567"
    with pytest.raises(HTTPException):
        lead_data = LeadCreate(**data)
        await validator.validate(lead_data)


@pytest.mark.asyncio
async def test_time_based_duplicate_checker_no_file(mock_aiofiles_open):
    repo = JsonLeadRepository("leads.json")
    checker = TimeBasedDuplicateChecker(repo)
    lead_data = LeadCreate(
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="email",
        email="test@example.com"
    )
    mock_aiofiles_open.side_effect = FileNotFoundError
    result = await checker.is_duplicate(lead_data)
    assert result == False


@pytest.mark.asyncio
async def test_time_based_duplicate_checker_duplicate(mock_aiofiles_open):
    repo = JsonLeadRepository("leads.json")
    checker = TimeBasedDuplicateChecker(repo)
    lead_data = LeadCreate(
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="email",
        email="test@example.com"
    )
    existing_leads = [{
        "id": 1,
        "timestamp": (datetime.now() - timedelta(seconds=1)).isoformat(),
        "contact_method": "email",
        "email": "test@example.com"
    }]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    result = await checker.is_duplicate(lead_data)
    assert result == True


@pytest.mark.asyncio
async def test_time_based_duplicate_checker_not_duplicate_time(mock_aiofiles_open):
    repo = JsonLeadRepository("leads.json")
    checker = TimeBasedDuplicateChecker(repo)
    lead_data = LeadCreate(
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="email",
        email="test@example.com"
    )
    existing_leads = [{
        "id": 1,
        "timestamp": (datetime.now() - timedelta(minutes=6)).isoformat(),
        "contact_method": "email",
        "email": "test@example.com"
    }]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    result = await checker.is_duplicate(lead_data)
    assert result == False


@pytest.mark.asyncio
async def test_time_based_duplicate_checker_different_method(mock_aiofiles_open):
    repo = JsonLeadRepository("leads.json")
    checker = TimeBasedDuplicateChecker(repo)
    lead_data = LeadCreate(
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="whatsapp",
        phone="+79261234567"
    )
    existing_leads = [{
        "id": 1,
        "timestamp": datetime.now().isoformat(),
        "contact_method": "email",
        "email": "test@example.com"
    }]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    result = await checker.is_duplicate(lead_data)
    assert result == False


@pytest.mark.asyncio
async def test_time_based_duplicate_checker_no_contact_value():
    repo = JsonLeadRepository("leads.json")
    checker = TimeBasedDuplicateChecker(repo)
    lead_data = LeadCreate(
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="email"
    )
    result = await checker.is_duplicate(lead_data)
    assert result == False


@pytest.mark.asyncio
async def test_email_notifier(mock_aiosmtplib):
    notifier = EmailNotifier(
        smtp_host="smtp.test.com",
        smtp_port=587,
        smtp_user="user",
        smtp_password="pass",
        from_email="from@test.com",
        to_email="to@test.com"
    )
    lead = Lead(
        id=1,
        timestamp=datetime.now(),
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="email",
        email="test@example.com"
    )
    await notifier.notify(lead)
    mock_aiosmtplib.login.assert_called_once()
    mock_aiosmtplib.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_email_notifier_content(mock_aiosmtplib):
    notifier = EmailNotifier(
        smtp_host="smtp.test.com",
        smtp_port=587,
        smtp_user="user",
        smtp_password="pass",
        from_email="from@test.com",
        to_email="to@test.com"
    )
    lead = Lead(
        id=1,
        timestamp=datetime.now(),
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="email",
        email="test@example.com"
    )
    await notifier.notify(lead)
    sent_msg = mock_aiosmtplib.send_message.call_args[0][0]
    assert "Новая заявка" in sent_msg["Subject"]
    body = sent_msg.get_payload()[0].get_payload(decode=True).decode('utf-8')
    assert lead.name in body
    assert "email" in body.lower()


@pytest.mark.asyncio
async def test_lead_service_process_lead(mock_aiofiles_open, mock_aiosmtplib):
    service = LeadService()
    lead_data = LeadCreate(
        name="Test",
        services=["site"],
        description="long description with enough words to pass validation for the test case",
        budget="30-50k",
        contact_method="email",
        email="test@example.com"
    )
    mock_read_file = AsyncMock()
    mock_read_file.read.side_effect = FileNotFoundError
    mock_write_file = AsyncMock()
    mock_aiofiles_open.side_effect = [mock_read_file, mock_write_file]

    lead = await service.process_lead(lead_data)
    assert lead.id == 1
    assert mock_write_file.write.called
    assert mock_aiosmtplib.send_message.called


@pytest.mark.asyncio
async def test_lead_service_get_all_leads(mock_aiofiles_open):
    service = LeadService()
    existing_leads = [{
        "id": 1,
        "timestamp": datetime.now().isoformat(),
        "name": "Test",
        "services": ["site"],
        "description": "long description with enough words to pass validation for the test case",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }]
    mock_file = AsyncMock()
    mock_file.read.return_value = json.dumps(existing_leads)
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    leads = await service.get_all_leads()
    assert len(leads) == 1
    assert isinstance(leads[0], Lead)
    assert leads[0].id == 1