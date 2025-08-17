import aiofiles
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import json
from .schemas import Lead, LeadCreate
from .config import config, logging
from fastapi import HTTPException, status

class ILeadRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def add(self, lead_data: Dict[str, Any]) -> None:
        pass

class JsonLeadRepository(ILeadRepository):
    def __init__(self, file_path: str):
        self._file_path = file_path

    async def _read_leads(self) -> List[Dict[str, Any]]:
        try:
            async with aiofiles.open(self._file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content) if content.strip() else []
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            logging.warning(f"Ошибка декодирования JSON: {e}")
            return []

    async def _write_leads(self, leads: List[Dict[str, Any]]) -> None:
        async with aiofiles.open(self._file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(leads, ensure_ascii=False, indent=2))

    async def get_all(self) -> List[Dict[str, Any]]:
        return await self._read_leads()

    async def add(self, lead_data: Dict[str, Any]) -> None:
        leads = await self._read_leads()
        leads.append(lead_data)
        await self._write_leads(leads)

class ILeadValidator(ABC):
    @abstractmethod
    async def validate(self, lead_data: LeadCreate) -> None:
        pass

class ContactMethodValidator(ILeadValidator):
    async def validate(self, lead_data: LeadCreate) -> None:
        if lead_data.contact_method == 'whatsapp' and not lead_data.phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Введите номер WhatsApp")
        elif lead_data.contact_method == 'telegram' and not lead_data.telegram:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Введите Telegram username")
        elif lead_data.contact_method == 'phone' and (not lead_data.phone_number or not lead_data.call_time):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Введите номер телефона и время для звонка")
        elif lead_data.contact_method == 'email' and not lead_data.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Введите email адрес")

class IDuplicateChecker(ABC):
    @abstractmethod
    async def is_duplicate(self, lead_data: LeadCreate) -> bool:
        pass

class TimeBasedDuplicateChecker(IDuplicateChecker):
    def __init__(self, repository: ILeadRepository, duplicate_window: timedelta = timedelta(minutes=5)):
        self._repository = repository
        self._duplicate_window = duplicate_window

    def _get_contact_value(self, lead_data: LeadCreate | Dict[str, Any]) -> str:
        if lead_data.contact_method == 'whatsapp':
            return lead_data.phone or '' if isinstance(lead_data, LeadCreate) else lead_data.get('phone', '')
        elif lead_data.contact_method == 'telegram':
            return lead_data.telegram or '' if isinstance(lead_data, LeadCreate) else lead_data.get('telegram', '')
        elif lead_data.contact_method == 'phone':
            return lead_data.phone_number or '' if isinstance(lead_data, LeadCreate) else lead_data.get('phone_number', '')
        elif lead_data.contact_method == 'email':
            return lead_data.email or '' if isinstance(lead_data, LeadCreate) else lead_data.get('email', '')
        return ''

    async def is_duplicate(self, lead_data: LeadCreate) -> bool:
        leads = await self._repository.get_all()
        contact_value = self._get_contact_value(lead_data).lower().strip()
        if not contact_value:
            return False

        for lead in leads:
            lead_time = datetime.fromisoformat(lead["timestamp"])
            if (datetime.now() - lead_time) < self._duplicate_window:
                if lead["contact_method"] == lead_data.contact_method:
                    lead_contact_value = self._get_contact_value(lead).lower().strip()
                    if lead_contact_value == contact_value:
                        return True
        return False

class INotifier(ABC):
    @abstractmethod
    async def notify(self, lead: Lead) -> None:
        pass

class EmailNotifier(INotifier):
    def __init__(self, smtp_host: str = config.smtp_host, smtp_port: int = config.smtp_port,
                 smtp_user: str = config.smtp_user, smtp_password: str = config.smtp_password,
                 from_email: str = config.from_email, to_email: str = config.to_email):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._from_email = from_email
        self._to_email = to_email

    async def notify(self, lead: Lead) -> None:
        services_text = ", ".join(lead.services)
        budget_map: Dict[str, str] = {
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
        msg['From'] = self._from_email
        msg['To'] = self._to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        async with aiosmtplib.SMTP(hostname=self._smtp_host, port=self._smtp_port, use_tls=True) as server:
            await server.login(self._smtp_user, self._smtp_password)
            await server.send_message(msg)

        logging.info(f"Уведомление о заявке #{lead.id} отправлено")

class LeadService:
    def __init__(self):
        self._repository: ILeadRepository = JsonLeadRepository(str(config.leads_file))
        self._validator: ILeadValidator = ContactMethodValidator()
        self._duplicate_checker: IDuplicateChecker = TimeBasedDuplicateChecker(self._repository)
        self._notifier: INotifier = EmailNotifier(
            config.smtp_host, config.smtp_port, config.smtp_user,
            config.smtp_password, config.from_email, config.to_email
        )

    async def process_lead(self, lead_data: LeadCreate) -> Lead:
        try:
            await self._validator.validate(lead_data)

            if await self._duplicate_checker.is_duplicate(lead_data):
                raise HTTPException(status_code=400, detail="Заявка с такими контактными данными уже была отправлена недавно")

            new_lead_data = lead_data.model_dump(exclude_none=True)
            new_lead_data['timestamp'] = datetime.now().isoformat()
            leads = await self._repository.get_all()
            new_lead_data['id'] = len(leads) + 1

            await self._repository.add(new_lead_data)

            lead = Lead(**new_lead_data)
            await self._notifier.notify(lead)

            logging.info(f"Заявка #{lead.id} сохранена и обработана успешно")
            return lead
        except HTTPException as e:
            raise e
        except Exception as e:
            logging.error(f"Ошибка обработки заявки: {e}")
            raise HTTPException(status_code=500, detail="Ошибка обработки заявки")

    async def get_all_leads(self) -> List[Lead]:
        try:
            leads_data = await self._repository.get_all()
            return [Lead(**lead) for lead in leads_data]
        except Exception as e:
            logging.error(f"Ошибка получения заявок: {e}")
            raise HTTPException(status_code=500, detail="Ошибка получения данных")