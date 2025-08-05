"""
MCP Tool pour l'endpoint Haloscan keywords/bulk
Permet d'analyser plusieurs mots-clés en une seule requête pour optimiser les performances
"""

from typing import Dict, Any, List
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("keywords_bulk_tool")

class KeywordsBulkTool(BaseMCPTool):
    """Outil MCP pour l'analyse en masse de mots-clés via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "keywordsbulk"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'analyse en masse de mots-clés"""
        return {
            "type": "function",
            "function": {
                "name": "keywords_bulk",
                "description": "Analyze multiple keywords in bulk to get comprehensive data for all keywords in a single request. Optimized for performance when analyzing many keywords at once.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of keywords to analyze in bulk (maximum 100 keywords per request)",
                            "minItems": 1,
                            "maxItems": 100
                        },
                        "country": {
                            "type": "string",
                            "description": "Country code for localized results (e.g., 'FR', 'US', 'GB')",
                            "default": "FR"
                        },
                        "language": {
                            "type": "string", 
                            "description": "Language code for results (e.g., 'fr', 'en', 'es')",
                            "default": "fr"
                        }
                    },
                    "required": ["keywords"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse en masse de mots-clés"""
        try:
            # Validation des paramètres
            keywords = kwargs.get("keywords", [])
            country = kwargs.get("country", "FR")
            language = kwargs.get("language", "fr")
            
            if not keywords:
                return {"error": "Au moins un mot-clé doit être fourni"}
            
            if len(keywords) > 100:
                return {"error": "Maximum 100 mots-clés par requête"}
            
            logger.info(f"🔍 Analyse en masse de {len(keywords)} mots-clés (pays: {country}, langue: {language})")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async(
                "keywords/bulk",
                {
                    "keywords": keywords,
                    "country": country,
                    "language": language
                }
            )
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_bulk_results(response, keywords)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse en masse: {str(e)}")
            return {"error": f"Erreur lors de l'analyse en masse: {str(e)}"}
    
    def _analyze_bulk_results(self, response: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
        """Analyse et synthèse des résultats d'analyse en masse"""
        try:
            results = response.get("data", {})
            
            # Statistiques globales
            total_keywords = len(keywords)
            processed_keywords = len([k for k in keywords if k in results])
            
            # Analyse des volumes de recherche
            volumes = []
            difficulties = []
            trends = []
            
            keyword_data = {}
            
            for keyword in keywords:
                if keyword in results:
                    data = results[keyword]
                    keyword_data[keyword] = {
                        "volume": data.get("volume", 0),
                        "difficulty": data.get("difficulty", 0),
                        "cpc": data.get("cpc", 0),
                        "trend": data.get("trend", "stable"),
                        "competition": data.get("competition", "unknown")
                    }
                    
                    if data.get("volume"):
                        volumes.append(data["volume"])
                    if data.get("difficulty"):
                        difficulties.append(data["difficulty"])
                    if data.get("trend"):
                        trends.append(data["trend"])
                else:
                    keyword_data[keyword] = {"error": "Données non disponibles"}
            
            # Calcul des statistiques
            stats = {
                "total_keywords": total_keywords,
                "processed_keywords": processed_keywords,
                "success_rate": f"{(processed_keywords/total_keywords)*100:.1f}%" if total_keywords > 0 else "0%"
            }
            
            if volumes:
                stats["volume_stats"] = {
                    "average": sum(volumes) // len(volumes),
                    "max": max(volumes),
                    "min": min(volumes),
                    "total": sum(volumes)
                }
            
            if difficulties:
                stats["difficulty_stats"] = {
                    "average": sum(difficulties) / len(difficulties),
                    "max": max(difficulties),
                    "min": min(difficulties)
                }
            
            # Analyse des tendances
            if trends:
                trend_analysis = {}
                for trend in set(trends):
                    trend_analysis[trend] = trends.count(trend)
                stats["trend_distribution"] = trend_analysis
            
            return {
                "summary": f"Analyse en masse réussie pour {processed_keywords}/{total_keywords} mots-clés",
                "statistics": stats,
                "keyword_data": keyword_data,
                "recommendations": self._generate_bulk_recommendations(keyword_data, stats)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des résultats: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des résultats: {str(e)}"}
    
    def _generate_bulk_recommendations(self, keyword_data: Dict[str, Any], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse en masse"""
        recommendations = []
        
        # Recommandations basées sur le volume
        if "volume_stats" in stats:
            volume_stats = stats["volume_stats"]
            if volume_stats["average"] > 10000:
                recommendations.append("🎯 Excellent potentiel de trafic avec un volume moyen élevé")
            elif volume_stats["average"] < 1000:
                recommendations.append("⚠️ Volume de recherche faible, considérez des mots-clés plus populaires")
        
        # Recommandations basées sur la difficulté
        if "difficulty_stats" in stats:
            difficulty_stats = stats["difficulty_stats"]
            if difficulty_stats["average"] > 70:
                recommendations.append("🔥 Mots-clés très compétitifs, stratégie long terme nécessaire")
            elif difficulty_stats["average"] < 30:
                recommendations.append("✅ Opportunités avec faible concurrence détectées")
        
        # Recommandations basées sur les tendances
        if "trend_distribution" in stats:
            trends = stats["trend_distribution"]
            if trends.get("rising", 0) > trends.get("falling", 0):
                recommendations.append("📈 Tendances positives dominantes, bon timing pour le SEO")
            elif trends.get("falling", 0) > trends.get("rising", 0):
                recommendations.append("📉 Attention aux tendances déclinantes, diversifiez votre stratégie")
        
        # Recommandation sur le taux de succès
        success_rate = float(stats["success_rate"].replace("%", ""))
        if success_rate < 80:
            recommendations.append("⚠️ Certains mots-clés n'ont pas de données, vérifiez leur orthographe")
        
        return recommendations if recommendations else ["📊 Analyse terminée, consultez les données détaillées"]
