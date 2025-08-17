from fastapi import APIRouter, HTTPException, Depends
from .schemas import LeadCreate, Lead
from .services import LeadService
from typing import List, Dict
from datetime import datetime
from .config import logging
from fastapi import status

router: APIRouter = APIRouter()


async def get_lead_service() -> LeadService:
    return LeadService()


@router.post("/submit-form", response_model=Dict[str, str | bool])
async def submit_form(
    lead_data: LeadCreate,
    lead_service: LeadService = Depends(get_lead_service)
) -> Dict[str, str | bool]:
    try:
        logging.info(f"Получены данные формы: {lead_data.model_dump()}")
        lead = await lead_service.process_lead(lead_data)

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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "error": "Внутренняя ошибка сервера"}
        )


@router.get("/admin/leads", response_model=List[Lead])
async def admin_leads(
    lead_service: LeadService = Depends(get_lead_service)
) -> List[Lead]:
    return await lead_service.get_all_leads()


@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }