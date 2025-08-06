"""
Modèles Pydantic pour l'API MCP Chat
"""

from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Modèle pour la réponse de santé du serveur"""
    status: str
    haloscan_status: str
    credits: Optional[str] = None
    message: str
    error: Optional[str] = None
