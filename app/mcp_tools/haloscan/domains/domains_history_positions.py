"""
MCP Tool pour l'endpoint Haloscan domains/history
Permet d'obtenir l'historique des positions d'un domaine sur une période donnée
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_history_positions_tool")

class DomainsHistoryPositionsTool(BaseMCPTool):
    """Outil MCP pour obtenir l'historique des positions d'un domaine via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainshistorypositions"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'historique des positions d'un domaine"""
        return {
            "type": "function",
            "function": {
                "name": "domains_history_positions",
                "description": "Get historical keyword positions for a domain over a specific time period. Shows how keywords performed over time with detailed metrics.",
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
                            "description": "Maximum number of results to return",
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
                            "enum": ["default", "volume", "traffic", "position", "keyword", "url", "cpc", "competition", "kgr", "allintitle", "last_scrap", "word_count", "result_count"],
                            "description": "Field used for sorting results. Default sorts by descending traffic and then ascending position",
                            "default": "default"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Whether the results are sorted in ascending or descending order",
                            "default": "desc"
                        },
                        "still_there": {
                            "type": "boolean",
                            "description": "When TRUE, only keep positions that are still held. When FALSE, only keep positions that were lost. Leave empty if you don't want to filter."
                        },
                        "volume_min": {
                            "type": "integer",
                            "description": "Minimum search volume filter",
                            "minimum": 0
                        },
                        "volume_max": {
                            "type": "integer",
                            "description": "Maximum search volume filter",
                            "minimum": 0
                        },
                        "best_position_min": {
                            "type": "integer",
                            "description": "Minimum best position filter",
                            "minimum": 1
                        },
                        "best_position_max": {
                            "type": "integer",
                            "description": "Maximum best position filter",
                            "minimum": 1
                        },
                        "keyword_include": {
                            "type": "string",
                            "description": "Regular expression for keywords to be included"
                        },
                        "keyword_exclude": {
                            "type": "string",
                            "description": "Regular expression for keywords to be excluded"
                        }
                    },
                    "required": ["input", "date_from", "date_to"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse de l'historique des positions d'un domaine"""
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
                "still_there", "volume_min", "volume_max", "cpc_min", "cpc_max",
                "competition_min", "competition_max", "kgr_min", "kgr_max",
                "best_position_min", "best_position_max", "worst_position_min", "worst_position_max",
                "most_recent_position_min", "most_recent_position_max",
                "word_count_min", "word_count_max", "keyword_include", "keyword_exclude"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            logger.info(f"🔍 Analyse historique des positions pour {input_domain} ({date_from} à {date_to})")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/history", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_history_positions_results(response, input_domain, date_from, date_to)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse historique: {str(e)}")
            return {"error": f"Erreur lors de l'analyse historique: {str(e)}"}
    
    def _analyze_history_positions_results(self, response: Dict[str, Any], input_domain: str, date_from: str, date_to: str) -> Dict[str, Any]:
        """Analyse et synthèse des résultats de l'historique des positions"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            filtered_count = response.get("filtered_result_count", 0)
            returned_count = response.get("returned_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucune donnée historique trouvée pour {input_domain} entre {date_from} et {date_to}",
                    "domain": input_domain,
                    "period": {"from": date_from, "to": date_to},
                    "total_keywords": 0,
                    "keywords": []
                }
            
            # Analyse des métriques globales
            total_traffic = sum(result.get("most_recent_traffic", 0) for result in results)
            active_keywords = sum(1 for result in results if result.get("still_there", False))
            lost_keywords = returned_count - active_keywords
            
            # Analyse des positions
            best_positions = [result.get("best_position", 100) for result in results if result.get("best_position")]
            worst_positions = [result.get("worst_position", 1) for result in results if result.get("worst_position")]
            current_positions = [result.get("most_recent_position", 100) for result in results if result.get("most_recent_position")]
            
            # Analyse des volumes
            volumes = [result.get("volume", 0) for result in results if result.get("volume", 0) > 0]
            
            # Analyse des mots-clés individuels
            analyzed_keywords = []
            for result in results:
                keyword_analysis = {
                    "keyword": result.get("keyword", ""),
                    "url": result.get("url", ""),
                    "current_position": result.get("most_recent_position"),
                    "best_position": result.get("best_position"),
                    "worst_position": result.get("worst_position"),
                    "current_traffic": result.get("most_recent_traffic", 0),
                    "volume": result.get("volume", 0),
                    "cpc": result.get("cpc", 0),
                    "competition": result.get("competition"),
                    "still_ranking": result.get("still_there", False),
                    "first_seen": result.get("first_time_seen", ""),
                    "last_seen": result.get("last_time_seen", ""),
                    "times_seen": result.get("times_seen", 0),
                    "performance_trend": self._calculate_performance_trend(result)
                }
                analyzed_keywords.append(keyword_analysis)
            
            # Statistiques globales
            stats = {
                "total_keywords_found": total_count,
                "keywords_analyzed": returned_count,
                "active_keywords": active_keywords,
                "lost_keywords": lost_keywords,
                "retention_rate": f"{(active_keywords/returned_count)*100:.1f}%" if returned_count > 0 else "0%",
                "total_current_traffic": total_traffic,
                "average_traffic_per_keyword": total_traffic // returned_count if returned_count > 0 else 0
            }
            
            if best_positions:
                stats["position_stats"] = {
                    "best_position_achieved": min(best_positions),
                    "average_best_position": sum(best_positions) / len(best_positions),
                    "average_current_position": sum(current_positions) / len(current_positions) if current_positions else 0
                }
            
            if volumes:
                stats["volume_stats"] = {
                    "total_volume": sum(volumes),
                    "average_volume": sum(volumes) // len(volumes),
                    "max_volume": max(volumes)
                }
            
            return {
                "summary": f"Analyse historique de {returned_count} mots-clés pour {input_domain}",
                "domain": input_domain,
                "period": {"from": date_from, "to": date_to},
                "statistics": stats,
                "keywords": analyzed_keywords,
                "recommendations": self._generate_history_recommendations(analyzed_keywords, stats),
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
    
    def _calculate_performance_trend(self, result: Dict[str, Any]) -> str:
        """Calcule la tendance de performance d'un mot-clé"""
        best_pos = result.get("best_position")
        current_pos = result.get("most_recent_position")
        still_there = result.get("still_there", False)
        
        if not still_there:
            return "lost"
        
        if not best_pos or not current_pos:
            return "stable"
        
        if current_pos < best_pos:
            return "improving"
        elif current_pos > best_pos:
            return "declining"
        else:
            return "stable"
    
    def _generate_history_recommendations(self, keywords: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse historique"""
        recommendations = []
        
        if not keywords:
            return ["Aucune donnée historique disponible pour cette période"]
        
        # Analyse du taux de rétention
        retention_rate = float(stats.get("retention_rate", "0%").replace("%", ""))
        if retention_rate > 80:
            recommendations.append("🎯 Excellent taux de rétention des positions, votre SEO est stable")
        elif retention_rate < 50:
            recommendations.append("⚠️ Taux de rétention faible, analysez les causes de perte de positions")
        
        # Analyse des tendances
        improving_count = sum(1 for kw in keywords if kw["performance_trend"] == "improving")
        declining_count = sum(1 for kw in keywords if kw["performance_trend"] == "declining")
        
        if improving_count > declining_count:
            recommendations.append("📈 Plus de mots-clés en progression qu'en déclin, tendance positive")
        elif declining_count > improving_count:
            recommendations.append("📉 Attention: plus de mots-clés en déclin, révision SEO nécessaire")
        
        # Analyse du trafic
        avg_traffic = stats.get("average_traffic_per_keyword", 0)
        if avg_traffic > 100:
            recommendations.append("🚀 Bon trafic moyen par mot-clé, optimisez les top performers")
        elif avg_traffic < 10:
            recommendations.append("🔧 Trafic faible, concentrez-vous sur les mots-clés à fort volume")
        
        # Recommandations sur les positions
        if "position_stats" in stats:
            avg_current = stats["position_stats"].get("average_current_position", 0)
            if avg_current > 20:
                recommendations.append("📊 Positions moyennes élevées, travaillez l'optimisation on-page")
            elif avg_current < 10:
                recommendations.append("🏆 Bonnes positions moyennes, maintenez vos efforts SEO")
        
        return recommendations if recommendations else ["📊 Analyse historique terminée, consultez les données détaillées"]
