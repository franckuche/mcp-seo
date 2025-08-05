"""
Router pour les endpoints liés aux domaines
"""

from fastapi import APIRouter, HTTPException
from ..models import DomainRequest, BulkRequest
from ..dependencies import haloscan_client

router = APIRouter(tags=["domains"])


@router.post("/overview")
async def analyze_domain(request: DomainRequest):
    """Analyse SEO complète d'un domaine"""
    try:
        data = {
            "domain": request.domain,
            "requestedData": request.requested_data or ["traffic", "visibility", "top_pages"]
        }
        return await haloscan_client.request("domains/overview", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitors")
async def get_domain_competitors(request: DomainRequest):
    """Concurrents organiques du domaine"""
    try:
        data = {
            "domain": request.domain,
            "lineCount": request.line_count
        }
        return await haloscan_client.request("domains/competitors", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/top-pages")
async def get_domain_top_pages(request: DomainRequest):
    """Pages les plus performantes"""
    try:
        data = {
            "domain": request.domain,
            "lineCount": request.line_count
        }
        return await haloscan_client.request("domains/top-pages", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk")
async def analyze_domains_bulk(request: BulkRequest):
    """Analyse groupée de domaines"""
    try:
        data = {
            "domains": request.items,
            "requestedData": request.requested_data or ["overview"]
        }
        return await haloscan_client.request("domains/bulk", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
