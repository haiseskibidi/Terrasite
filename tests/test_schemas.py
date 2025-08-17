import pytest
from backend.schemas import LeadBase, LeadCreate, Lead
from pydantic import ValidationError
from datetime import datetime


@pytest.mark.parametrize(
    "valid_data",
    [
        {
            "name": "Test",
            "services": ["site"],
            "description": "Long description with enough words to pass validation",
            "budget": "30-50k",
            "contact_method": "email",
            "email": "test@example.com"
        },
        {
            "name": "Test",
            "services": ["bot"],
            "description": "Another description with enough words to pass validation",
            "budget": "500k+",
            "contact_method": "whatsapp",
            "phone": "+79261234567"
        }
    ]
)
def test_lead_base_valid(valid_data):
    lead = LeadBase(**valid_data)
    assert lead.name == valid_data["name"]
    assert lead.services == valid_data["services"]


@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        (
            {
                "name": "",
                "services": ["site"],
                "description": "desc long enough to pass",
                "budget": "30-50k",
                "contact_method": "email",
                "email": "test@example.com"
            },
            "string_too_short"
        ),
        (
            {
                "name": "Test",
                "services": [],
                "description": "desc long enough to pass",
                "budget": "30-50k",
                "contact_method": "email",
                "email": "test@example.com"
            },
            "too_short"
        ),
        (
            {
                "name": "Test",
                "services": ["site"],
                "description": "short",
                "budget": "30-50k",
                "contact_method": "email",
                "email": "test@example.com"
            },
            "Description must contain at least 8 words"
        ),
        (
            {
                "name": "Test",
                "services": ["site"],
                "description": "desc long enough to pass",
                "budget": "invalid",
                "contact_method": "email",
                "email": "test@example.com"
            },
            "Недопустимый бюджет"
        ),
        (
            {
                "name": "Test",
                "services": ["site"],
                "description": "desc long enough to pass",
                "budget": "30-50k",
                "contact_method": "invalid",
                "email": "test@example.com"
            },
            "Недопустимый способ связи"
        ),
        (
            {
                "name": "Test",
                "services": ["site"],
                "description": "desc long enough to pass",
                "budget": "30-50k",
                "contact_method": "email",
                "email": "invalid"
            },
            "value is not a valid email address"
        ),
    ]
)
def test_lead_base_invalid(invalid_data, expected_error):
    with pytest.raises(ValidationError) as exc:
        LeadBase(**invalid_data)
    assert expected_error in str(exc.value)


def test_lead_create():
    data = {
        "name": "Test",
        "services": ["site"],
        "description": "Description long enough to pass validation",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com",
        "phone": None,
        "telegram": None,
        "phone_number": None,
        "call_time": None
    }
    lead_create = LeadCreate(**data)
    assert lead_create.model_dump(exclude_none=True) == {
        "name": "Test",
        "services": ["site"],
        "description": "Description long enough to pass validation",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com"
    }


def test_lead():
    data = {
        "id": 1,
        "timestamp": datetime.now(),
        "name": "Test",
        "services": ["site"],
        "description": "Description long enough to pass validation",
        "budget": "30-50k",
        "contact_method": "email",
        "email": "test@example.com",
        "phone": None,
        "telegram": None,
        "phone_number": None,
        "call_time": None
    }
    lead = Lead(**data)
    assert lead.id == 1
    assert isinstance(lead.timestamp, datetime)