import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import router
from config import config
import aiofiles
import json
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(config.LEADS_FILE):
        async with aiofiles.open(config.LEADS_FILE, 'w', encoding='utf-8') as f:
            await f.write(json.dumps([]))
    yield

app = FastAPI(title="Terrasite API", lifespan=lifespan)

app.include_router(router)

app.mount("/static", StaticFiles(directory=".", html=True), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("index.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    uvicorn.run(app, port=port, log_level="debug" if debug else "info")