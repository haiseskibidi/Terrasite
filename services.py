import aiofiles
import json
from datetime import datetime
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from schemas import Lead, LeadCreate
from config import config, logging
from fastapi import HTTPException, status


async def is_duplicate_submission(lead_data: LeadCreate) -> bool:
  try:
    leads: List[dict] = []
    try:
      async with aiofiles.open(config.LEADS_FILE, 'r', encoding='utf-8') as f:
        content = await f.read()
        leads = json.loads(content)
    except FileNotFoundError:
      return False

    contact_value = ""
    if lead_data.contact_method == 'whatsapp':
      contact_value = lead_data.phone or ''
    elif lead_data.contact_method == 'telegram':
      contact_value = lead_data.telegram or ''
    elif lead_data.contact_method == 'phone':
      contact_value = lead_data.phone_number or ''
    elif lead_data.contact_method == 'email':
      contact_value = lead_data.email or ''

    if not contact_value:
      return False

    current_time = datetime.now()
    for lead in leads:
      try:
        lead_time = datetime.fromisoformat(lead.get('timestamp', ''))
        time_diff = (current_time - lead_time).total_seconds()

        if time_diff < 300 and lead.get('contact_method') == lead_data.contact_method:
          lead_contact_value = ""
          if lead_data.contact_method == 'whatsapp':
            lead_contact_value = lead.get('phone', '')
          elif lead_data.contact_method == 'telegram':
            lead_contact_value = lead.get('telegram', '')
          elif lead_data.contact_method == 'phone':
            lead_contact_value = lead.get('phone_number', '')
          elif lead_data.contact_method == 'email':
            lead_contact_value = lead.get('email', '')

          if lead_contact_value.lower().strip() == contact_value.lower().strip():
            return True
      except (ValueError, TypeError):
        continue

    return False
  except Exception as e:
    logging.error(f"Ошибка проверки дубликатов: {e}")
    return False


async def validate_lead_data(lead_data: LeadCreate):
  if lead_data.contact_method == 'whatsapp' and not lead_data.phone:
    raise HTTPException(status_code=400, detail="Введите номер WhatsApp")
  elif lead_data.contact_method == 'telegram' and not lead_data.telegram:
    raise HTTPException(status_code=400, detail="Введите Telegram username")
  elif lead_data.contact_method == 'phone' and (not lead_data.phone_number or not lead_data.call_time):
    raise HTTPException(status_code=400, detail="Введите номер телефона и время для звонка")
  elif lead_data.contact_method == 'email' and not lead_data.email:
    raise HTTPException(status_code=400, detail="Введите email адрес")


async def save_lead(lead_data: LeadCreate) -> Lead:
  try:
    leads: List[dict] = []
    try:
      async with aiofiles.open(config.LEADS_FILE, 'r', encoding='utf-8') as f:
        content = await f.read()
        leads = json.loads(content)
    except FileNotFoundError:
      pass

    new_lead = lead_data.model_dump(exclude_none=True)
    new_lead['timestamp'] = datetime.now().isoformat()
    new_lead['id'] = len(leads) + 1
    leads.append(new_lead)

    async with aiofiles.open(config.LEADS_FILE, 'w', encoding='utf-8') as f:
      await f.write(json.dumps(leads, ensure_ascii=False, indent=2))

    logging.info(f"Заявка #{new_lead['id']} сохранена успешно")
    return Lead(**new_lead)
  except Exception as e:
    logging.error(f"Ошибка сохранения заявки: {e}")
    raise HTTPException(status_code=500, detail="Ошибка сохранения заявки")


async def send_notification_email(lead: Lead):
  try:
    services_text = ", ".join(lead.services)
    budget_map = {
      '30-50k': '30-50 тыс',
      '50-150k': '50-150 тыс',
      '150-300k': '150-300 тыс',
      '300-500k': '300-500 тыс',
      '500k+': '500+ тыс'
    }
    budget_text = budget_map.get(lead.budget, lead.budget)

    contact_method_text = {
      'whatsapp': 'WhatsApp',
      'telegram': 'Telegram',
      'phone': 'Звонок',
      'email': 'Email'
    }.get(lead.contact_method, lead.contact_method)

    contact_value = ''
    if lead.contact_method == 'whatsapp':
      contact_value = lead.phone or ''
    elif lead.contact_method == 'telegram':
      contact_value = lead.telegram or ''
    elif lead.contact_method == 'phone':
      contact_value = f"{lead.phone_number or ''}, время: {lead.call_time or ''}"
    elif lead.contact_method == 'email':
      contact_value = lead.email or ''

    subject = f"Новая заявка с сайта Terrasite от {lead.name}"

    body = f"""
Новая заявка с сайта Terrasite!

Контактная информация:
Имя: {lead.name}
Способ связи: {contact_method_text}
Контакт: {contact_value}

Детали проекта:
Услуги: {services_text}
Бюджет: {budget_text}

Описание проекта:
{lead.description}

Время подачи заявки: {lead.timestamp.strftime('%d.%m.%Y %H:%M')}

---
Отправлено автоматически с сайта Terrasite
        """.strip()

    msg = MIMEMultipart()
    msg['From'] = config.FROM_EMAIL
    msg['To'] = config.TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    async with aiosmtplib.SMTP(hostname=config.SMTP_HOST, port=config.SMTP_PORT, use_tls=True) as server:
      await server.login(config.SMTP_USER, config.SMTP_PASSWORD)
      await server.send_message(msg)

    logging.info(f"Уведомление о заявке #{lead.id} отправлено")
  except Exception as e:
    logging.error(f"Ошибка отправки уведомления: {e}")


async def get_leads() -> List[Lead]:
  try:
    async with aiofiles.open(config.LEADS_FILE, 'r', encoding='utf-8') as f:
      content = await f.read()
      leads_data = json.loads(content)
      return [Lead(**lead) for lead in leads_data]
  except FileNotFoundError:
    return []
  except Exception as e:
    logging.error(f"Ошибка получения заявок: {e}")
    raise HTTPException(status_code=500, detail="Ошибка получения данных")