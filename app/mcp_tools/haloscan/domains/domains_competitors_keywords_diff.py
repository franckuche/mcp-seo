"""
MCP Tool pour l'endpoint Haloscan domains/siteCompetitors/keywordsDiff
Permet d'analyser les différences de mots-clés entre un domaine et ses concurrents
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_competitors_keywords_diff_tool")

class DomainsCompetitorsKeywordsDiffTool(BaseMCPTool):
    """Outil MCP pour analyser les différences de mots-clés entre un domaine et ses concurrents via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainscompetitorskeywordsdiff"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'analyse des différences de mots-clés avec les concurrents"""
        return {
            "type": "function",
            "function": {
                "name": "domains_competitors_keywords_diff",
                "description": "Analyze keyword differences between a domain and its competitors to identify opportunities, gaps, and competitive advantages in search rankings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The domain or URL to analyze (e.g., 'example.com' or 'https://example.com')"
                        },
                        "competitors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of competitor domains to compare against. Use 'auto' for automatic competitor detection",
                            "default": ["auto"]
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["auto", "root", "domain", "url"],
                            "description": "Whether to look for a domain or a full URL. Leave empty for auto detection",
                            "default": "auto"
                        },
                        "exclusive": {
                            "type": "boolean",
                            "description": "Include positions where only the search input is positioned, and none of the competitors"
                        },
                        "missing": {
                            "type": "boolean",
                            "description": "Include positions where the search input is not positioned, but at least one competitor is"
                        },
                        "besting": {
                            "type": "boolean",
                            "description": "Include positions where the search input is positioned better than at least one competitor"
                        },
                        "bested": {
                            "type": "boolean",
                            "description": "Include positions where the search input is positioned worse than at least one competitor"
                        },
                        "acceptedTypes": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["missing", "exclusive", "besting", "bested", "mixed"]
                            },
                            "description": "Filter by keyword comparison types"
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
                            "enum": ["default", "best_reference_position", "best_reference_url", "best_reference_traffic", "best_competitor_position", "best_competitor_traffic", "competitors_positions", "unique_competitors_count", "type", "keyword", "volume", "cpc", "competition", "allintitle", "result_count", "kgr", "word_count", "best_competitor_url"],
                            "description": "Field used for sorting results. Default sorts by descending unique_competitors_count, then by descending best_competitor_traffic",
                            "default": "default"
                        },
                        "best_competitor_traffic_min": {
                            "type": "integer",
                            "description": "Minimum best competitor traffic filter",
                            "minimum": 0
                        },
                        "best_competitor_traffic_max": {
                            "type": "integer",
                            "description": "Maximum best competitor traffic filter",
                            "minimum": 0
                        },
                        "best_competitor_position_min": {
                            "type": "integer",
                            "description": "Minimum best competitor position filter",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "best_competitor_position_max": {
                            "type": "integer",
                            "description": "Maximum best competitor position filter",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "best_reference_traffic_min": {
                            "type": "integer",
                            "description": "Minimum best reference traffic filter",
                            "minimum": 0
                        },
                        "best_reference_traffic_max": {
                            "type": "integer",
                            "description": "Maximum best reference traffic filter",
                            "minimum": 0
                        },
                        "best_reference_position_min": {
                            "type": "integer",
                            "description": "Minimum best reference position filter",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "best_reference_position_max": {
                            "type": "integer",
                            "description": "Maximum best reference position filter",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "competitors_positions_min": {
                            "type": "integer",
                            "description": "Minimum competitors positions filter",
                            "minimum": 0
                        },
                        "competitors_positions_max": {
                            "type": "integer",
                            "description": "Maximum competitors positions filter",
                            "minimum": 0
                        },
                        "unique_competitors_count_min": {
                            "type": "integer",
                            "description": "Minimum unique competitors count filter",
                            "minimum": 0
                        },
                        "unique_competitors_count_max": {
                            "type": "integer",
                            "description": "Maximum unique competitors count filter",
                            "minimum": 0
                        },
                        "keyword_word_count_min": {
                            "type": "integer",
                            "description": "Minimum word count in keyword",
                            "minimum": 1
                        },
                        "keyword_word_count_max": {
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
                        "allintitle_min": {
                            "type": "integer",
                            "description": "Minimum allintitle count",
                            "minimum": 0
                        },
                        "allintitle_max": {
                            "type": "integer",
                            "description": "Maximum allintitle count",
                            "minimum": 0
                        }
                    },
                    "required": ["input"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse des différences de mots-clés avec les concurrents"""
        try:
            # Validation des paramètres requis
            input_domain = kwargs.get("input", "").strip()
            
            if not input_domain:
                return {"error": "Le paramètre 'input' (domaine) est requis"}
            
            # Préparation des paramètres
            params = {
                "input": input_domain,
                "competitors": kwargs.get("competitors", ["auto"]),
                "mode": kwargs.get("mode", "auto"),
                "lineCount": kwargs.get("lineCount", 20),
                "page": kwargs.get("page", 1),
                "order_by": kwargs.get("order_by", "default")
            }
            
            # Ajout des filtres de type de comparaison
            comparison_filters = ["exclusive", "missing", "besting", "bested"]
            for filter_param in comparison_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            if "acceptedTypes" in kwargs and kwargs["acceptedTypes"]:
                params["acceptedTypes"] = kwargs["acceptedTypes"]
            
            # Ajout des filtres optionnels
            optional_filters = [
                "best_competitor_traffic_min", "best_competitor_traffic_max", "best_competitor_traffic_keep_na",
                "best_competitor_position_min", "best_competitor_position_max",
                "best_reference_traffic_min", "best_reference_traffic_max", "best_reference_traffic_keep_na",
                "best_reference_position_min", "best_reference_position_max",
                "competitors_positions_min", "competitors_positions_max",
                "unique_competitors_count_min", "unique_competitors_count_max",
                "keyword_word_count_min", "keyword_word_count_max",
                "keyword_include", "keyword_exclude",
                "volume_min", "volume_max", "volume_keep_na",
                "cpc_min", "cpc_max", "cpc_keep_na",
                "competition_min", "competition_max", "competition_keep_na",
                "kgr_min", "kgr_max", "kgr_keep_na",
                "kvi_min", "kvi_max", "kvi_keep_na",
                "allintitle_min", "allintitle_max", "allintitle_keep_na",
                "google_indexed_min", "google_indexed_max", "google_indexed_keep_na"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            competitors_str = ", ".join(params["competitors"][:3]) + ("..." if len(params["competitors"]) > 3 else "")
            logger.info(f"🔍 Analyse des différences de mots-clés pour {input_domain} vs {competitors_str}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/siteCompetitors/keywordsDiff", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_competitors_keywords_diff_results(response, input_domain, params["competitors"])
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des différences de mots-clés: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des différences de mots-clés: {str(e)}"}
    
    def _analyze_competitors_keywords_diff_results(self, response: Dict[str, Any], input_domain: str, competitors: List[str]) -> Dict[str, Any]:
        """Analyse et synthèse des résultats des différences de mots-clés avec les concurrents"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            filtered_count = response.get("filtered_result_count", 0)
            returned_count = response.get("returned_result_count", 0)
            result_summary = response.get("result_summary", [])
            filtered_summary = response.get("filtered_result_summary", [])
            
            if not results:
                return {
                    "summary": f"Aucune différence de mots-clés trouvée entre {input_domain} et ses concurrents",
                    "domain": input_domain,
                    "competitors": competitors,
                    "total_keywords": 0,
                    "keywords_analysis": []
                }
            
            # Analyse des métriques globales par type
            type_analysis = {}
            for keyword in results:
                keyword_type = keyword.get("type", "unknown")
                if keyword_type not in type_analysis:
                    type_analysis[keyword_type] = {
                        "count": 0,
                        "total_volume": 0,
                        "total_competitor_traffic": 0,
                        "total_reference_traffic": 0,
                        "keywords": []
                    }
                
                type_analysis[keyword_type]["count"] += 1
                type_analysis[keyword_type]["total_volume"] += keyword.get("volume", 0)
                type_analysis[keyword_type]["total_competitor_traffic"] += keyword.get("best_competitor_traffic", 0)
                type_analysis[keyword_type]["total_reference_traffic"] += keyword.get("best_reference_traffic", 0)
                type_analysis[keyword_type]["keywords"].append(keyword)
            
            # Analyse des mots-clés individuels
            analyzed_keywords = []
            for keyword in results:
                keyword_analysis = {
                    "keyword": keyword.get("keyword", ""),
                    "type": keyword.get("type", ""),
                    "volume": keyword.get("volume", 0),
                    "cpc": keyword.get("cpc", 0),
                    "competition": keyword.get("competition"),
                    "kgr": keyword.get("kgr"),
                    "allintitle": keyword.get("allintitle"),
                    "result_count": keyword.get("result_count", 0),
                    "word_count": keyword.get("word_count", 0),
                    "competitor_data": {
                        "best_position": keyword.get("best_competitor_position"),
                        "best_traffic": keyword.get("best_competitor_traffic", 0),
                        "best_url": keyword.get("best_competitor_url", ""),
                        "positions_count": keyword.get("competitors_positions", 0),
                        "unique_count": keyword.get("unique_competitors_count", 0)
                    },
                    "reference_data": {
                        "best_position": keyword.get("best_reference_position"),
                        "best_traffic": keyword.get("best_reference_traffic", 0),
                        "best_url": keyword.get("best_reference_url", "")
                    },
                    "opportunity_score": self._calculate_opportunity_score(keyword),
                    "priority_level": self._determine_priority_level(keyword)
                }
                analyzed_keywords.append(keyword_analysis)
            
            # Identification des opportunités par type
            opportunities = {
                "missing": [kw for kw in analyzed_keywords if kw["type"] == "missing"],
                "bested": [kw for kw in analyzed_keywords if kw["type"] == "bested"],
                "exclusive": [kw for kw in analyzed_keywords if kw["type"] == "exclusive"],
                "besting": [kw for kw in analyzed_keywords if kw["type"] == "besting"],
                "mixed": [kw for kw in analyzed_keywords if kw["type"] == "mixed"]
            }
            
            # Top opportunités par score
            top_opportunities = sorted(analyzed_keywords, key=lambda x: x["opportunity_score"], reverse=True)[:10]
            
            # Statistiques globales
            stats = {
                "total_keywords_found": total_count,
                "keywords_analyzed": returned_count,
                "type_distribution": {t: data["count"] for t, data in type_analysis.items()},
                "volume_by_type": {t: data["total_volume"] for t, data in type_analysis.items()},
                "traffic_potential": {
                    "competitor_traffic": sum(data["total_competitor_traffic"] for data in type_analysis.values()),
                    "reference_traffic": sum(data["total_reference_traffic"] for data in type_analysis.values())
                },
                "summary_stats": self._process_summary_stats(result_summary, filtered_summary)
            }
            
            return {
                "summary": f"Analyse comparative de {returned_count} mots-clés entre {input_domain} et ses concurrents",
                "domain": input_domain,
                "competitors": competitors,
                "statistics": stats,
                "opportunities_by_type": opportunities,
                "top_opportunities": top_opportunities,
                "type_analysis": type_analysis,
                "all_keywords": analyzed_keywords,
                "recommendations": self._generate_competitors_diff_recommendations(analyzed_keywords, stats, opportunities),
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
    
    def _calculate_opportunity_score(self, keyword: Dict[str, Any]) -> float:
        """Calcule un score d'opportunité pour un mot-clé basé sur le type et les métriques"""
        keyword_type = keyword.get("type", "")
        volume = keyword.get("volume", 0)
        competitor_traffic = keyword.get("best_competitor_traffic", 0)
        competitor_position = keyword.get("best_competitor_position", 100)
        reference_position = keyword.get("best_reference_position", 100)
        
        # Score de base selon le type
        type_scores = {
            "missing": 80,      # Forte opportunité
            "bested": 60,       # Opportunité d'amélioration
            "mixed": 40,        # Opportunité mixte
            "besting": 20,      # Maintenir l'avantage
            "exclusive": 10     # Déjà exclusif
        }
        
        base_score = type_scores.get(keyword_type, 0)
        
        # Bonus pour volume élevé
        volume_bonus = min(volume / 1000, 20)
        
        # Bonus pour trafic concurrent élevé
        traffic_bonus = min(competitor_traffic / 100, 15)
        
        # Bonus pour position concurrent accessible
        position_bonus = max(0, (100 - competitor_position) / 10) if competitor_position else 0
        
        total_score = base_score + volume_bonus + traffic_bonus + position_bonus
        return round(total_score, 2)
    
    def _determine_priority_level(self, keyword: Dict[str, Any]) -> str:
        """Détermine le niveau de priorité d'un mot-clé"""
        opportunity_score = self._calculate_opportunity_score(keyword)
        
        if opportunity_score >= 80:
            return "high"
        elif opportunity_score >= 50:
            return "medium"
        elif opportunity_score >= 20:
            return "low"
        else:
            return "minimal"
    
    def _process_summary_stats(self, result_summary: List[Dict], filtered_summary: List[Dict]) -> Dict[str, Any]:
        """Traite les statistiques de résumé"""
        summary_stats = {
            "total_by_competitor_count": {},
            "filtered_by_competitor_count": {}
        }
        
        for summary in result_summary:
            competitor_count = summary.get("unique_competitors_count", 0)
            summary_stats["total_by_competitor_count"][competitor_count] = {
                "exclusive": summary.get("exclusive", 0),
                "missing": summary.get("missing", 0),
                "besting": summary.get("besting", 0),
                "bested": summary.get("bested", 0),
                "mixed": summary.get("mixed", 0)
            }
        
        for summary in filtered_summary:
            competitor_count = summary.get("unique_competitors_count", 0)
            summary_stats["filtered_by_competitor_count"][competitor_count] = {
                "exclusive": summary.get("exclusive", 0),
                "missing": summary.get("missing", 0),
                "besting": summary.get("besting", 0),
                "bested": summary.get("bested", 0),
                "mixed": summary.get("mixed", 0)
            }
        
        return summary_stats
    
    def _generate_competitors_diff_recommendations(self, keywords: List[Dict[str, Any]], stats: Dict[str, Any], opportunities: Dict[str, List]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des différences avec les concurrents"""
        recommendations = []
        
        if not keywords:
            return ["Aucune différence significative trouvée avec les concurrents"]
        
        # Analyse des opportunités manquantes
        missing_count = len(opportunities.get("missing", []))
        if missing_count > 0:
            recommendations.append(f"🎯 {missing_count} mots-clés manqués: opportunités de contenu à créer")
        
        # Analyse des mots-clés où on est battu
        bested_count = len(opportunities.get("bested", []))
        if bested_count > 0:
            recommendations.append(f"📈 {bested_count} mots-clés à améliorer: optimisation SEO nécessaire")
        
        # Analyse des avantages exclusifs
        exclusive_count = len(opportunities.get("exclusive", []))
        if exclusive_count > 0:
            recommendations.append(f"🏆 {exclusive_count} mots-clés exclusifs: maintenez cet avantage concurrentiel")
        
        # Analyse des positions dominantes
        besting_count = len(opportunities.get("besting", []))
        if besting_count > 0:
            recommendations.append(f"🚀 {besting_count} mots-clés où vous dominez: renforcez ces positions")
        
        # Analyse du potentiel de trafic
        competitor_traffic = stats.get("traffic_potential", {}).get("competitor_traffic", 0)
        if competitor_traffic > 1000:
            recommendations.append(f"💰 Potentiel de trafic concurrent: {competitor_traffic:.0f} visites/mois à capturer")
        
        # Top opportunités
        if keywords:
            top_opportunity = max(keywords, key=lambda x: x["opportunity_score"])
            if top_opportunity["opportunity_score"] > 50:
                recommendations.append(f"🌟 Priorité absolue: '{top_opportunity['keyword']}' (score: {top_opportunity['opportunity_score']})")
        
        # Analyse de la distribution des types
        type_dist = stats.get("type_distribution", {})
        total_keywords = sum(type_dist.values())
        
        if type_dist.get("missing", 0) > total_keywords * 0.3:
            recommendations.append("⚠️ Beaucoup de mots-clés manqués, développez votre stratégie de contenu")
        
        if type_dist.get("exclusive", 0) > total_keywords * 0.2:
            recommendations.append("🎪 Forte différenciation SEO, capitalisez sur vos avantages uniques")
        
        # Recommandations sur les volumes
        high_volume_missing = [kw for kw in opportunities.get("missing", []) if kw["volume"] > 1000]
        if high_volume_missing:
            recommendations.append(f"🔥 {len(high_volume_missing)} mots-clés manqués à fort volume identifiés")
        
        return recommendations if recommendations else ["📊 Analyse concurrentielle terminée, consultez les données détaillées"]
