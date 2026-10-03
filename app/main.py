from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.routes import router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Text-only AI Comic Story Creator using Gemini",
    version="2.0.0",
)

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)

app.state.templates = templates

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name
    }