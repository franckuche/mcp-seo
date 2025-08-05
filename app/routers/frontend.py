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
    Interface graphique principale pour le serveur MCP Haloscan
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/chat-chunked", response_class=HTMLResponse)
async def get_chat_chunked(request: Request):
    """
    Interface chat MCP avec chunking intelligent
    """
    return templates.TemplateResponse("chat_chunked.html", {"request": request})

@router.get("/ui", response_class=HTMLResponse)
async def get_ui_alias(request: Request):
    """
    Alias pour l'interface graphique
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/chat", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    """
    🤖 Interface chat MCP avec OpenAI + Haloscan
    """
    return templates.TemplateResponse("chat.html", {"request": request})
