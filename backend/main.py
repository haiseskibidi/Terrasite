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
from typing import AsyncGenerator, Any

BASE_DIR: Path = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    (BASE_DIR / "data").mkdir(exist_ok=True)

    leads_file: Path = Path(config.LEADS_FILE)
    if not leads_file.exists():
        async with aiofiles.open(leads_file, mode='w', encoding='utf-8') as f:
            await f.write(json.dumps([]))
    yield


app: FastAPI = FastAPI(title="Terrasite API", lifespan=lifespan)
app.include_router(router)

static_dir: Path = BASE_DIR.parent / "static"
app.mount(
    "/static",
    StaticFiles(directory=static_dir, html=True),
    name="static"
)


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
    port: int = int(os.environ.get('PORT', '8000'))
    debug: bool = os.environ.get('DEBUG', 'False').lower() == 'true'
    uvicorn.run(
        "backend.main:app",
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )