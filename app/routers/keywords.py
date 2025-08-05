"""
Router pour les endpoints liés aux mots-clés
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ..models import KeywordRequest, BulkRequest
from ..dependencies import haloscan_client
from ..logging_config import get_logger

logger = get_logger("keywords")

router = APIRouter(tags=["keywords"])


@router.post("/overview")
async def analyze_keyword(request: KeywordRequest):
    """Analyse complète d'un mot-clé"""
    try:
        data = {
            "keyword": request.keyword,
            "requested_data": request.requested_data or ["metrics", "serp", "related_search"],
            "lang": request.lang
        }
        return await haloscan_client.request("keywords/overview", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match")
async def search_keywords(request: KeywordRequest):
    """Recherche de mots-clés par correspondance"""
    try:
        data = {
            "keyword": request.keyword,
            "lineCount": request.line_count,
            "page": request.page
        }
        return await haloscan_client.request("keywords/match", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/similar")
async def get_similar_keywords(request: KeywordRequest):
    """Mots-clés similaires"""
    try:
        data = {
            "keyword": request.keyword,
            "lineCount": request.line_count,
            "page": request.page
        }
        return await haloscan_client.request("keywords/similar", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions")
async def get_keyword_questions(request: KeywordRequest):
    """Questions liées au mot-clé"""
    try:
        data = {
            "keyword": request.keyword,
            "lineCount": request.line_count
        }
        return await haloscan_client.request("keywords/questions", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk")
async def analyze_keywords_bulk(request: BulkRequest):
    """Analyse groupée de mots-clés"""
    try:
        data = {
            "keywords": request.items,
            "requestedData": request.requested_data or ["metrics"]
        }
        return await haloscan_client.request("keywords/bulk", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
