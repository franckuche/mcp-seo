"""
Modèles Pydantic pour l'API Haloscan
"""

from typing import List, Optional
from pydantic import BaseModel


class KeywordRequest(BaseModel):
    """Modèle pour les requêtes d'analyse de mots-clés"""
    keyword: str
    line_count: int = 20
    page: int = 1
    requested_data: Optional[List[str]] = None
    lang: str = "fr"


class DomainRequest(BaseModel):
    """Modèle pour les requêtes d'analyse de domaines"""
    domain: str
    line_count: int = 20
    requested_data: Optional[List[str]] = None


class BulkRequest(BaseModel):
    """Modèle pour les requêtes d'analyse en masse"""
    items: List[str]  # keywords ou domains
    requested_data: Optional[List[str]] = None


class BulkKeywordRequest(BaseModel):
    """Modèle pour les requêtes d'analyse de mots-clés en masse"""
    keywords: List[str]
    lang: str = "fr"
    requested_data: Optional[List[str]] = None


class PositionSearchRequest(BaseModel):
    """Modèle pour la recherche de mots-clés par plage de positions"""
    domain: str
    position_min: int = 1
    position_max: int = 10
    lang: str = "fr"
    requested_data: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Modèle pour la réponse de santé du serveur"""
    status: str
    haloscan_status: str
    credits: Optional[str] = None
    message: str
    error: Optional[str] = None
