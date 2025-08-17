import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routers import router
from backend.config import config
import aiofiles
import json
from contextlib import asynccontextmanager

BASE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
  (BASE_DIR / "data").mkdir(exist_ok=True)

  leads_file = Path(config.LEADS_FILE)
  if not leads_file.exists():
    async with aiofiles.open(leads_file, 'w', encoding='utf-8') as f:
      await f.write(json.dumps([]))
  yield


app = FastAPI(title="Terrasite API", lifespan=lifespan)
app.include_router(router)

static_dir = BASE_DIR.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/")
async def serve_index():
  return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
  port = int(os.environ.get('PORT', 8000))
  debug = os.environ.get('DEBUG', 'False').lower() == 'true'
  uvicorn.run(
    "backend.main:app",
    port=port,
    reload=debug,
    log_level="debug" if debug else "info"
  )
