import aiofiles
import inspect
import asyncio
import json
from datetime import datetime
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any, Union, Awaitable
from backend.schemas import Lead, LeadCreate
from backend.config import config, logging
from fastapi import HTTPException, status
from types import TracebackType
from typing_extensions import Self


async def is_duplicate_submission(lead_data: LeadCreate) -> bool:
  try:
    leads: List[Dict[str, Any]] = []
    try:
      opener: Union[
        aiofiles.threadpool.AsyncTextIOWrapper, Awaitable[aiofiles.threadpool.AsyncTextIOWrapper]] = aiofiles.open(
        config.LEADS_FILE, 'r', encoding='utf-8'
      )
      fh: aiofiles.threadpool.AsyncTextIOWrapper = await opener if inspect.isawaitable(opener) else opener
      read_call: Union[str, Awaitable[str], None] = fh.read() if hasattr(fh, 'read') else None
      content: str = await read_call if inspect.isawaitable(read_call) else read_call
      try:
        if hasattr(fh, 'aclose'):
          await fh.aclose()
        elif hasattr(fh, 'close'):
          close_call = fh.close()
          await close_call if inspect.isawaitable(close_call) else close_call
      except Exception as e:
        logging.warning(f"Ошибка закрытия файла: {e}")
      try:
        leads = json.loads(content) if content and content.strip() else []
      except json.JSONDecodeError as e:
        logging.warning(f"Ошибка декодирования JSON: {e}")
        leads = []
    except FileNotFoundError:
      return False

    contact_value: str = ""
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

    current_time: datetime = datetime.now()
    for lead in leads:
      try:
        lead_time_str: str = lead.get('timestamp', '')
        lead_time: datetime = datetime.fromisoformat(lead_time_str)
        time_diff: float = (current_time - lead_time).total_seconds()

        if time_diff < 300 and lead.get('contact_method') == lead_data.contact_method:
          lead_contact_value: str = ""
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
      except (ValueError, TypeError) as e:
        logging.warning(f"Ошибка обработки данных заявки: {e}")
        continue

    return False
  except Exception as e:
    logging.error(f"Ошибка проверки дубликатов: {e}")
    return False


async def validate_lead_data(lead_data: LeadCreate) -> None:
  if lead_data.contact_method == 'whatsapp' and not lead_data.phone:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Введите номер WhatsApp"
    )
  elif lead_data.contact_method == 'telegram' and not lead_data.telegram:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Введите Telegram username"
    )
  elif lead_data.contact_method == 'phone' and (not lead_data.phone_number or not lead_data.call_time):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Введите номер телефона и время для звонка"
    )
  elif lead_data.contact_method == 'email' and not lead_data.email:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Введите email адрес"
    )


async def save_lead(lead_data: LeadCreate) -> Lead:
  try:
    leads: List[Dict[str, Any]] = []
    try:
      opener: Union[
        aiofiles.threadpool.AsyncTextIOWrapper, Awaitable[aiofiles.threadpool.AsyncTextIOWrapper]] = aiofiles.open(
        config.LEADS_FILE, 'r', encoding='utf-8'
      )
      fh: aiofiles.threadpool.AsyncTextIOWrapper = await opener if inspect.isawaitable(opener) else opener
      read_call: Union[str, Awaitable[str], None] = fh.read() if hasattr(fh, 'read') else None
      content: str = await read_call if inspect.isawaitable(read_call) else read_call
      try:
        if hasattr(fh, 'aclose'):
          await fh.aclose()
        elif hasattr(fh, 'close'):
          close_call = fh.close()
          await close_call if inspect.isawaitable(close_call) else close_call
      except Exception as e:
        logging.warning(f"Ошибка закрытия файла: {e}")
      try:
        leads = json.loads(content) if content and content.strip() else []
      except json.JSONDecodeError as e:
        logging.warning(f"Ошибка декодирования JSON: {e}")
        leads = []
    except FileNotFoundError:
      pass

    new_lead: Dict[str, Any] = lead_data.model_dump(exclude_none=True)
    new_lead['timestamp'] = datetime.now().isoformat()
    new_lead['id'] = len(leads) + 1
    leads.append(new_lead)

    opener_w: Union[
      aiofiles.threadpool.AsyncTextIOWrapper, Awaitable[aiofiles.threadpool.AsyncTextIOWrapper]] = aiofiles.open(
      config.LEADS_FILE, 'w', encoding='utf-8'
    )
    fh_w: aiofiles.threadpool.AsyncTextIOWrapper = await opener_w if inspect.isawaitable(opener_w) else opener_w
    write_call: Union[None, Awaitable[None]] = fh_w.write(json.dumps(leads, ensure_ascii=False, indent=2))
    if inspect.isawaitable(write_call):
      await write_call
    try:
      if hasattr(fh_w, 'aclose'):
        await fh_w.aclose()
      elif hasattr(fh_w, 'close'):
        close_call = fh_w.close()
        await close_call if inspect.isawaitable(close_call) else close_call
    except Exception as e:
      logging.warning(f"Ошибка закрытия файла: {e}")

    logging.info(f"Заявка #{new_lead['id']} сохранена успешно")
    return Lead(**new_lead)
  except Exception as e:
    logging.error(f"Ошибка сохранения заявки: {e}")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Ошибка сохранения заявки"
    )


