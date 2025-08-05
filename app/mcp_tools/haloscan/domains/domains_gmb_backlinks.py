"""
MCP Tool pour l'endpoint Haloscan domains/gmbBacklinks
Permet d'analyser les backlinks Google My Business d'un domaine
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_gmb_backlinks_tool")

class DomainsGmbBacklinksTool(BaseMCPTool):
    """Outil MCP pour analyser les backlinks Google My Business d'un domaine via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainsgmbbacklinks"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'analyse des backlinks GMB"""
        return {
            "type": "function",
            "function": {
                "name": "domains_gmb_backlinks",
                "description": "Analyze Google My Business backlinks for a domain to discover local business listings, reviews, and local SEO opportunities.",
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
                            "enum": ["default", "rating_count", "rating_value", "is_claimed", "total_photos", "name", "address", "phone", "longitude", "latitude", "categories", "url", "domain", "root_domain"],
                            "description": "Field used for sorting results. Default sorts by descending rating_count, then by descending rating_value",
                            "default": "default"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Whether the results are sorted in ascending or descending order",
                            "default": "asc"
                        },
                        "rating_count_min": {
                            "type": "integer",
                            "description": "Minimum rating count filter",
                            "minimum": 0
                        },
                        "rating_count_max": {
                            "type": "integer",
                            "description": "Maximum rating count filter",
                            "minimum": 0
                        },
                        "rating_value_min": {
                            "type": "number",
                            "description": "Minimum rating value filter (0-5)",
                            "minimum": 0,
                            "maximum": 5
                        },
                        "rating_value_max": {
                            "type": "number",
                            "description": "Maximum rating value filter (0-5)",
                            "minimum": 0,
                            "maximum": 5
                        },
                        "latitude_min": {
                            "type": "number",
                            "description": "Minimum latitude filter"
                        },
                        "latitude_max": {
                            "type": "number",
                            "description": "Maximum latitude filter"
                        },
                        "longitude_min": {
                            "type": "number",
                            "description": "Minimum longitude filter"
                        },
                        "longitude_max": {
                            "type": "number",
                            "description": "Maximum longitude filter"
                        },
                        "categories_include": {
                            "type": "string",
                            "description": "Regular expression for categories to be included"
                        },
                        "categories_exclude": {
                            "type": "string",
                            "description": "Regular expression for categories to be excluded"
                        },
                        "is_claimed": {
                            "type": "boolean",
                            "description": "When FALSE, only return unclaimed companies. When TRUE, only return claimed companies. Leave empty if you don't want to filter."
                        }
                    },
                    "required": ["input"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse des backlinks GMB d'un domaine"""
        try:
            # Validation des paramètres requis
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
                "order": kwargs.get("order", "asc")
            }
            
            # Ajout des filtres optionnels
            optional_filters = [
                "rating_count_min", "rating_count_max", "rating_count_keep_na",
                "rating_value_min", "rating_value_max", "rating_value_keep_na",
                "latitude_min", "latitude_max", "latitude_keep_na",
                "longitude_min", "longitude_max", "longitude_keep_na",
                "categories_include", "categories_exclude", "is_claimed"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            logger.info(f"🔍 Analyse des backlinks GMB pour {input_domain}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/gmbBacklinks", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_gmb_backlinks_results(response, input_domain)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des backlinks GMB: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des backlinks GMB: {str(e)}"}
    
    def _analyze_gmb_backlinks_results(self, response: Dict[str, Any], input_domain: str) -> Dict[str, Any]:
        """Analyse et synthèse des résultats des backlinks GMB"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            filtered_count = response.get("filtered_result_count", 0)
            returned_count = response.get("returned_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucun backlink GMB trouvé pour {input_domain}",
                    "domain": input_domain,
                    "total_businesses": 0,
                    "businesses": []
                }
            
            # Analyse des entreprises individuelles
            analyzed_businesses = []
            for business in results:
                business_analysis = {
                    "cid": business.get("cid", ""),
                    "name": business.get("name", ""),
                    "address": business.get("address", ""),
                    "phone": business.get("phone", ""),
                    "url": business.get("url", ""),
                    "domain": business.get("domain", ""),
                    "root_domain": business.get("root_domain", ""),
                    "location": {
                        "latitude": business.get("latitude"),
                        "longitude": business.get("longitude")
                    },
                    "ratings": {
                        "count": business.get("rating_count", 0),
                        "value": business.get("rating_value", 0),
                        "quality_score": self._calculate_rating_quality(business.get("rating_count", 0), business.get("rating_value", 0))
                    },
                    "categories": business.get("categories", ""),
                    "is_claimed": bool(business.get("is_claimed", 0)),
                    "total_photos": business.get("total_photos", 0),
                    "business_quality": self._assess_business_quality(business),
                    "local_seo_value": self._calculate_local_seo_value(business)
                }
                analyzed_businesses.append(business_analysis)
            
            # Analyse des catégories
            categories_analysis = self._analyze_categories(analyzed_businesses)
            
            # Analyse géographique
            geographic_analysis = self._analyze_geographic_distribution(analyzed_businesses)
            
            # Analyse de la qualité
            quality_analysis = self._analyze_business_quality(analyzed_businesses)
            
            # Top businesses par différents critères
            top_rated = sorted([b for b in analyzed_businesses if b["ratings"]["count"] > 0], 
                             key=lambda x: (x["ratings"]["value"], x["ratings"]["count"]), reverse=True)[:5]
            
            most_reviewed = sorted(analyzed_businesses, key=lambda x: x["ratings"]["count"], reverse=True)[:5]
            
            high_seo_value = sorted(analyzed_businesses, key=lambda x: x["local_seo_value"], reverse=True)[:5]
            
            # Statistiques globales
            stats = {
                "total_businesses_found": total_count,
                "businesses_analyzed": returned_count,
                "claimed_businesses": sum(1 for b in analyzed_businesses if b["is_claimed"]),
                "unclaimed_businesses": sum(1 for b in analyzed_businesses if not b["is_claimed"]),
                "businesses_with_ratings": sum(1 for b in analyzed_businesses if b["ratings"]["count"] > 0),
                "businesses_with_photos": sum(1 for b in analyzed_businesses if b["total_photos"] > 0),
                "average_rating": round(sum(b["ratings"]["value"] for b in analyzed_businesses if b["ratings"]["value"] > 0) / 
                                     len([b for b in analyzed_businesses if b["ratings"]["value"] > 0]), 2) if analyzed_businesses else 0,
                "total_reviews": sum(b["ratings"]["count"] for b in analyzed_businesses),
                "total_photos": sum(b["total_photos"] for b in analyzed_businesses)
            }
            
            return {
                "summary": f"Analyse de {returned_count} entreprises GMB liées à {input_domain}",
                "domain": input_domain,
                "statistics": stats,
                "categories_analysis": categories_analysis,
                "geographic_analysis": geographic_analysis,
                "quality_analysis": quality_analysis,
                "top_rated_businesses": top_rated,
                "most_reviewed_businesses": most_reviewed,
                "high_seo_value_businesses": high_seo_value,
                "all_businesses": analyzed_businesses,
                "recommendations": self._generate_gmb_recommendations(analyzed_businesses, stats),
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
    
    def _calculate_rating_quality(self, rating_count: int, rating_value: float) -> str:
        """Calcule la qualité des avis d'une entreprise"""
        if rating_count == 0:
            return "no_ratings"
        elif rating_count < 10:
            return "few_ratings"
        elif rating_value >= 4.5 and rating_count >= 50:
            return "excellent"
        elif rating_value >= 4.0 and rating_count >= 20:
            return "good"
        elif rating_value >= 3.5:
            return "average"
        else:
            return "poor"
    
    def _assess_business_quality(self, business: Dict[str, Any]) -> str:
        """Évalue la qualité globale d'une entreprise GMB"""
        score = 0
        
        # Statut revendiqué
        if business.get("is_claimed", 0):
            score += 30
        
        # Avis
        rating_count = business.get("rating_count", 0)
        rating_value = business.get("rating_value", 0)
        
        if rating_count >= 50:
            score += 25
        elif rating_count >= 20:
            score += 15
        elif rating_count >= 5:
            score += 10
        
        if rating_value >= 4.5:
            score += 20
        elif rating_value >= 4.0:
            score += 15
        elif rating_value >= 3.5:
            score += 10
        
        # Photos
        photos = business.get("total_photos", 0)
        if photos >= 10:
            score += 15
        elif photos >= 5:
            score += 10
        elif photos >= 1:
            score += 5
        
        # Informations complètes
        if business.get("phone"):
            score += 5
        if business.get("address"):
            score += 5
        
        # Classification
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "average"
        else:
            return "poor"
    
    def _calculate_local_seo_value(self, business: Dict[str, Any]) -> float:
        """Calcule la valeur SEO local d'une entreprise"""
        score = 0
        
        # Facteurs de ranking local
        if business.get("is_claimed", 0):
            score += 25
        
        rating_count = business.get("rating_count", 0)
        rating_value = business.get("rating_value", 0)
        
        # Avis (facteur important)
        score += min(rating_count * 0.5, 30)  # Max 30 points
        score += rating_value * 4  # Max 20 points
        
        # Photos (engagement)
        photos = business.get("total_photos", 0)
        score += min(photos * 2, 20)  # Max 20 points
        
        # Complétude des informations
        if business.get("phone"):
            score += 2.5
        if business.get("address"):
            score += 2.5
        
        return round(score, 2)
    
    def _analyze_categories(self, businesses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse la distribution des catégories d'entreprises"""
        categories_count = {}
        all_categories = []
        
        for business in businesses:
            categories_str = business.get("categories", "")
            if categories_str:
                categories = [cat.strip() for cat in categories_str.split(",")]
                all_categories.extend(categories)
                
                for category in categories:
                    if category not in categories_count:
                        categories_count[category] = 0
                    categories_count[category] += 1
        
        # Top catégories
        top_categories = dict(sorted(categories_count.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            "total_unique_categories": len(categories_count),
            "top_categories": top_categories,
            "most_common_category": max(categories_count.items(), key=lambda x: x[1])[0] if categories_count else None
        }
    
    def _analyze_geographic_distribution(self, businesses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse la distribution géographique des entreprises"""
        locations = []
        for business in businesses:
            lat = business.get("location", {}).get("latitude")
            lng = business.get("location", {}).get("longitude")
            if lat is not None and lng is not None:
                locations.append({"lat": lat, "lng": lng})
        
        if not locations:
            return {"has_location_data": False}
        
        # Calcul du centre géographique
        center_lat = sum(loc["lat"] for loc in locations) / len(locations)
        center_lng = sum(loc["lng"] for loc in locations) / len(locations)
        
        # Calcul de la dispersion
        distances = []
        for loc in locations:
            # Distance approximative en km
            lat_diff = abs(loc["lat"] - center_lat)
            lng_diff = abs(loc["lng"] - center_lng)
            distance = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111  # Approximation
            distances.append(distance)
        
        avg_distance = sum(distances) / len(distances) if distances else 0
        max_distance = max(distances) if distances else 0
        
        return {
            "has_location_data": True,
            "businesses_with_location": len(locations),
            "geographic_center": {"latitude": round(center_lat, 6), "longitude": round(center_lng, 6)},
            "dispersion": {
                "average_distance_km": round(avg_distance, 2),
                "max_distance_km": round(max_distance, 2),
                "concentration_level": "high" if avg_distance < 10 else "medium" if avg_distance < 50 else "low"
            }
        }
    
    def _analyze_business_quality(self, businesses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse la qualité globale des entreprises"""
        quality_distribution = {"excellent": 0, "good": 0, "average": 0, "poor": 0}
        
        for business in businesses:
            quality = business.get("business_quality", "poor")
            if quality in quality_distribution:
                quality_distribution[quality] += 1
        
        claimed_rate = sum(1 for b in businesses if b["is_claimed"]) / len(businesses) * 100 if businesses else 0
        
        return {
            "quality_distribution": quality_distribution,
            "claimed_rate": round(claimed_rate, 1),
            "average_seo_value": round(sum(b["local_seo_value"] for b in businesses) / len(businesses), 2) if businesses else 0
        }
    
    def _generate_gmb_recommendations(self, businesses: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des backlinks GMB"""
        recommendations = []
        
        if not businesses:
            return ["Aucune entreprise GMB trouvée pour ce domaine"]
        
        # Analyse du statut de revendication
        claimed_rate = (stats.get("claimed_businesses", 0) / stats.get("businesses_analyzed", 1)) * 100
        if claimed_rate < 70:
            recommendations.append(f"🏢 Seulement {claimed_rate:.0f}% des entreprises sont revendiquées, opportunité d'amélioration")
        elif claimed_rate > 90:
            recommendations.append("✅ Excellent taux de revendication des entreprises")
        
        # Analyse des avis
        avg_rating = stats.get("average_rating", 0)
        if avg_rating >= 4.5:
            recommendations.append("⭐ Excellente réputation moyenne, maintenez la qualité")
        elif avg_rating < 3.5:
            recommendations.append("📈 Note moyenne faible, travaillez l'expérience client")
        
        businesses_with_ratings = stats.get("businesses_with_ratings", 0)
        total_businesses = stats.get("businesses_analyzed", 1)
        rating_coverage = (businesses_with_ratings / total_businesses) * 100
        
        if rating_coverage < 50:
            recommendations.append("💬 Peu d'entreprises ont des avis, encouragez les retours clients")
        
        # Analyse des photos
        businesses_with_photos = stats.get("businesses_with_photos", 0)
        photo_coverage = (businesses_with_photos / total_businesses) * 100
        
        if photo_coverage < 60:
            recommendations.append("📸 Ajoutez plus de photos pour améliorer l'engagement")
        
        # Top performers
        high_quality = [b for b in businesses if b["business_quality"] in ["excellent", "good"]]
        if high_quality:
            recommendations.append(f"🌟 {len(high_quality)} entreprise(s) de qualité identifiée(s)")
        
        # Opportunités SEO local
        high_seo_businesses = [b for b in businesses if b["local_seo_value"] > 70]
        if high_seo_businesses:
            recommendations.append(f"🚀 {len(high_seo_businesses)} entreprise(s) à fort potentiel SEO local")
        
        # Analyse géographique
        if len(businesses) > 5:
            recommendations.append("🗺️ Présence géographique diversifiée, bon pour le SEO local")
        
        # Recommandation générale
        total_reviews = stats.get("total_reviews", 0)
        if total_reviews > 500:
            recommendations.append("💪 Forte base d'avis clients, excellent signal de confiance")
        
        return recommendations if recommendations else ["📊 Analyse GMB terminée, consultez les données détaillées"]
