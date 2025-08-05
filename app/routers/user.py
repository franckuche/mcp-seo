"""
Router pour les endpoints utilisateur
"""

from fastapi import APIRouter, HTTPException
from ..dependencies import haloscan_client

router = APIRouter(tags=["user"])


@router.get("/credit")
async def get_user_credit():
    """Crédits utilisateur Haloscan"""
    try:
        return await haloscan_client.request("user/credit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
