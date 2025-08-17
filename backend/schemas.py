from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
import re


class LeadBase(BaseModel):
  name: str = Field(..., min_length=2, max_length=50, description="Имя клиента")
  services: List[str] = Field(..., min_items=1, description="Список услуг")
  description: str = Field(..., min_length=50, max_length=2000, description="Описание проекта")
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

  @validator('name')
  def validate_name(cls, value):
    if not re.match(r'^[а-яёА-ЯЁa-zA-Z\s\-]+$', value.strip()):
      raise ValueError('Имя может содержать только буквы, пробелы и дефисы')
    return value.strip()

  @validator('description')
  def validate_description(cls, value):
    description = value.strip()
    if len(description.split()) < 8:
      raise ValueError('Описание должно содержать минимум 8 слов')
    if re.match(r'^(.)\1{20,}$', description):
      raise ValueError('Описание содержит слишком много повторяющихся символов')
    return description

  @validator('phone')
  def validate_phone(cls, value):
    if value is None:
      return value
    phone_clean = re.sub(r'[\s\-()]', '', value)
    if not re.match(r'^(\+7|8)\d{10}$', phone_clean):
      raise ValueError('Некорректный формат номера телефона')
    return value

  @validator('phone_number')
  def validate_phone_number(cls, value):
    if value is None:
      return value
    phone_clean = re.sub(r'[\s\-()]', '', value)
    if not re.match(r'^(\+7|8)\d{10}$', phone_clean):
      raise ValueError('Некорректный формат номера телефона')
    return value

  @validator('telegram')
  def validate_telegram(cls, value):
    if value is None:
      return value
    if not re.match(r'^@[a-zA-Z0-9_]{5,32}$', value):
      raise ValueError('Некорректный формат Telegram username')
    return value

  @validator('call_time')
  def validate_call_time(cls, value):
    if value is None:
      return value
    if len(value.strip()) < 5:
      raise ValueError('Укажите время для звонка более подробно')
    return value.strip()


class LeadCreate(LeadBase):
  pass


class Lead(LeadBase):
  id: int
  timestamp: datetime

  @validator('timestamp', pre=True)
  def parse_timestamp(cls, v):
    if isinstance(v, str):
      return datetime.fromisoformat(v)
    return v

  class Config:
    from_attributes = True
