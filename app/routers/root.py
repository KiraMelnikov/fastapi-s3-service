from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index() -> str:
    return (TEMPLATES_DIR / "index.html").read_text()


@router.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"}, status_code=200)
