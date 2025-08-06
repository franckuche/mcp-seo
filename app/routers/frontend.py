"""
Router pour l'interface graphique web
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Configuration des templates
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/", response_class=HTMLResponse)
async def get_frontend(request: Request):
    """
    Interface chat MCP avec chunking intelligent - Page principale
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/health-ui", response_class=HTMLResponse)
async def get_health_ui(request: Request):
    """
    Interface de monitoring (alias vers la page principale)
    """
    return templates.TemplateResponse("index.html", {"request": request})
