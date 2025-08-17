from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime

class LeadBase(BaseModel):
    name: str = Field(..., min_length=1, description="Имя клиента")
    services: List[str] = Field(..., min_items=1, description="Список услуг")
    description: str = Field(..., min_length=10, description="Описание проекта")
    budget: str = Field(..., description="Бюджет проекта")
    contact_method: str = Field(..., description="Способ связи")

    phone: Optional[str] = Field(None, description="Номер WhatsApp")
    telegram: Optional[str] = Field(None, description="Telegram username")
    phone_number: Optional[str] = Field(None, description="Номер телефона")
    call_time: Optional[str] = Field(None, description="Время звонка")
    email: Optional[EmailStr] = Field(None, description="Email клиента")

    @validator('budget')
    def validate_budget(cls, value):
        allowed = ['30-50k', '50-150k', '150-300k', '300-500k', '500k+']
        if value not in allowed:
            raise ValueError(f'Недопустимый бюджет: {value}')
        return value

    @validator('contact_method')
    def validate_contact_method(cls, value):
        allowed = ['whatsapp', 'telegram', 'phone', 'email']
        if value not in allowed:
            raise ValueError(f'Недопустимый способ связи: {value}')
        return value

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True