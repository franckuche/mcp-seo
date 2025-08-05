"""
MCP Tool pour l'endpoint Haloscan domains/topPages
Permet d'obtenir les pages les plus performantes d'un domaine avec leurs métriques SEO
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_top_pages_tool")

class DomainsTopPagesTool(BaseMCPTool):
    """Outil MCP pour obtenir les pages les plus performantes d'un domaine via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainstoppages"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'analyse des pages les plus performantes"""
        return {
            "type": "function",
            "function": {
                "name": "domains_top_pages",
                "description": "Get the top performing pages of a domain with their SEO metrics including traffic, keywords, and ranking positions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The domain or URL to analyze (e.g., 'example.com' or 'https://example.com')"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["auto", "root", "domain", "url"],
                            "description": "Whether to look for a domain or a full URL. Leave empty for auto detection",
                            "default": "auto"
                        },
                        "lineCount": {
                            "type": "integer",
                            "description": "Maximum number of pages to return",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number for pagination",
                            "default": 1,
                            "minimum": 1
                        },
                        "order_by": {
                            "type": "string",
                            "enum": ["default", "domain", "url", "first_time_seen", "last_time_seen", "known_versions", "total_traffic", "unique_keywords", "total_top_100", "total_top_50", "total_top_10", "total_top_3"],
                            "description": "Field used for sorting results. Default sorts by descending traffic and then ascending position",
                            "default": "default"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Whether the results are sorted in ascending or descending order",
                            "default": "desc"
                        },
                        "total_traffic_min": {
                            "type": "integer",
                            "description": "Minimum total traffic filter",
                            "minimum": 0
                        },
                        "total_traffic_max": {
                            "type": "integer",
                            "description": "Maximum total traffic filter",
                            "minimum": 0
                        },
                        "unique_keywords_min": {
                            "type": "integer",
                            "description": "Minimum unique keywords filter",
                            "minimum": 0
                        },
                        "unique_keywords_max": {
                            "type": "integer",
                            "description": "Maximum unique keywords filter",
                            "minimum": 0
                        }
                    },
                    "required": ["input"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse des pages les plus performantes d'un domaine"""
        try:
            # Validation des paramètres
            input_domain = kwargs.get("input", "").strip()
            if not input_domain:
                return {"error": "Le paramètre 'input' (domaine) est requis"}
            
            # Préparation des paramètres
            params = {
                "input": input_domain,
                "mode": kwargs.get("mode", "auto"),
                "lineCount": kwargs.get("lineCount", 20),
                "page": kwargs.get("page", 1),
                "order_by": kwargs.get("order_by", "default"),
                "order": kwargs.get("order", "desc")
            }
            
            # Ajout des filtres optionnels
            optional_filters = [
                "total_traffic_min", "total_traffic_max",
                "unique_keywords_min", "unique_keywords_max",
                "total_top_3_min", "total_top_3_max",
                "total_top_10_min", "total_top_10_max",
                "total_top_50_min", "total_top_50_max",
                "total_top_100_min", "total_top_100_max",
                "known_versions_min", "known_versions_max"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            logger.info(f"🔍 Analyse des pages top pour {input_domain} (mode: {params['mode']}, limite: {params['lineCount']})")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/topPages", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_top_pages_results(response, input_domain)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des pages top: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des pages top: {str(e)}"}
    
    def _analyze_top_pages_results(self, response: Dict[str, Any], input_domain: str) -> Dict[str, Any]:
        """Analyse et synthèse des résultats des pages les plus performantes"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            filtered_count = response.get("filtered_result_count", 0)
            returned_count = response.get("returned_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucune page trouvée pour {input_domain}",
                    "domain": input_domain,
                    "total_pages": 0,
                    "pages": []
                }
            
            # Analyse des métriques globales
            total_traffic = sum(page.get("total_traffic", 0) for page in results)
            total_keywords = sum(page.get("unique_keywords", 0) for page in results)
            total_top_3 = sum(page.get("total_top_3", 0) for page in results)
            total_top_10 = sum(page.get("total_top_10", 0) for page in results)
            
            # Analyse des pages individuelles
            analyzed_pages = []
            for page in results:
                page_analysis = {
                    "url": page.get("url", ""),
                    "traffic": page.get("total_traffic", 0),
                    "traffic_value": page.get("total_traffic_value", 0),
                    "keywords": page.get("unique_keywords", 0),
                    "top_keywords": page.get("top_keywords", ""),
                    "positions": {
                        "top_3": page.get("total_top_3", 0),
                        "top_10": page.get("total_top_10", 0),
                        "top_50": page.get("total_top_50", 0),
                        "top_100": page.get("total_top_100", 0)
                    },
                    "first_seen": page.get("first_time_seen", ""),
                    "last_seen": page.get("last_time_seen", ""),
                    "versions": page.get("known_versions", 0),
                    "performance_score": self._calculate_page_performance_score(page)
                }
                analyzed_pages.append(page_analysis)
            
            # Identification des pages les plus performantes
            top_performers = sorted(analyzed_pages, key=lambda x: x["performance_score"], reverse=True)[:5]
            
            # Statistiques globales
            stats = {
                "total_pages_found": total_count,
                "pages_analyzed": returned_count,
                "total_traffic": total_traffic,
                "total_keywords": total_keywords,
                "total_top_positions": {
                    "top_3": total_top_3,
                    "top_10": total_top_10
                },
                "average_traffic_per_page": total_traffic // returned_count if returned_count > 0 else 0,
                "average_keywords_per_page": total_keywords // returned_count if returned_count > 0 else 0
            }
            
            return {
                "summary": f"Analyse de {returned_count} pages top pour {input_domain}",
                "domain": input_domain,
                "statistics": stats,
                "top_performers": top_performers,
                "all_pages": analyzed_pages,
                "recommendations": self._generate_top_pages_recommendations(analyzed_pages, stats),
                "response_metadata": {
                    "response_time": response.get("response_time", ""),
                    "total_results": total_count,
                    "filtered_results": filtered_count,
                    "remaining_results": response.get("remaining_result_count", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des résultats: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des résultats: {str(e)}"}
    
    def _calculate_page_performance_score(self, page: Dict[str, Any]) -> float:
        """Calcule un score de performance pour une page basé sur ses métriques"""
        traffic = page.get("total_traffic", 0)
        keywords = page.get("unique_keywords", 0)
        top_3 = page.get("total_top_3", 0)
        top_10 = page.get("total_top_10", 0)
        
        # Score pondéré : trafic (40%), top 3 positions (30%), top 10 positions (20%), nombre de mots-clés (10%)
        score = (traffic * 0.4) + (top_3 * 100 * 0.3) + (top_10 * 50 * 0.2) + (keywords * 0.1)
        return round(score, 2)
    
    def _generate_top_pages_recommendations(self, pages: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des pages top"""
        recommendations = []
        
        if not pages:
            return ["Aucune page trouvée pour ce domaine"]
        
        # Analyse du trafic
        avg_traffic = stats.get("average_traffic_per_page", 0)
        if avg_traffic > 1000:
            recommendations.append("🎯 Excellent trafic moyen par page, votre contenu performe bien")
        elif avg_traffic < 100:
            recommendations.append("⚠️ Trafic faible par page, optimisez le SEO de vos contenus principaux")
        
        # Analyse des positions
        total_top_3 = stats.get("total_top_positions", {}).get("top_3", 0)
        total_top_10 = stats.get("total_top_positions", {}).get("top_10", 0)
        
        if total_top_3 > 50:
            recommendations.append("🏆 Nombreuses positions en top 3, excellente autorité SEO")
        elif total_top_10 > 100:
            recommendations.append("📈 Bonnes positions en top 10, potentiel d'amélioration vers le top 3")
        else:
            recommendations.append("🔧 Peu de positions dans le top 10, travaillez l'optimisation on-page")
        
        # Analyse des mots-clés
        avg_keywords = stats.get("average_keywords_per_page", 0)
        if avg_keywords > 100:
            recommendations.append("🎪 Pages riches en mots-clés, bon potentiel de longue traîne")
        elif avg_keywords < 20:
            recommendations.append("📝 Peu de mots-clés par page, enrichissez votre contenu")
        
        # Recommandations spécifiques aux top performers
        top_page = max(pages, key=lambda x: x["traffic"]) if pages else None
        if top_page and top_page["traffic"] > 0:
            recommendations.append(f"🌟 Page star: {top_page['url'][:50]}... avec {top_page['traffic']} de trafic")
        
        return recommendations if recommendations else ["📊 Analyse terminée, consultez les données détaillées"]
