from datetime import datetime
from pydantic import ValidationError
import pytest
from backend.schemas import LeadBase, LeadCreate, Lead


def test_lead_base_valid():
  data = {
    "name": "Test",
    "services": ["site"],
    "description": "long description with enough words to pass validation",
    "budget": "30-50k",
    "contact_method": "email",
    "email": "test@example.com"
  }
  lead_base = LeadBase(**data)
  assert lead_base.name == "Test"
  assert lead_base.services == ["site"]
  assert lead_base.description == "long description with enough words to pass validation"
  assert lead_base.budget == "30-50k"
  assert lead_base.contact_method == "email"
  assert lead_base.email == "test@example.com"


@pytest.mark.parametrize(
  "invalid_data, expected_error",
  [
    (
        {
          "name": "",
          "services": ["site"],
          "description": "long description with enough words to pass validation",
          "budget": "30-50k",
          "contact_method": "email",
          "email": "test@example.com"
        },
        "Имя может содержать только буквы, пробелы и дефисы"
    ),
    (
        {
          "name": "Test",
          "services": [],
          "description": "long description with enough words to pass validation",
          "budget": "30-50k",
          "contact_method": "email",
          "email": "test@example.com"
        },
        "List should have at least 1 item"
    ),
    (
        {
          "name": "Test",
          "services": ["site"],
          "description": "short desc",
          "budget": "30-50k",
          "contact_method": "email",
          "email": "test@example.com"
        },
        "Описание должно содержать минимум 8 слов"
    ),
    (
        {
          "name": "Test",
          "services": ["site"],
          "description": "long description with enough words to pass validation",
          "budget": "invalid",
          "contact_method": "email",
          "email": "test@example.com"
        },
        "Недопустимый бюджет: invalid"
    ),
    (
        {
          "name": "Test",
          "services": ["site"],
          "description": "long description with enough words to pass validation",
          "budget": "30-50k",
          "contact_method": "invalid",
          "email": "test@example.com"
        },
        "Недопустимый способ связи: invalid"
    ),
    (
        {
          "name": "Test",
          "services": ["site"],
          "description": "long description with enough words to pass validation",
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
    "description": "long description with enough words to pass validation",
    "budget": "30-50k",
    "contact_method": "email",
    "email": "test@example.com",
    "phone": None,
    "telegram": None,
    "phone_number": None,
    "call_time": None
  }
  lead_create = LeadCreate(**data)
  assert lead_create.name == "Test"
  assert lead_create.services == ["site"]
  assert lead_create.description == "long description with enough words to pass validation"
  assert lead_create.budget == "30-50k"
  assert lead_create.contact_method == "email"
  assert lead_create.email == "test@example.com"


def test_lead():
  data = {
    "id": 1,
    "timestamp": datetime.now(),
    "name": "Test",
    "services": ["site"],
    "description": "long description with enough words to pass validation",
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
  assert lead.name == "Test"
  assert lead.services == ["site"]
  assert lead.description == "long description with enough words to pass validation"
  assert lead.budget == "30-50k"
  assert lead.contact_method == "email"
  assert lead.email == "test@example.com"
