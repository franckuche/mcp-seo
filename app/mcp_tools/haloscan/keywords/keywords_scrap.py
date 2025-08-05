"""
MCP Tool pour l'endpoint Haloscan keywords/scrap
Permet de demander le rafraîchissement des données pour une liste de mots-clés
"""

from typing import Dict, Any, List
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("keywords_scrap_tool")

class KeywordsScrapTool(BaseMCPTool):
    """Outil MCP pour demander le rafraîchissement des données de mots-clés via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "keywordsscrap"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour le rafraîchissement des données de mots-clés"""
        return {
            "type": "function",
            "function": {
                "name": "keywords_scrap",
                "description": "Request data refresh for a list of keywords. This triggers scraping of fresh SERP data for the specified keywords. Uses 1 refresh credit per keyword.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of keywords to refresh/scrap (e.g., ['seo tools', 'marketing digital'])",
                            "minItems": 1,
                            "maxItems": 50
                        }
                    },
                    "required": ["keywords"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute la demande de rafraîchissement des données de mots-clés"""
        try:
            # Validation des paramètres
            keywords = kwargs.get("keywords", [])
            
            if not keywords:
                return {"error": "Au moins un mot-clé doit être fourni"}
            
            if not isinstance(keywords, list):
                return {"error": "Le paramètre 'keywords' doit être une liste"}
            
            # Validation du nombre de mots-clés
            if len(keywords) > 50:
                return {"error": "Maximum 50 mots-clés par requête"}
            
            # Nettoyage des mots-clés
            clean_keywords = [kw.strip() for kw in keywords if kw.strip()]
            if not clean_keywords:
                return {"error": "Aucun mot-clé valide fourni"}
            
            logger.info(f"🔄 Demande de rafraîchissement pour {len(clean_keywords)} mots-clés")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async(
                "keywords/scrap",
                {"keywords": clean_keywords}
            )
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse de la réponse
            return self._analyze_scrap_response(response, clean_keywords)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la demande de rafraîchissement: {str(e)}")
            return {"error": f"Erreur lors de la demande de rafraîchissement: {str(e)}"}
    
    def _analyze_scrap_response(self, response: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
        """Analyse et synthèse de la réponse de rafraîchissement"""
        try:
            # Vérification du statut de la réponse
            status_code = response.get("status_code", response.get("response_code", 200))
            
            # Status 201 indique que la requête a été acceptée et sera traitée
            if status_code == 201:
                success_status = "accepted"
                message = "Demande de rafraîchissement acceptée et en cours de traitement"
            elif status_code == 200:
                success_status = "processed"
                message = "Demande de rafraîchissement traitée avec succès"
            else:
                success_status = "unknown"
                message = f"Statut de réponse inattendu: {status_code}"
            
            # Calcul des crédits consommés
            credits_used = len(keywords)
            
            # Informations sur les mots-clés traités
            keyword_info = []
            for keyword in keywords:
                keyword_info.append({
                    "keyword": keyword,
                    "status": "queued" if status_code == 201 else "processed",
                    "credits_used": 1
                })
            
            # Estimation du temps de traitement
            estimated_time = self._estimate_processing_time(len(keywords))
            
            result = {
                "summary": f"{message} pour {len(keywords)} mots-clés",
                "status": success_status,
                "request_details": {
                    "keywords_count": len(keywords),
                    "credits_consumed": credits_used,
                    "estimated_processing_time": estimated_time
                },
                "keywords": keyword_info,
                "recommendations": self._generate_scrap_recommendations(keywords, status_code),
                "response_metadata": {
                    "status_code": status_code,
                    "response_time": response.get("response_time", ""),
                    "timestamp": response.get("timestamp", "")
                }
            }
            
            # Ajout d'informations spécifiques selon le statut
            if status_code == 201:
                result["next_steps"] = [
                    "Les données seront rafraîchies dans les prochaines minutes",
                    "Vous pouvez vérifier l'état avec les outils d'analyse de mots-clés",
                    "Les nouveaux résultats seront disponibles après traitement"
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse de la réponse: {str(e)}")
            return {"error": f"Erreur lors de l'analyse de la réponse: {str(e)}"}
    
    def _estimate_processing_time(self, keyword_count: int) -> str:
        """Estime le temps de traitement basé sur le nombre de mots-clés"""
        if keyword_count <= 5:
            return "1-3 minutes"
        elif keyword_count <= 15:
            return "3-8 minutes"
        elif keyword_count <= 30:
            return "8-15 minutes"
        else:
            return "15-30 minutes"
    
    def _generate_scrap_recommendations(self, keywords: List[str], status_code: int) -> List[str]:
        """Génère des recommandations basées sur la demande de rafraîchissement"""
        recommendations = []
        
        if status_code == 201:
            recommendations.append("✅ Demande acceptée - Les données seront mises à jour prochainement")
            recommendations.append("⏱️ Attendez quelques minutes avant de consulter les nouvelles données")
            
            if len(keywords) > 20:
                recommendations.append("📊 Traitement en lot important - Surveillez vos crédits de rafraîchissement")
            
            recommendations.append("🔍 Utilisez les outils d'analyse après traitement pour voir les nouvelles données")
            
        elif status_code == 200:
            recommendations.append("✅ Traitement terminé - Les nouvelles données sont disponibles")
            recommendations.append("📈 Consultez maintenant les métriques mises à jour")
            
        else:
            recommendations.append("⚠️ Statut inattendu - Vérifiez votre solde de crédits")
            recommendations.append("🔄 Réessayez si nécessaire")
        
        # Recommandations générales
        if len(keywords) < 5:
            recommendations.append("💡 Conseil: Groupez vos demandes pour optimiser l'usage des crédits")
        
        return recommendations if recommendations else ["📊 Demande de rafraîchissement envoyée"]
