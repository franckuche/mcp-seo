"""
Router pour les recherches SEO avancées
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from ..dependencies import get_haloscan_client, HaloscanClient

router = APIRouter()

class PositionSearchRequest(BaseModel):
    """Modèle pour la recherche par position"""
    domain: str = Field(..., description="Domaine à analyser")
    position_min: int = Field(1, ge=1, le=100, description="Position minimum (1-100)")
    position_max: int = Field(10, ge=1, le=100, description="Position maximum (1-100)")
    lang: str = Field("fr", description="Langue de recherche")
    limit: Optional[int] = Field(50, ge=1, le=500, description="Nombre max de résultats")

class KeywordGapRequest(BaseModel):
    """Modèle pour l'analyse d'écart de mots-clés"""
    domain1: str = Field(..., description="Premier domaine")
    domain2: str = Field(..., description="Deuxième domaine (concurrent)")
    lang: str = Field("fr", description="Langue de recherche")

@router.post("/search/keywords-by-position")
async def search_keywords_by_position(
    request: PositionSearchRequest,
    client: HaloscanClient = Depends(get_haloscan_client)
) -> Dict[str, Any]:
    """
    🎯 Recherche avancée : Trouve tous les mots-clés d'un domaine dans une plage de positions
    
    Exemple : Tous les mots-clés de example.com en position 5 à 10
    """
    try:
        # Validation des positions
        if request.position_min > request.position_max:
            raise HTTPException(
                status_code=400, 
                detail="La position minimum doit être inférieure à la position maximum"
            )
        
        # Appel à l'API Haloscan pour obtenir les données du domaine
        domain_data = await client.get_domains_overview(
            domain=request.domain,
            lang=request.lang
        )
        
        # Simulation de filtrage par position (à adapter selon l'API Haloscan réelle)
        # En réalité, vous devrez utiliser l'endpoint spécifique de Haloscan
        filtered_keywords = []
        
        # Si l'API retourne des mots-clés avec positions, on filtre
        if "keywords" in domain_data:
            for keyword_data in domain_data["keywords"]:
                position = keyword_data.get("position", 0)
                if request.position_min <= position <= request.position_max:
                    filtered_keywords.append({
                        "keyword": keyword_data.get("keyword", ""),
                        "position": position,
                        "search_volume": keyword_data.get("search_volume", 0),
                        "cpc": keyword_data.get("cpc", 0),
                        "competition": keyword_data.get("competition", ""),
                        "url": keyword_data.get("url", "")
                    })
        
        # Limitation des résultats
        if request.limit:
            filtered_keywords = filtered_keywords[:request.limit]
        
        return {
            "domain": request.domain,
            "position_range": f"{request.position_min}-{request.position_max}",
            "total_keywords": len(filtered_keywords),
            "keywords": filtered_keywords,
            "search_params": {
                "language": request.lang,
                "limit": request.limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche : {str(e)}")

@router.post("/search/keyword-gap")
async def analyze_keyword_gap(
    request: KeywordGapRequest,
    client: HaloscanClient = Depends(get_haloscan_client)
) -> Dict[str, Any]:
    """
    🔍 Analyse d'écart de mots-clés entre deux domaines
    
    Trouve les mots-clés où le concurrent est mieux positionné
    """
    try:
        # Obtenir les données des deux domaines
        domain1_data = await client.get_domains_overview(
            domain=request.domain1,
            lang=request.lang
        )
        
        domain2_data = await client.get_domains_overview(
            domain=request.domain2,
            lang=request.lang
        )
        
        # Analyser les écarts (logique simplifiée)
        opportunities = []
        competitor_advantages = []
        
        # Cette logique devra être adaptée selon la structure réelle des données Haloscan
        return {
            "domain1": request.domain1,
            "domain2": request.domain2,
            "opportunities": opportunities,
            "competitor_advantages": competitor_advantages,
            "analysis_summary": {
                "total_opportunities": len(opportunities),
                "competitor_stronger_keywords": len(competitor_advantages)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")

@router.post("/search/top-pages-keywords")
async def get_top_pages_keywords(
    domain: str,
    page_limit: int = 10,
    client: HaloscanClient = Depends(get_haloscan_client)
) -> Dict[str, Any]:
    """
    📄 Obtient les mots-clés des meilleures pages d'un domaine
    """
    try:
        # Obtenir les top pages du domaine
        top_pages_data = await client.get_domains_top_pages(domain=domain)
        
        # Pour chaque page, obtenir ses mots-clés principaux
        pages_with_keywords = []
        
        # Cette logique devra être adaptée selon l'API Haloscan
        return {
            "domain": domain,
            "total_pages": len(pages_with_keywords),
            "pages": pages_with_keywords[:page_limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")

@router.post("/search/bulk-position-check")
async def bulk_position_check(
    keywords: List[str],
    domain: str,
    lang: str = "fr",
    client: HaloscanClient = Depends(get_haloscan_client)
) -> Dict[str, Any]:
    """
    📊 Vérification en masse des positions d'une liste de mots-clés pour un domaine
    """
    try:
        if len(keywords) > 100:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 100 mots-clés par requête"
            )
        
        results = []
        
        # Traitement par lot des mots-clés
        for keyword in keywords:
            try:
                # Obtenir les données du mot-clé
                keyword_data = await client.get_keywords_overview(
                    keyword=keyword,
                    lang=lang
                )
                
                # Extraire la position pour le domaine spécifié
                position = None
                url = None
                
                # Cette logique devra être adaptée selon la structure des données Haloscan
                if "serp_results" in keyword_data:
                    for result in keyword_data["serp_results"]:
                        if domain in result.get("url", ""):
                            position = result.get("position")
                            url = result.get("url")
                            break
                
                results.append({
                    "keyword": keyword,
                    "position": position,
                    "url": url,
                    "found": position is not None
                })
                
            except Exception as e:
                results.append({
                    "keyword": keyword,
                    "position": None,
                    "url": None,
                    "found": False,
                    "error": str(e)
                })
        
        # Statistiques
        found_count = sum(1 for r in results if r["found"])
        avg_position = None
        if found_count > 0:
            positions = [r["position"] for r in results if r["position"]]
            avg_position = sum(positions) / len(positions) if positions else None
        
        return {
            "domain": domain,
            "total_keywords": len(keywords),
            "found_keywords": found_count,
            "not_found": len(keywords) - found_count,
            "average_position": avg_position,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification : {str(e)}")
