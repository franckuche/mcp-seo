"""
MCP Tool pour l'endpoint Haloscan domains/keywords
Permet d'analyser les positions d'un domaine sur des mots-clés spécifiques
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_keywords_tool")

class DomainsKeywordsTool(BaseMCPTool):
    """Outil MCP pour analyser les positions d'un domaine sur des mots-clés spécifiques via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainskeywords"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'analyse des mots-clés d'un domaine"""
        return {
            "type": "function",
            "function": {
                "name": "domains_keywords",
                "description": "Analyze how a domain performs on specific keywords with detailed position, traffic, and SEO metrics for each keyword.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The domain or URL to analyze (e.g., 'example.com' or 'https://example.com')"
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of keywords to analyze (e.g., ['keyword 1', 'keyword 2'])",
                            "minItems": 1
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
                            "enum": ["default", "keyword", "volume", "cpc", "competition", "kgr", "allintitle"],
                            "description": "Field used for sorting results",
                            "default": "default"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Whether the results are sorted in ascending or descending order",
                            "default": "asc"
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
                        "kvi_min": {
                            "type": "number",
                            "description": "Minimum Keyword Value Index",
                            "minimum": 0
                        },
                        "kvi_max": {
                            "type": "number",
                            "description": "Maximum Keyword Value Index",
                            "minimum": 0
                        },
                        "allintitle_min": {
                            "type": "integer",
                            "description": "Minimum allintitle count",
                            "minimum": 0
                        },
                        "allintitle_max": {
                            "type": "integer",
                            "description": "Maximum allintitle count",
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
                        "title_word_count_min": {
                            "type": "integer",
                            "description": "Minimum number of words in keyword",
                            "minimum": 1
                        },
                        "title_word_count_max": {
                            "type": "integer",
                            "description": "Maximum number of words in keyword",
                            "minimum": 1
                        },
                        "keyword_include": {
                            "type": "string",
                            "description": "Regular expression for keywords to be included"
                        },
                        "keyword_exclude": {
                            "type": "string",
                            "description": "Regular expression for keywords to be excluded"
                        },
                        "title_include": {
                            "type": "string",
                            "description": "Regular expression for titles to be included"
                        },
                        "title_exclude": {
                            "type": "string",
                            "description": "Regular expression for titles to be excluded"
                        }
                    },
                    "required": ["input", "keywords"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse des mots-clés d'un domaine"""
        try:
            # Validation des paramètres requis
            input_domain = kwargs.get("input", "").strip()
            keywords = kwargs.get("keywords", [])
            
            if not input_domain:
                return {"error": "Le paramètre 'input' (domaine) est requis"}
            if not keywords or not isinstance(keywords, list):
                return {"error": "Le paramètre 'keywords' est requis et doit être une liste de mots-clés"}
            
            # Préparation des paramètres
            params = {
                "input": input_domain,
                "keywords": keywords,
                "mode": kwargs.get("mode", "auto"),
                "lineCount": kwargs.get("lineCount", 20),
                "page": kwargs.get("page", 1),
                "order_by": kwargs.get("order_by", "default"),
                "order": kwargs.get("order", "asc")
            }
            
            # Ajout des filtres optionnels
            optional_filters = [
                "volume_min", "volume_max", "cpc_min", "cpc_max",
                "competition_min", "competition_max", "kgr_min", "kgr_max",
                "kvi_min", "kvi_max", "kvi_keep_na",
                "allintitle_min", "allintitle_max", "position_min", "position_max",
                "traffic_min", "traffic_max", "title_word_count_min", "title_word_count_max",
                "serp_date_min", "serp_date_max", "keyword_include", "keyword_exclude",
                "title_include", "title_exclude"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            logger.info(f"🔍 Analyse des mots-clés pour {input_domain}: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/keywords", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_domain_keywords_results(response, input_domain, keywords)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des mots-clés du domaine: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des mots-clés du domaine: {str(e)}"}
    
    def _analyze_domain_keywords_results(self, response: Dict[str, Any], input_domain: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyse et synthèse des résultats des mots-clés d'un domaine"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            total_keyword_count = response.get("total_keyword_count", 0)
            filtered_count = response.get("filtered_result_count", 0)
            returned_count = response.get("returned_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucune position trouvée pour {input_domain} sur les mots-clés analysés",
                    "domain": input_domain,
                    "requested_keywords": keywords,
                    "total_keywords": len(keywords),
                    "found_keywords": 0,
                    "keywords_analysis": []
                }
            
            # Analyse des métriques globales
            total_traffic = sum(result.get("traffic", 0) for result in results)
            total_volume = sum(result.get("volume", 0) for result in results)
            
            # Analyse des positions
            positions = [result.get("position", 100) for result in results if result.get("position")]
            top_3_count = sum(1 for pos in positions if pos <= 3)
            top_10_count = sum(1 for pos in positions if pos <= 10)
            top_50_count = sum(1 for pos in positions if pos <= 50)
            
            # Analyse des CPC et compétition
            cpcs = [result.get("cpc", 0) for result in results if result.get("cpc", 0) > 0]
            competitions = [result.get("competition", 0) for result in results if result.get("competition") is not None]
            
            # Analyse des mots-clés individuels
            analyzed_keywords = []
            for result in results:
                keyword_analysis = {
                    "keyword": result.get("keyword", ""),
                    "url": result.get("url", ""),
                    "position": result.get("position"),
                    "traffic": result.get("traffic", 0),
                    "volume": result.get("volume", 0),
                    "cpc": result.get("cpc", 0),
                    "competition": result.get("competition"),
                    "kgr": result.get("kgr"),
                    "allintitle": result.get("allintitle"),
                    "result_count": result.get("result_count", 0),
                    "word_count": result.get("word_count", 0),
                    "last_scrap": result.get("last_scrap", ""),
                    "page_first_seen": result.get("page_first_seen_date", ""),
                    "performance_category": self._categorize_keyword_performance(result),
                    "commercial_value": self._calculate_commercial_value(result)
                }
                analyzed_keywords.append(keyword_analysis)
            
            # Identification des mots-clés par catégorie
            top_performers = [kw for kw in analyzed_keywords if kw["performance_category"] == "top_performer"]
            opportunities = [kw for kw in analyzed_keywords if kw["performance_category"] == "opportunity"]
            commercial_keywords = [kw for kw in analyzed_keywords if kw["commercial_value"] > 50]
            
            # Mots-clés demandés vs trouvés
            found_keywords = [result.get("keyword", "") for result in results]
            missing_keywords = [kw for kw in keywords if kw not in found_keywords]
            
            # Statistiques globales
            stats = {
                "total_results_found": total_count,
                "total_keywords_found": total_keyword_count,
                "keywords_analyzed": returned_count,
                "requested_keywords": len(keywords),
                "found_keywords": len(found_keywords),
                "missing_keywords": len(missing_keywords),
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
                    "volume": total_volume // returned_count if returned_count > 0 else 0,
                    "cpc": sum(cpcs) / len(cpcs) if cpcs else 0,
                    "competition": sum(competitions) / len(competitions) if competitions else 0
                },
                "categories": {
                    "top_performers": len(top_performers),
                    "opportunities": len(opportunities),
                    "commercial_keywords": len(commercial_keywords)
                }
            }
            
            return {
                "summary": f"Analyse de {returned_count} positions pour {input_domain} sur {len(keywords)} mots-clés",
                "domain": input_domain,
                "requested_keywords": keywords,
                "missing_keywords": missing_keywords,
                "statistics": stats,
                "top_performers": top_performers,
                "opportunities": opportunities,
                "commercial_keywords": commercial_keywords,
                "all_keywords": analyzed_keywords,
                "recommendations": self._generate_domain_keywords_recommendations(analyzed_keywords, stats, missing_keywords),
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
    
    def _calculate_commercial_value(self, result: Dict[str, Any]) -> float:
        """Calcule la valeur commerciale d'un mot-clé"""
        volume = result.get("volume", 0)
        cpc = result.get("cpc", 0)
        competition = result.get("competition", 0)
        traffic = result.get("traffic", 0)
        
        # Score basé sur: volume, CPC, compétition, trafic actuel
        volume_score = min(volume / 1000, 25)  # Max 25 points
        cpc_score = min(cpc * 5, 25) if cpc else 0  # Max 25 points
        competition_score = competition * 15 if competition else 0  # Max 15 points
        traffic_score = min(traffic / 100, 35)  # Max 35 points
        
        total_score = volume_score + cpc_score + competition_score + traffic_score
        return round(total_score, 2)
    
    def _generate_domain_keywords_recommendations(self, keywords: List[Dict[str, Any]], stats: Dict[str, Any], missing_keywords: List[str]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des mots-clés du domaine"""
        recommendations = []
        
        if not keywords:
            return ["Aucune position trouvée pour les mots-clés analysés"]
        
        # Analyse de la couverture
        found_rate = (stats.get("found_keywords", 0) / stats.get("requested_keywords", 1)) * 100
        if found_rate < 50:
            recommendations.append(f"⚠️ Seulement {found_rate:.0f}% des mots-clés ont des positions, travaillez votre SEO")
        elif found_rate > 80:
            recommendations.append(f"🎯 Excellente couverture: {found_rate:.0f}% des mots-clés positionnés")
        
        # Analyse des positions
        avg_position = stats.get("averages", {}).get("position", 0)
        top_10_count = stats.get("position_distribution", {}).get("top_10", 0)
        
        if avg_position < 15:
            recommendations.append("🏆 Excellente position moyenne, optimisez pour le top 3")
        elif avg_position > 30:
            recommendations.append("📈 Position moyenne élevée, renforcez l'autorité du domaine")
        
        if top_10_count > len(keywords) * 0.3:
            recommendations.append("🎯 Bon nombre de mots-clés en top 10, maintenez vos efforts")
        elif top_10_count < len(keywords) * 0.1:
            recommendations.append("🔧 Peu de mots-clés en top 10, travaillez l'optimisation on-page")
        
        # Analyse du trafic
        total_traffic = stats.get("total_traffic", 0)
        if total_traffic > 1000:
            recommendations.append("🚀 Excellent trafic généré par ces mots-clés")
        elif total_traffic < 100:
            recommendations.append("📊 Trafic faible, concentrez-vous sur les mots-clés à fort potentiel")
        
        # Analyse commerciale
        commercial_count = stats.get("categories", {}).get("commercial_keywords", 0)
        if commercial_count > 0:
            recommendations.append(f"💰 {commercial_count} mots-clés à fort potentiel commercial identifiés")
        
        # Mots-clés manquants
        if missing_keywords:
            recommendations.append(f"🔍 {len(missing_keywords)} mots-clés sans position: {', '.join(missing_keywords[:3])}{'...' if len(missing_keywords) > 3 else ''}")
        
        # Recommandation sur les opportunités
        opportunities = stats.get("categories", {}).get("opportunities", 0)
        if opportunities > 0:
            recommendations.append(f"💡 {opportunities} opportunités d'amélioration identifiées")
        
        return recommendations if recommendations else ["📊 Analyse des mots-clés terminée, consultez les données détaillées"]
