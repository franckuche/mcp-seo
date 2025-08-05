"""
MCP Tool pour l'endpoint Haloscan page/bestKeywords
Permet d'obtenir les meilleurs mots-clés pour une page spécifique avec leurs métriques SEO
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("page_best_keywords_tool")

class PageBestKeywordsTool(BaseMCPTool):
    """Outil MCP pour obtenir les meilleurs mots-clés d'une page via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "pagebestkeywords"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour les meilleurs mots-clés d'une page"""
        return {
            "type": "function",
            "function": {
                "name": "page_best_keywords",
                "description": "Get the best performing keywords for a specific page/URL with detailed SEO metrics including positions, traffic, volume, and competition data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The specific page URL to analyze (e.g., 'https://example.com/page' or 'example.com/page')"
                        },
                        "lineCount": {
                            "type": "integer",
                            "description": "Maximum number of keywords to return",
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
                            "enum": ["default", "volume", "traffic", "position", "keyword", "cpc", "competition", "kgr", "allintitle", "last_scrap", "word_count", "result_count"],
                            "description": "Field used for sorting results. Default sorts by descending traffic and then ascending position",
                            "default": "default"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Whether the results are sorted in ascending or descending order",
                            "default": "desc"
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
                        "traffic_min": {
                            "type": "integer",
                            "description": "Minimum traffic filter",
                            "minimum": 0
                        },
                        "traffic_max": {
                            "type": "integer",
                            "description": "Maximum traffic filter",
                            "minimum": 0
                        },
                        "position_min": {
                            "type": "integer",
                            "description": "Minimum position filter (1 = best)",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "position_max": {
                            "type": "integer",
                            "description": "Maximum position filter (100 = worst)",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "cpc_min": {
                            "type": "number",
                            "description": "Minimum cost per click filter",
                            "minimum": 0
                        },
                        "cpc_max": {
                            "type": "number",
                            "description": "Maximum cost per click filter",
                            "minimum": 0
                        },
                        "competition_min": {
                            "type": "number",
                            "description": "Minimum competition level (0-1)",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "competition_max": {
                            "type": "number",
                            "description": "Maximum competition level (0-1)",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "kgr_min": {
                            "type": "number",
                            "description": "Minimum Keyword Golden Ratio",
                            "minimum": 0
                        },
                        "kgr_max": {
                            "type": "number",
                            "description": "Maximum Keyword Golden Ratio",
                            "minimum": 0
                        },
                        "word_count_min": {
                            "type": "integer",
                            "description": "Minimum word count in keyword",
                            "minimum": 1
                        },
                        "word_count_max": {
                            "type": "integer",
                            "description": "Maximum word count in keyword",
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
                    "required": ["input"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse des meilleurs mots-clés d'une page"""
        try:
            # Validation des paramètres requis
            input_url = kwargs.get("input", "").strip()
            
            if not input_url:
                return {"error": "Le paramètre 'input' (URL de la page) est requis"}
            
            # Préparation des paramètres
            params = {
                "input": input_url,
                "lineCount": kwargs.get("lineCount", 20),
                "page": kwargs.get("page", 1),
                "order_by": kwargs.get("order_by", "default"),
                "order": kwargs.get("order", "desc")
            }
            
            # Ajout des filtres optionnels
            optional_filters = [
                "volume_min", "volume_max", "traffic_min", "traffic_max",
                "position_min", "position_max", "cpc_min", "cpc_max",
                "competition_min", "competition_max", "kgr_min", "kgr_max",
                "allintitle_min", "allintitle_max", "word_count_min", "word_count_max",
                "result_count_min", "result_count_max", "keyword_include", "keyword_exclude"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            logger.info(f"🔍 Analyse des meilleurs mots-clés pour la page: {input_url}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("page/bestKeywords", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_page_keywords_results(response, input_url)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des mots-clés de la page: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des mots-clés de la page: {str(e)}"}
    
    def _analyze_page_keywords_results(self, response: Dict[str, Any], input_url: str) -> Dict[str, Any]:
        """Analyse et synthèse des résultats des meilleurs mots-clés d'une page"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            filtered_count = response.get("filtered_result_count", 0)
            returned_count = response.get("returned_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucun mot-clé trouvé pour la page {input_url}",
                    "page_url": input_url,
                    "total_keywords": 0,
                    "keywords": []
                }
            
            # Analyse des métriques globales
            total_traffic = sum(result.get("traffic", 0) for result in results)
            total_volume = sum(result.get("volume", 0) for result in results)
            
            # Analyse des positions
            positions = [result.get("position", 100) for result in results if result.get("position")]
            top_3_count = sum(1 for pos in positions if pos <= 3)
            top_10_count = sum(1 for pos in positions if pos <= 10)
            top_50_count = sum(1 for pos in positions if pos <= 50)
            
            # Analyse des volumes et CPC
            volumes = [result.get("volume", 0) for result in results if result.get("volume", 0) > 0]
            cpcs = [result.get("cpc", 0) for result in results if result.get("cpc", 0) > 0]
            
            # Analyse des mots-clés individuels
            analyzed_keywords = []
            for result in results:
                keyword_analysis = {
                    "keyword": result.get("keyword", ""),
                    "position": result.get("position"),
                    "traffic": result.get("traffic", 0),
                    "volume": result.get("volume", 0),
                    "cpc": result.get("cpc", 0),
                    "competition": result.get("competition"),
                    "kgr": result.get("kgr"),
                    "allintitle": result.get("allintitle"),
                    "word_count": result.get("word_count", 0),
                    "result_count": result.get("result_count", 0),
                    "last_scrap": result.get("last_scrap", ""),
                    "performance_category": self._categorize_keyword_performance(result),
                    "opportunity_score": self._calculate_opportunity_score(result)
                }
                analyzed_keywords.append(keyword_analysis)
            
            # Identification des mots-clés par catégorie
            top_performers = [kw for kw in analyzed_keywords if kw["performance_category"] == "top_performer"]
            opportunities = [kw for kw in analyzed_keywords if kw["performance_category"] == "opportunity"]
            long_tail = [kw for kw in analyzed_keywords if kw["word_count"] >= 4]
            
            # Statistiques globales
            stats = {
                "total_keywords_found": total_count,
                "keywords_analyzed": returned_count,
                "total_traffic": total_traffic,
                "total_volume": total_volume,
                "position_distribution": {
                    "top_3": top_3_count,
                    "top_10": top_10_count,
                    "top_50": top_50_count,
                    "beyond_50": returned_count - top_50_count
                },
                "averages": {
                    "position": sum(positions) / len(positions) if positions else 0,
                    "traffic": total_traffic // returned_count if returned_count > 0 else 0,
                    "volume": sum(volumes) // len(volumes) if volumes else 0,
                    "cpc": sum(cpcs) / len(cpcs) if cpcs else 0
                },
                "categories": {
                    "top_performers": len(top_performers),
                    "opportunities": len(opportunities),
                    "long_tail": len(long_tail)
                }
            }
            
            return {
                "summary": f"Analyse de {returned_count} mots-clés pour la page {input_url}",
                "page_url": input_url,
                "statistics": stats,
                "top_performers": top_performers[:10],  # Top 10 performers
                "opportunities": opportunities[:10],    # Top 10 opportunities
                "long_tail_keywords": long_tail[:10],   # Top 10 long tail
                "all_keywords": analyzed_keywords,
                "recommendations": self._generate_page_keywords_recommendations(analyzed_keywords, stats),
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
    
    def _categorize_keyword_performance(self, result: Dict[str, Any]) -> str:
        """Catégorise la performance d'un mot-clé"""
        position = result.get("position", 100)
        traffic = result.get("traffic", 0)
        volume = result.get("volume", 0)
        
        # Top performer: position <= 10 et trafic > 0
        if position <= 10 and traffic > 0:
            return "top_performer"
        
        # Opportunité: position 11-50 avec bon volume
        if 11 <= position <= 50 and volume > 100:
            return "opportunity"
        
        # Long tail: position correcte mais faible volume
        if position <= 20 and volume < 100:
            return "long_tail"
        
        # Needs work: position > 50
        if position > 50:
            return "needs_work"
        
        return "average"
    
    def _calculate_opportunity_score(self, result: Dict[str, Any]) -> float:
        """Calcule un score d'opportunité pour un mot-clé"""
        position = result.get("position", 100)
        volume = result.get("volume", 0)
        competition = result.get("competition", 1)
        cpc = result.get("cpc", 0)
        
        # Score basé sur: volume élevé, faible compétition, position améliorable
        volume_score = min(volume / 1000, 10)  # Max 10 points
        competition_score = (1 - competition) * 5 if competition else 0  # Max 5 points
        position_score = max(0, (100 - position) / 10)  # Max 10 points
        cpc_score = min(cpc, 5)  # Max 5 points
        
        total_score = volume_score + competition_score + position_score + cpc_score
        return round(total_score, 2)
    
    def _generate_page_keywords_recommendations(self, keywords: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des mots-clés de la page"""
        recommendations = []
        
        if not keywords:
            return ["Aucun mot-clé trouvé pour cette page"]
        
        # Analyse des positions
        avg_position = stats.get("averages", {}).get("position", 0)
        top_10_count = stats.get("position_distribution", {}).get("top_10", 0)
        
        if avg_position < 15:
            recommendations.append("🏆 Excellente position moyenne, optimisez pour le top 3")
        elif avg_position > 30:
            recommendations.append("📈 Position moyenne élevée, renforcez l'optimisation SEO")
        
        if top_10_count > len(keywords) * 0.3:
            recommendations.append("🎯 Bon nombre de mots-clés en top 10, maintenez vos efforts")
        elif top_10_count < len(keywords) * 0.1:
            recommendations.append("🔧 Peu de mots-clés en top 10, travaillez l'autorité de la page")
        
        # Analyse du trafic
        total_traffic = stats.get("total_traffic", 0)
        if total_traffic > 1000:
            recommendations.append("🚀 Excellent trafic généré, cette page est performante")
        elif total_traffic < 100:
            recommendations.append("📊 Trafic faible, optimisez les mots-clés à fort potentiel")
        
        # Analyse des opportunités
        opportunities = stats.get("categories", {}).get("opportunities", 0)
        if opportunities > 5:
            recommendations.append(f"💡 {opportunities} opportunités d'amélioration identifiées")
        
        # Analyse de la longue traîne
        long_tail = stats.get("categories", {}).get("long_tail", 0)
        if long_tail > len(keywords) * 0.3:
            recommendations.append("🎪 Bon potentiel longue traîne, enrichissez le contenu")
        
        # Recommandations sur le CPC
        avg_cpc = stats.get("averages", {}).get("cpc", 0)
        if avg_cpc > 2:
            recommendations.append("💰 Mots-clés à fort CPC, potentiel commercial élevé")
        
        # Recommandation sur les mots-clés les plus prometteurs
        if keywords:
            best_opportunity = max(keywords, key=lambda x: x["opportunity_score"])
            if best_opportunity["opportunity_score"] > 15:
                recommendations.append(f"🌟 Mot-clé prioritaire: '{best_opportunity['keyword']}' (score: {best_opportunity['opportunity_score']})")
        
        return recommendations if recommendations else ["📊 Analyse des mots-clés terminée, consultez les données détaillées"]
