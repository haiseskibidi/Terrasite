from fastapi import APIRouter, HTTPException
from backend.schemas import LeadCreate, Lead
from backend.services import (
    is_duplicate_submission,
    validate_lead_data,
    save_lead,
    send_notification_email,
    get_leads
)
from typing import List, Dict
from datetime import datetime
from backend.config import logging

router: APIRouter = APIRouter()


@router.post("/submit-form", response_model=Dict[str, str | bool])
async def submit_form(lead_data: LeadCreate) -> Dict[str, str | bool]:
    try:
        logging.info(f"Получены данные формы: {lead_data.model_dump()}")
        await validate_lead_data(lead_data)

        if await is_duplicate_submission(lead_data):
            raise HTTPException(
                status_code=400,
                detail="Заявка с такими контактными данными уже была отправлена недавно"
            )

        lead: Lead = await save_lead(lead_data)
        await send_notification_email(lead)

        contact_info: str = ""
        if lead_data.contact_method == 'whatsapp':
            contact_info = f"WhatsApp: {lead_data.phone}"
        elif lead_data.contact_method == 'telegram':
            contact_info = f"Telegram: {lead_data.telegram}"
        elif lead_data.contact_method == 'phone':
            contact_info = f"Звонок: {lead_data.phone_number} в {lead_data.call_time}"
        elif lead_data.contact_method == 'email':
            contact_info = f"Email: {lead_data.email}"

        logging.info(f"Новая заявка обработана: {lead_data.name} ({contact_info})")

        return {"success": True, "message": "Заявка успешно отправлена"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Ошибка обработки заявки: {e}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Внутренняя ошибка сервера"}
        )


@router.get("/admin/leads", response_model=List[Lead])
async def admin_leads() -> List[Lead]:
    return await get_leads()


@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }