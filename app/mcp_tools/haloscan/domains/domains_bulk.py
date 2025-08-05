"""
MCP Tool pour l'endpoint Haloscan domains/bulk
Permet d'analyser plusieurs domaines en une seule requête avec leurs métriques SEO
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_bulk_tool")

class DomainsBulkTool(BaseMCPTool):
    """Outil MCP pour analyser plusieurs domaines en bulk via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainsbulk"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'analyse bulk de domaines"""
        return {
            "type": "function",
            "function": {
                "name": "domains_bulk",
                "description": "Analyze multiple domains in bulk to compare their SEO performance metrics including traffic, keywords, positions, and rankings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "inputs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of domains or URLs to analyze (e.g., ['example1.com', 'example2.com'])",
                            "minItems": 1,
                            "maxItems": 50
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
                            "enum": ["keep", "first_time_seen", "last_time_seen", "indexed_pages", "unique_keywords", "total_traffic", "total_top_100", "total_top_50", "total_top_10", "total_top_3", "name", "type", "total_traffic_value"],
                            "description": "Field used for sorting results. 'keep' preserves the original input order",
                            "default": "keep"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Whether the results are sorted in ascending or descending order",
                            "default": "asc"
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
                        "total_top_3_max": {
                            "type": "integer",
                            "description": "Maximum top 3 positions filter",
                            "minimum": 0
                        },
                        "total_top_10_min": {
                            "type": "integer",
                            "description": "Minimum top 10 positions filter",
                            "minimum": 0
                        },
                        "total_top_10_max": {
                            "type": "integer",
                            "description": "Maximum top 10 positions filter",
                            "minimum": 0
                        },
                        "total_top_50_min": {
                            "type": "integer",
                            "description": "Minimum top 50 positions filter",
                            "minimum": 0
                        },
                        "total_top_50_max": {
                            "type": "integer",
                            "description": "Maximum top 50 positions filter",
                            "minimum": 0
                        },
                        "total_top_100_min": {
                            "type": "integer",
                            "description": "Minimum top 100 positions filter",
                            "minimum": 0
                        },
                        "total_top_100_max": {
                            "type": "integer",
                            "description": "Maximum top 100 positions filter",
                            "minimum": 0
                        }
                    },
                    "required": ["inputs"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse bulk de domaines"""
        try:
            # Validation des paramètres requis
            inputs = kwargs.get("inputs", [])
            
            if not inputs or not isinstance(inputs, list):
                return {"error": "Le paramètre 'inputs' est requis et doit être une liste de domaines"}
            if len(inputs) > 50:
                return {"error": "Maximum 50 domaines autorisés par requête bulk"}
            
            # Préparation des paramètres
            params = {
                "inputs": inputs,
                "mode": kwargs.get("mode", "auto"),
                "lineCount": kwargs.get("lineCount", 20),
                "page": kwargs.get("page", 1),
                "order_by": kwargs.get("order_by", "keep"),
                "order": kwargs.get("order", "asc")
            }
            
            # Ajout des filtres optionnels
            optional_filters = [
                "total_traffic_min", "total_traffic_max",
                "unique_keywords_min", "unique_keywords_max",
                "total_top_3_min", "total_top_3_max",
                "total_top_10_min", "total_top_10_max",
                "total_top_50_min", "total_top_50_max",
                "total_top_100_min", "total_top_100_max"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            logger.info(f"🔍 Analyse bulk de {len(inputs)} domaines: {', '.join(inputs[:3])}{'...' if len(inputs) > 3 else ''}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/bulk", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_bulk_domains_results(response, inputs)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse bulk des domaines: {str(e)}")
            return {"error": f"Erreur lors de l'analyse bulk des domaines: {str(e)}"}
    
    def _analyze_bulk_domains_results(self, response: Dict[str, Any], inputs: List[str]) -> Dict[str, Any]:
        """Analyse et synthèse des résultats de l'analyse bulk de domaines"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            known_item_count = response.get("known_item_count", 0)
            filtered_count = response.get("filtered_result_count", 0)
            returned_count = response.get("returned_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucune donnée trouvée pour les {len(inputs)} domaines analysés",
                    "requested_domains": inputs,
                    "total_domains": len(inputs),
                    "found_domains": 0,
                    "domains_analysis": []
                }
            
            # Analyse des métriques globales
            total_traffic = sum(domain.get("total_traffic", 0) for domain in results)
            total_keywords = sum(domain.get("unique_keywords", 0) for domain in results)
            total_pages = sum(domain.get("indexed_pages", 0) for domain in results)
            total_top_10 = sum(domain.get("total_top_10", 0) for domain in results)
            
            # Analyse des domaines individuels
            analyzed_domains = []
            for domain in results:
                domain_analysis = {
                    "url": domain.get("url", ""),
                    "type": domain.get("type", ""),
                    "traffic": domain.get("total_traffic", 0),
                    "traffic_value": domain.get("total_traffic_value", 0),
                    "keywords": domain.get("unique_keywords", 0),
                    "indexed_pages": domain.get("indexed_pages", 0),
                    "positions": {
                        "top_3": domain.get("total_top_3", 0),
                        "top_10": domain.get("total_top_10", 0),
                        "top_50": domain.get("total_top_50", 0),
                        "top_100": domain.get("total_top_100", 0)
                    },
                    "timeline": {
                        "first_seen": domain.get("first_time_seen", ""),
                        "last_seen": domain.get("last_time_seen", "")
                    },
                    "rankings": {
                        "traffic_rank": domain.get("traffic_rank"),
                        "page_count_rank": domain.get("page_count_rank"),
                        "keyword_count_rank": domain.get("keyword_count_rank")
                    },
                    "performance_score": self._calculate_domain_performance_score(domain),
                    "authority_level": self._determine_authority_level(domain)
                }
                analyzed_domains.append(domain_analysis)
            
            # Tri par performance
            top_performers = sorted(analyzed_domains, key=lambda x: x["performance_score"], reverse=True)
            
            # Identification des leaders par catégorie
            leaders = {
                "traffic_leader": max(analyzed_domains, key=lambda x: x["traffic"]) if analyzed_domains else None,
                "keywords_leader": max(analyzed_domains, key=lambda x: x["keywords"]) if analyzed_domains else None,
                "pages_leader": max(analyzed_domains, key=lambda x: x["indexed_pages"]) if analyzed_domains else None,
                "positions_leader": max(analyzed_domains, key=lambda x: x["positions"]["top_10"]) if analyzed_domains else None
            }
            
            # Domaines demandés vs trouvés
            found_domains = [domain.get("url", "") for domain in results]
            missing_domains = [domain for domain in inputs if domain not in found_domains]
            
            # Statistiques globales
            stats = {
                "total_domains_requested": len(inputs),
                "domains_found": known_item_count,
                "domains_analyzed": returned_count,
                "missing_domains": len(missing_domains),
                "aggregate_metrics": {
                    "total_traffic": total_traffic,
                    "total_keywords": total_keywords,
                    "total_pages": total_pages,
                    "total_top_10": total_top_10
                },
                "averages": {
                    "traffic_per_domain": total_traffic // returned_count if returned_count > 0 else 0,
                    "keywords_per_domain": total_keywords // returned_count if returned_count > 0 else 0,
                    "pages_per_domain": total_pages // returned_count if returned_count > 0 else 0,
                    "top_10_per_domain": total_top_10 // returned_count if returned_count > 0 else 0
                },
                "authority_distribution": self._analyze_authority_distribution(analyzed_domains)
            }
            
            return {
                "summary": f"Analyse comparative de {returned_count} domaines sur {len(inputs)} demandés",
                "requested_domains": inputs,
                "missing_domains": missing_domains,
                "statistics": stats,
                "leaders": leaders,
                "top_performers": top_performers[:10],  # Top 10 performers
                "all_domains": analyzed_domains,
                "recommendations": self._generate_bulk_domains_recommendations(analyzed_domains, stats, missing_domains),
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
    
    def _calculate_domain_performance_score(self, domain: Dict[str, Any]) -> float:
        """Calcule un score de performance global pour un domaine"""
        traffic = domain.get("total_traffic", 0)
        keywords = domain.get("unique_keywords", 0)
        top_10 = domain.get("total_top_10", 0)
        pages = domain.get("indexed_pages", 0)
        
        # Score pondéré : trafic (40%), top 10 (30%), mots-clés (20%), pages (10%)
        traffic_score = min(traffic / 100, 100)  # Max 100 points
        top_10_score = min(top_10 * 2, 75)  # Max 75 points
        keywords_score = min(keywords / 100, 50)  # Max 50 points
        pages_score = min(pages / 1000, 25)  # Max 25 points
        
        total_score = (traffic_score * 0.4) + (top_10_score * 0.3) + (keywords_score * 0.2) + (pages_score * 0.1)
        return round(total_score, 2)
    
    def _determine_authority_level(self, domain: Dict[str, Any]) -> str:
        """Détermine le niveau d'autorité d'un domaine"""
        traffic = domain.get("total_traffic", 0)
        keywords = domain.get("unique_keywords", 0)
        top_10 = domain.get("total_top_10", 0)
        
        if traffic > 10000 and keywords > 5000 and top_10 > 500:
            return "high_authority"
        elif traffic > 1000 and keywords > 1000 and top_10 > 100:
            return "medium_authority"
        elif traffic > 100 and keywords > 100 and top_10 > 10:
            return "low_authority"
        else:
            return "emerging"
    
    def _analyze_authority_distribution(self, domains: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyse la distribution des niveaux d'autorité"""
        distribution = {"high_authority": 0, "medium_authority": 0, "low_authority": 0, "emerging": 0}
        
        for domain in domains:
            authority_level = domain.get("authority_level", "emerging")
            distribution[authority_level] += 1
        
        return distribution
    
    def _generate_bulk_domains_recommendations(self, domains: List[Dict[str, Any]], stats: Dict[str, Any], missing_domains: List[str]) -> List[str]:
        """Génère des recommandations basées sur l'analyse bulk des domaines"""
        recommendations = []
        
        if not domains:
            return ["Aucun domaine trouvé dans la base de données Haloscan"]
        
        # Analyse de la couverture
        found_rate = (stats.get("domains_found", 0) / stats.get("total_domains_requested", 1)) * 100
        if found_rate < 70:
            recommendations.append(f"⚠️ Seulement {found_rate:.0f}% des domaines trouvés dans la base")
        elif found_rate == 100:
            recommendations.append("🎯 Tous les domaines trouvés dans la base de données")
        
        # Analyse des performances
        avg_traffic = stats.get("averages", {}).get("traffic_per_domain", 0)
        if avg_traffic > 5000:
            recommendations.append("🚀 Excellent trafic moyen, domaines très performants")
        elif avg_traffic < 500:
            recommendations.append("📈 Trafic moyen faible, potentiel d'amélioration important")
        
        # Analyse de l'autorité
        authority_dist = stats.get("authority_distribution", {})
        high_auth = authority_dist.get("high_authority", 0)
        if high_auth > 0:
            recommendations.append(f"🏆 {high_auth} domaine(s) à forte autorité identifié(s)")
        
        emerging = authority_dist.get("emerging", 0)
        if emerging > len(domains) * 0.5:
            recommendations.append("🌱 Beaucoup de domaines émergents, opportunités de croissance")
        
        # Leaders par catégorie
        leaders = ["traffic_leader", "keywords_leader", "pages_leader", "positions_leader"]
        leader_domains = []
        for leader_type in leaders:
            leader = None
            if leader_type == "traffic_leader":
                leader = max(domains, key=lambda x: x["traffic"], default=None)
            elif leader_type == "keywords_leader":
                leader = max(domains, key=lambda x: x["keywords"], default=None)
            elif leader_type == "pages_leader":
                leader = max(domains, key=lambda x: x["indexed_pages"], default=None)
            elif leader_type == "positions_leader":
                leader = max(domains, key=lambda x: x["positions"]["top_10"], default=None)
            
            if leader and leader["url"] not in leader_domains:
                leader_domains.append(leader["url"])
        
        if leader_domains:
            recommendations.append(f"🌟 Domaines leaders: {', '.join(leader_domains[:3])}{'...' if len(leader_domains) > 3 else ''}")
        
        # Domaines manquants
        if missing_domains:
            recommendations.append(f"🔍 {len(missing_domains)} domaines non trouvés: {', '.join(missing_domains[:3])}{'...' if len(missing_domains) > 3 else ''}")
        
        # Recommandation sur la diversité
        if len(domains) > 5:
            recommendations.append("📊 Analyse comparative disponible, identifiez les meilleures pratiques")
        
        return recommendations if recommendations else ["📊 Analyse bulk terminée, consultez les données détaillées"]
