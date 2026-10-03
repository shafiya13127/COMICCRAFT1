from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse

from app.schemas import ComicRequest
from app.gemini_flash import generate_comic, GeminiServiceError
from app.exporters import save_pdf

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_FOLDER = BASE_DIR / "exports"


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post("/api/generate")
async def generate(request: ComicRequest):
    try:
        comic = generate_comic(
            prompt=request.prompt,
            style=request.style,
            language=request.language,
            panels=request.panels
        )

        return comic.model_dump()

    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {exc}"
        )


@router.post("/api/export")
async def export_pdf(payload: dict):
    try:
        EXPORT_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        path = save_pdf(payload)

        pdf_path = Path(path)

        if not pdf_path.exists():
            raise Exception(
                "PDF file was not created."
            )

        return {
            "download_url": f"/api/download/{pdf_path.name}"
        }

    except Exception as exc:
        print("PDF EXPORT ERROR:", exc)

        raise HTTPException(
            status_code=500,
            detail=f"PDF export failed: {exc}"
        )


@router.get("/api/download/{filename}")
async def download_pdf(filename: str):

    # Prevent invalid paths
    safe_filename = Path(filename).name

    pdf_path = EXPORT_FOLDER / safe_filename

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found."
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=safe_filename
    )