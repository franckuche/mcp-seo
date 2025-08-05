"""
Router pour la santé du serveur et monitoring
"""
from fastapi import APIRouter, HTTPException, Depends
from ..models import HealthResponse
from ..dependencies import haloscan_client
from ..logging_config import get_logger

logger = get_logger("health")
from ..config import Config

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    ❤️ Vérification de la santé du serveur et des crédits Haloscan
    """
    logger.info("🏥 Début vérification santé du serveur")
    
    try:
        # Test de base du serveur
        server_status = "healthy"
        logger.info("✅ Serveur en bonne santé")
        
        # Test de connexion Haloscan
        haloscan_status = "unknown"
        credits = None
        
        try:
            logger.info("🔗 Test de connexion Haloscan...")
            credit_data = await haloscan_client.request("user/credit")
            haloscan_status = "connected"
            credits = credit_data.get("credits", "N/A")
            logger.info(f"✅ Connexion Haloscan OK - Crédits: {credits}")
        except Exception as e:
            haloscan_status = f"error: {str(e)}"
            logger.error(f"❌ Erreur connexion Haloscan: {e}")
        
        response = HealthResponse(
            status=server_status,
            haloscan_status=haloscan_status,
            credits=credits,
            message="Serveur MCP Haloscan opérationnel"
        )
        
        logger.info(f"🏥 Santé vérifiée avec succès: {response.dict()}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification de santé: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de santé: {str(e)}")
