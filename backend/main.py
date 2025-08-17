import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

try:
  from .schemas import LeadCreate, Lead
  from .services import LeadService
  from .config import config, logging
except ImportError:
  import sys
  from pathlib import Path

  sys.path.append(str(Path(__file__).parent.parent))
  from backend.schemas import LeadCreate, Lead
  from backend.services import LeadService
  from backend.config import config, logging
import aiofiles
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

BASE_DIR: Path = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
  (BASE_DIR / "data").mkdir(exist_ok=True)
  leads_file: Path = Path(config.leads_file)
  if not leads_file.exists():
    async with aiofiles.open(leads_file, mode='w', encoding='utf-8') as f:
      await f.write(json.dumps([]))
  yield


app: FastAPI = FastAPI(title="Terrasite API", lifespan=lifespan)

static_dir: Path = BASE_DIR.parent / "static"
app.mount(
  "/static",
  StaticFiles(directory=static_dir, html=True),
  name="static"
)


def get_lead_service():
  return LeadService()


@app.post("/submit-form", response_model=Lead)
async def submit_form(lead_data: LeadCreate, service: LeadService = Depends(get_lead_service)):
  try:
    logging.info(f"Получены данные формы: {lead_data.model_dump()}")
    return await service.process_lead(lead_data)
  except HTTPException as e:
    raise e
  except Exception as e:
    logging.error(f"Ошибка обработки заявки: {e}")
    raise HTTPException(status_code=500, detail="Ошибка обработки заявки")


@app.get("/admin/leads", response_model=list[Lead])
async def admin_leads(service: LeadService = Depends(get_lead_service)):
  try:
    return await service.get_all_leads()
  except Exception as e:
    logging.error(f"Ошибка получения заявок: {e}")
    raise HTTPException(status_code=500, detail="Ошибка получения данных")


@app.get("/")
async def serve_index() -> FileResponse:
  return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
  port: int = int(os.environ.get('PORT', '8000'))
  debug: bool = os.environ.get('DEBUG', 'False').lower() == 'true'
  uvicorn.run(
    app,
    port=port,
    reload=debug,
    log_level="debug" if debug else "info"
  )