async def send_notification_email(lead: Lead) -> None:
  try:
    services_text: str = ", ".join(lead.services)
    budget_map: Dict[str, str] = {
      '30-50k': '30-50 тыс',
      '50-150k': '50-150 тыс',
      '150-300k': '150-300 тыс',
      '300-500k': '300-500 тыс',
      '500k+': '500+ тыс'
    }
    budget_text: str = budget_map.get(lead.budget, lead.budget)

    contact_method_text: str = {
      'whatsapp': 'WhatsApp',
      'telegram': 'Telegram',
      'phone': 'Звонок',
      'email': 'Email'
    }.get(lead.contact_method, lead.contact_method)

    contact_value: str = ''
    if lead.contact_method == 'whatsapp':
      contact_value = lead.phone or ''
    elif lead.contact_method == 'telegram':
      contact_value = lead.telegram or ''
    elif lead.contact_method == 'phone':
      contact_value = f"{lead.phone_number or ''}, время: {lead.call_time or ''}"
    elif lead.contact_method == 'email':
      contact_value = lead.email or ''

    subject: str = f"Новая заявка с сайта Terrasite от {lead.name}"

    body: str = f"""
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

    msg: MIMEMultipart = MIMEMultipart()
    msg['From'] = config.FROM_EMAIL
    msg['To'] = config.TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    smtp_ctor: Union[aiosmtplib.SMTP, Awaitable[aiosmtplib.SMTP]] = aiosmtplib.SMTP(
      hostname=config.SMTP_HOST,
      port=config.SMTP_PORT,
      use_tls=True
    )
    smtp_obj: aiosmtplib.SMTP = await smtp_ctor if inspect.isawaitable(smtp_ctor) else smtp_ctor

    if hasattr(smtp_obj, "__aenter__"):
      async with smtp_obj as server:
        await server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        await server.send_message(msg)
    else:
      if hasattr(smtp_obj, 'connect'):
        connect_call = smtp_obj.connect()
        if inspect.isawaitable(connect_call):
          await connect_call
      login_call = smtp_obj.login(config.SMTP_USER, config.SMTP_PASSWORD)
      if inspect.isawaitable(login_call):
        await login_call
      send_call = smtp_obj.send_message(msg)
      if inspect.isawaitable(send_call):
        await send_call
      if hasattr(smtp_obj, 'quit'):
        quit_call = smtp_obj.quit()
        if inspect.isawaitable(quit_call):
          await quit_call

    logging.info(f"Уведомление о заявке #{lead.id} отправлено")
  except Exception as e:
    logging.error(f"Ошибка отправки уведомления: {e}")


async def get_leads() -> List[Lead]:
  try:
    opener: Union[
      aiofiles.threadpool.AsyncTextIOWrapper, Awaitable[aiofiles.threadpool.AsyncTextIOWrapper]] = aiofiles.open(
      config.LEADS_FILE, 'r', encoding='utf-8'
    )
    fh: aiofiles.threadpool.AsyncTextIOWrapper = await opener if inspect.isawaitable(opener) else opener
    read_call: Union[str, Awaitable[str], None] = fh.read() if hasattr(fh, 'read') else None
    content: str = await read_call if inspect.isawaitable(read_call) else read_call
    try:
      if hasattr(fh, 'aclose'):
        await fh.aclose()
      elif hasattr(fh, 'close'):
        close_call = fh.close()
        await close_call if inspect.isawaitable(close_call) else close_call
    except Exception as e:
      logging.warning(f"Ошибка закрытия файла: {e}")
    try:
      leads_data: List[Dict[str, Any]] = json.loads(content) if content and content.strip() else []
    except json.JSONDecodeError as e:
      logging.warning(f"Ошибка декодирования JSON: {e}")
      leads_data = []

    return [Lead(**lead) for lead in leads_data]
  except FileNotFoundError:
    return []
  except Exception as e:
    logging.error(f"Ошибка получения заявок: {e}")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Ошибка получения данных"
    )