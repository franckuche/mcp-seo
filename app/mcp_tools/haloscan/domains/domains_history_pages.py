"""
MCP Tool pour l'endpoint Haloscan domains/pagesHistory
Permet d'obtenir l'historique des pages d'un domaine avec leurs performances SEO sur une période donnée
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_history_pages_tool")

class DomainsHistoryPagesTool(BaseMCPTool):
    """Outil MCP pour obtenir l'historique des pages d'un domaine via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainshistorypages"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'historique des pages d'un domaine"""
        return {
            "type": "function",
            "function": {
                "name": "domains_history_pages",
                "description": "Get historical performance data for pages of a domain over a specific time period. Shows how individual pages performed with traffic, keywords, and ranking metrics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The domain or URL to analyze (e.g., 'example.com' or 'https://example.com')"
                        },
                        "date_from": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format (e.g., '2023-01-01')"
                        },
                        "date_to": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format (e.g., '2023-12-31')"
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
                        },
                        "total_top_3_min": {
                            "type": "integer",
                            "description": "Minimum top 3 positions filter",
                            "minimum": 0
                        },
                        "total_top_10_min": {
                            "type": "integer",
                            "description": "Minimum top 10 positions filter",
                            "minimum": 0
                        }
                    },
                    "required": ["input", "date_from", "date_to"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse de l'historique des pages d'un domaine"""
        try:
            # Validation des paramètres requis
            input_domain = kwargs.get("input", "").strip()
            date_from = kwargs.get("date_from", "").strip()
            date_to = kwargs.get("date_to", "").strip()
            
            if not input_domain:
                return {"error": "Le paramètre 'input' (domaine) est requis"}
            if not date_from:
                return {"error": "Le paramètre 'date_from' est requis (format YYYY-MM-DD)"}
            if not date_to:
                return {"error": "Le paramètre 'date_to' est requis (format YYYY-MM-DD)"}
            
            # Préparation des paramètres
            params = {
                "input": input_domain,
                "date_from": date_from,
                "date_to": date_to,
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
            
            logger.info(f"🔍 Analyse historique des pages pour {input_domain} ({date_from} à {date_to})")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/pagesHistory", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_history_pages_results(response, input_domain, date_from, date_to)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse historique des pages: {str(e)}")
            return {"error": f"Erreur lors de l'analyse historique des pages: {str(e)}"}
    
    def _analyze_history_pages_results(self, response: Dict[str, Any], input_domain: str, date_from: str, date_to: str) -> Dict[str, Any]:
        """Analyse et synthèse des résultats de l'historique des pages"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            filtered_count = response.get("filtered_result_count", 0)
            returned_count = response.get("returned_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucune page historique trouvée pour {input_domain} entre {date_from} et {date_to}",
                    "domain": input_domain,
                    "period": {"from": date_from, "to": date_to},
                    "total_pages": 0,
                    "pages": []
                }
            
            # Analyse des métriques globales
            total_traffic = sum(page.get("total_traffic", 0) for page in results)
            total_keywords = sum(page.get("unique_keywords", 0) for page in results)
            total_active_keywords = sum(page.get("active_keywords", 0) for page in results)
            total_lost_keywords = sum(page.get("lost_keywords", 0) for page in results)
            
            # Analyse des positions top
            total_top_3 = sum(page.get("total_top_3", 0) for page in results)
            total_top_10 = sum(page.get("total_top_10", 0) for page in results)
            total_top_50 = sum(page.get("total_top_50", 0) for page in results)
            
            # Analyse des pages individuelles
            analyzed_pages = []
            for page in results:
                page_analysis = {
                    "url": page.get("url", ""),
                    "domain": page.get("domain", ""),
                    "traffic": page.get("total_traffic", 0),
                    "keywords": {
                        "unique": page.get("unique_keywords", 0),
                        "active": page.get("active_keywords", 0),
                        "lost": page.get("lost_keywords", 0)
                    },
                    "positions": {
                        "top_3": page.get("total_top_3", 0),
                        "top_10": page.get("total_top_10", 0),
                        "top_50": page.get("total_top_50", 0),
                        "top_100": page.get("total_top_100", 0)
                    },
                    "timeline": {
                        "first_seen": page.get("first_time_seen", ""),
                        "last_seen": page.get("last_time_seen", ""),
                        "versions": page.get("known_versions", 0)
                    },
                    "performance_score": self._calculate_page_performance_score(page),
                    "keyword_retention_rate": self._calculate_keyword_retention_rate(page)
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
                "keyword_health": {
                    "active_keywords": total_active_keywords,
                    "lost_keywords": total_lost_keywords,
                    "retention_rate": f"{(total_active_keywords/(total_active_keywords + total_lost_keywords))*100:.1f}%" if (total_active_keywords + total_lost_keywords) > 0 else "0%"
                },
                "position_distribution": {
                    "top_3": total_top_3,
                    "top_10": total_top_10,
                    "top_50": total_top_50
                },
                "averages": {
                    "traffic_per_page": total_traffic // returned_count if returned_count > 0 else 0,
                    "keywords_per_page": total_keywords // returned_count if returned_count > 0 else 0,
                    "top_10_per_page": total_top_10 // returned_count if returned_count > 0 else 0
                }
            }
            
            return {
                "summary": f"Analyse historique de {returned_count} pages pour {input_domain}",
                "domain": input_domain,
                "period": {"from": date_from, "to": date_to},
                "statistics": stats,
                "top_performers": top_performers,
                "all_pages": analyzed_pages,
                "recommendations": self._generate_history_pages_recommendations(analyzed_pages, stats),
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
        """Calcule un score de performance pour une page basé sur ses métriques historiques"""
        traffic = page.get("total_traffic", 0)
        active_keywords = page.get("active_keywords", 0)
        top_3 = page.get("total_top_3", 0)
        top_10 = page.get("total_top_10", 0)
        
        # Score pondéré : trafic (40%), mots-clés actifs (20%), top 3 (25%), top 10 (15%)
        score = (traffic * 0.4) + (active_keywords * 5 * 0.2) + (top_3 * 100 * 0.25) + (top_10 * 50 * 0.15)
        return round(score, 2)
    
    def _calculate_keyword_retention_rate(self, page: Dict[str, Any]) -> str:
        """Calcule le taux de rétention des mots-clés pour une page"""
        active = page.get("active_keywords", 0)
        lost = page.get("lost_keywords", 0)
        total = active + lost
        
        if total == 0:
            return "0%"
        
        retention_rate = (active / total) * 100
        return f"{retention_rate:.1f}%"
    
    def _generate_history_pages_recommendations(self, pages: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse historique des pages"""
        recommendations = []
        
        if not pages:
            return ["Aucune page historique trouvée pour cette période"]
        
        # Analyse du taux de rétention global
        retention_rate = stats.get("keyword_health", {}).get("retention_rate", "0%")
        retention_value = float(retention_rate.replace("%", ""))
        
        if retention_value > 80:
            recommendations.append("🎯 Excellent taux de rétention des mots-clés, vos pages sont stables")
        elif retention_value < 60:
            recommendations.append("⚠️ Taux de rétention faible, analysez les pages qui perdent des positions")
        
        # Analyse du trafic moyen
        avg_traffic = stats.get("averages", {}).get("traffic_per_page", 0)
        if avg_traffic > 1000:
            recommendations.append("🚀 Excellent trafic moyen par page, optimisez les top performers")
        elif avg_traffic < 100:
            recommendations.append("📈 Trafic faible par page, concentrez-vous sur l'optimisation SEO")
        
        # Analyse des positions top
        avg_top_10 = stats.get("averages", {}).get("top_10_per_page", 0)
        if avg_top_10 > 10:
            recommendations.append("🏆 Bonnes positions en top 10, travaillez vers le top 3")
        elif avg_top_10 < 3:
            recommendations.append("🔧 Peu de positions top 10, renforcez l'autorité de vos pages")
        
        # Analyse des pages performantes
        if pages:
            best_page = max(pages, key=lambda x: x["traffic"])
            if best_page["traffic"] > 0:
                recommendations.append(f"🌟 Page star: {best_page['url'][:50]}... avec {best_page['traffic']:.0f} de trafic")
        
        # Recommandations sur la diversité des mots-clés
        avg_keywords = stats.get("averages", {}).get("keywords_per_page", 0)
        if avg_keywords > 50:
            recommendations.append("🎪 Pages riches en mots-clés, bon potentiel de longue traîne")
        elif avg_keywords < 10:
            recommendations.append("📝 Peu de mots-clés par page, enrichissez votre contenu")
        
        return recommendations if recommendations else ["📊 Analyse historique des pages terminée"]
