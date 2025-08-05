"""
MCP Tool pour l'endpoint Haloscan domains/gmbBacklinks/categories
Permet d'analyser les catégories des backlinks Google My Business d'un domaine
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_gmb_backlinks_categories_tool")

class DomainsGmbBacklinksCategoresTool(BaseMCPTool):
    """Outil MCP pour l'analyse des catégories de backlinks Google My Business via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainsgmbbacklinkscategories"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'analyse des catégories GMB"""
        return {
            "type": "function",
            "function": {
                "name": "domains_gmb_backlinks_categories",
                "description": "Analyze the categories distribution of Google My Business backlinks for a domain to understand the business types and industries linking to the domain.",
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
                            "description": "Maximum number of category results to analyze",
                            "default": 100,
                            "minimum": 1,
                            "maximum": 500
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number for pagination",
                            "default": 1,
                            "minimum": 1
                        },
                        "min_businesses_per_category": {
                            "type": "integer",
                            "description": "Minimum number of businesses required for a category to be included in results",
                            "default": 1,
                            "minimum": 1
                        },
                        "category_filter": {
                            "type": "string",
                            "description": "Regular expression to filter specific categories"
                        },
                        "include_subcategories": {
                            "type": "boolean",
                            "description": "Whether to include subcategory analysis",
                            "default": True
                        },
                        "rating_count_min": {
                            "type": "integer",
                            "description": "Minimum rating count for businesses to be included in category analysis",
                            "minimum": 0
                        },
                        "rating_value_min": {
                            "type": "number",
                            "description": "Minimum rating value (0-5) for businesses to be included",
                            "minimum": 0,
                            "maximum": 5
                        },
                        "is_claimed": {
                            "type": "boolean",
                            "description": "Filter to include only claimed (true) or unclaimed (false) businesses in analysis"
                        }
                    },
                    "required": ["input"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse des catégories de backlinks GMB"""
        try:
            # Validation des paramètres requis
            input_domain = kwargs.get("input", "").strip()
            
            if not input_domain:
                return {"error": "Le paramètre 'input' (domaine) est requis"}
            
            # Préparation des paramètres
            params = {
                "input": input_domain,
                "mode": kwargs.get("mode", "auto"),
                "lineCount": kwargs.get("lineCount", 100),
                "page": kwargs.get("page", 1)
            }
            
            # Paramètres d'analyse des catégories
            category_params = [
                "min_businesses_per_category", "category_filter", "include_subcategories"
            ]
            for param in category_params:
                if param in kwargs and kwargs[param] is not None:
                    params[param] = kwargs[param]
            
            # Filtres optionnels
            optional_filters = [
                "rating_count_min", "rating_value_min", "is_claimed"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            logger.info(f"📊 Analyse des catégories GMB pour {input_domain}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/gmbBacklinks/categories", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_gmb_categories_results(response, input_domain)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des catégories GMB: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des catégories GMB: {str(e)}"}
    
    def _analyze_gmb_categories_results(self, response: Dict[str, Any], input_domain: str) -> Dict[str, Any]:
        """Analyse et synthèse des résultats des catégories GMB"""
        try:
            results = response.get("results", [])
            total_count = response.get("total_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucune catégorie GMB trouvée pour {input_domain}",
                    "domain": input_domain,
                    "total_categories": 0,
                    "categories": []
                }
            
            # Analyse détaillée des catégories
            analyzed_categories = []
            all_businesses = []
            
            for category_data in results:
                category_name = category_data.get("category", "")
                business_count = category_data.get("business_count", 0)
                businesses = category_data.get("businesses", [])
                
                # Analyse des entreprises de cette catégorie
                category_businesses = []
                total_ratings = 0
                total_rating_count = 0
                claimed_count = 0
                
                for business in businesses:
                    business_info = {
                        "name": business.get("name", ""),
                        "rating_count": business.get("rating_count", 0),
                        "rating_value": business.get("rating_value", 0),
                        "is_claimed": bool(business.get("is_claimed", 0)),
                        "address": business.get("address", ""),
                        "phone": business.get("phone", "")
                    }
                    category_businesses.append(business_info)
                    all_businesses.append({**business_info, "category": category_name})
                    
                    if business_info["rating_value"] > 0:
                        total_ratings += business_info["rating_value"]
                        total_rating_count += 1
                    
                    if business_info["is_claimed"]:
                        claimed_count += 1
                
                # Calculs pour cette catégorie
                avg_rating = round(total_ratings / total_rating_count, 2) if total_rating_count > 0 else 0
                claimed_rate = round((claimed_count / business_count) * 100, 1) if business_count > 0 else 0
                
                category_analysis = {
                    "name": category_name,
                    "business_count": business_count,
                    "percentage_of_total": round((business_count / total_count) * 100, 1) if total_count > 0 else 0,
                    "average_rating": avg_rating,
                    "claimed_rate": claimed_rate,
                    "businesses": category_businesses,
                    "category_quality": self._assess_category_quality(category_businesses),
                    "industry_type": self._classify_industry_type(category_name),
                    "local_seo_value": self._calculate_category_seo_value(category_businesses, business_count),
                    "competitiveness": self._assess_category_competitiveness(category_name, business_count)
                }
                analyzed_categories.append(category_analysis)
            
            # Tri par nombre d'entreprises
            analyzed_categories.sort(key=lambda x: x["business_count"], reverse=True)
            
            # Analyse des industries
            industry_analysis = self._analyze_industries(analyzed_categories)
            
            # Analyse de la diversité
            diversity_analysis = self._analyze_category_diversity(analyzed_categories, total_count)
            
            # Top catégories par différents critères
            top_by_count = analyzed_categories[:10]
            top_by_quality = sorted(analyzed_categories, key=lambda x: x["category_quality"]["score"], reverse=True)[:5]
            top_by_seo_value = sorted(analyzed_categories, key=lambda x: x["local_seo_value"], reverse=True)[:5]
            
            # Catégories émergentes et niches
            niche_categories = [cat for cat in analyzed_categories if cat["business_count"] <= 3 and cat["average_rating"] >= 4.0]
            dominant_categories = [cat for cat in analyzed_categories if cat["percentage_of_total"] >= 10]
            
            # Opportunités d'amélioration
            improvement_opportunities = self._identify_improvement_opportunities(analyzed_categories)
            
            # Statistiques globales
            global_stats = {
                "total_categories": len(analyzed_categories),
                "total_businesses_analyzed": sum(cat["business_count"] for cat in analyzed_categories),
                "average_businesses_per_category": round(sum(cat["business_count"] for cat in analyzed_categories) / len(analyzed_categories), 1) if analyzed_categories else 0,
                "most_common_category": analyzed_categories[0]["name"] if analyzed_categories else None,
                "category_concentration": {
                    "top_3_percentage": sum(cat["percentage_of_total"] for cat in analyzed_categories[:3]),
                    "top_5_percentage": sum(cat["percentage_of_total"] for cat in analyzed_categories[:5]),
                    "diversity_index": self._calculate_diversity_index(analyzed_categories)
                },
                "quality_metrics": {
                    "average_rating_all": round(sum(b["rating_value"] for b in all_businesses if b["rating_value"] > 0) / 
                                              len([b for b in all_businesses if b["rating_value"] > 0]), 2) if all_businesses else 0,
                    "claimed_rate_all": round(sum(1 for b in all_businesses if b["is_claimed"]) / len(all_businesses) * 100, 1) if all_businesses else 0,
                    "categories_with_high_quality": len([cat for cat in analyzed_categories if cat["category_quality"]["level"] in ["excellent", "good"]])
                }
            }
            
            return {
                "summary": f"Analyse de {len(analyzed_categories)} catégorie(s) GMB pour {input_domain}",
                "domain": input_domain,
                "global_statistics": global_stats,
                "industry_analysis": industry_analysis,
                "diversity_analysis": diversity_analysis,
                "top_categories_by_count": top_by_count,
                "top_categories_by_quality": top_by_quality,
                "top_categories_by_seo_value": top_by_seo_value,
                "niche_categories": niche_categories,
                "dominant_categories": dominant_categories,
                "improvement_opportunities": improvement_opportunities,
                "all_categories": analyzed_categories,
                "recommendations": self._generate_category_recommendations(analyzed_categories, global_stats),
                "response_metadata": {
                    "response_time": response.get("response_time", ""),
                    "total_results": total_count
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des résultats: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des résultats: {str(e)}"}
    
    def _assess_category_quality(self, businesses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Évalue la qualité d'une catégorie basée sur ses entreprises"""
        if not businesses:
            return {"level": "poor", "score": 0, "factors": []}
        
        score = 0
        factors = []
        
        # Taux de revendication
        claimed_rate = sum(1 for b in businesses if b["is_claimed"]) / len(businesses) * 100
        if claimed_rate >= 80:
            score += 25
            factors.append("Excellent taux de revendication")
        elif claimed_rate >= 60:
            score += 15
            factors.append("Bon taux de revendication")
        
        # Qualité des avis
        rated_businesses = [b for b in businesses if b["rating_value"] > 0]
        if rated_businesses:
            avg_rating = sum(b["rating_value"] for b in rated_businesses) / len(rated_businesses)
            avg_count = sum(b["rating_count"] for b in rated_businesses) / len(rated_businesses)
            
            if avg_rating >= 4.5:
                score += 30
                factors.append("Excellentes notes moyennes")
            elif avg_rating >= 4.0:
                score += 20
                factors.append("Bonnes notes moyennes")
            
            if avg_count >= 20:
                score += 20
                factors.append("Bon volume d'avis")
            elif avg_count >= 10:
                score += 10
                factors.append("Volume d'avis correct")
        
        # Complétude des informations
        complete_info = sum(1 for b in businesses if b["phone"] and b["address"]) / len(businesses) * 100
        if complete_info >= 80:
            score += 15
            factors.append("Informations complètes")
        elif complete_info >= 60:
            score += 10
            factors.append("Informations partielles")
        
        # Taille de la catégorie
        if len(businesses) >= 10:
            score += 10
            factors.append("Catégorie bien représentée")
        elif len(businesses) >= 5:
            score += 5
            factors.append("Catégorie moyennement représentée")
        
        # Classification
        if score >= 80:
            level = "excellent"
        elif score >= 60:
            level = "good"
        elif score >= 40:
            level = "average"
        else:
            level = "poor"
        
        return {
            "level": level,
            "score": score,
            "factors": factors,
            "claimed_rate": round(claimed_rate, 1),
            "average_rating": round(sum(b["rating_value"] for b in rated_businesses) / len(rated_businesses), 2) if rated_businesses else 0
        }
    
    def _classify_industry_type(self, category_name: str) -> str:
        """Classifie le type d'industrie d'une catégorie"""
        category_lower = category_name.lower()
        
        industry_mapping = {
            "retail": ["store", "shop", "retail", "boutique", "market", "mall"],
            "food_beverage": ["restaurant", "cafe", "bar", "food", "bakery", "pizza", "coffee"],
            "health_wellness": ["doctor", "clinic", "hospital", "pharmacy", "dentist", "medical", "health", "spa"],
            "automotive": ["car", "auto", "garage", "mechanic", "tire", "vehicle"],
            "beauty_personal": ["salon", "beauty", "barber", "spa", "nail", "cosmetic"],
            "professional_services": ["lawyer", "accountant", "consultant", "agency", "office", "service"],
            "home_garden": ["contractor", "plumber", "electrician", "landscaping", "home", "repair"],
            "entertainment": ["theater", "cinema", "club", "entertainment", "game", "recreation"],
            "education": ["school", "university", "education", "training", "course"],
            "travel_hospitality": ["hotel", "motel", "travel", "tourism", "accommodation"],
            "technology": ["computer", "tech", "software", "IT", "digital"],
            "finance": ["bank", "insurance", "financial", "credit", "loan"],
            "real_estate": ["real estate", "property", "realtor", "housing"],
            "sports_fitness": ["gym", "fitness", "sport", "athletic", "yoga"]
        }
        
        for industry, keywords in industry_mapping.items():
            if any(keyword in category_lower for keyword in keywords):
                return industry
        
        return "other"
    
    def _calculate_category_seo_value(self, businesses: List[Dict[str, Any]], business_count: int) -> float:
        """Calcule la valeur SEO local d'une catégorie"""
        if not businesses:
            return 0
        
        score = 0
        
        # Volume (nombre d'entreprises)
        score += min(business_count * 2, 30)  # Max 30 points
        
        # Qualité moyenne des avis
        rated_businesses = [b for b in businesses if b["rating_value"] > 0]
        if rated_businesses:
            avg_rating = sum(b["rating_value"] for b in rated_businesses) / len(rated_businesses)
            avg_count = sum(b["rating_count"] for b in rated_businesses) / len(rated_businesses)
            
            score += avg_rating * 10  # Max 50 points
            score += min(avg_count, 20)  # Max 20 points
        
        return round(score, 2)
    
    def _assess_category_competitiveness(self, category_name: str, business_count: int) -> str:
        """Évalue la compétitivité d'une catégorie"""
        # Catégories généralement très compétitives
        high_competition = [
            "restaurant", "cafe", "bar", "hotel", "salon", "dentist", "lawyer",
            "real estate", "insurance", "car dealer", "gym", "spa"
        ]
        
        # Catégories de niche
        niche_categories = [
            "specialty", "custom", "artisan", "boutique", "vintage", "organic",
            "handmade", "luxury", "premium", "exclusive"
        ]
        
        category_lower = category_name.lower()
        
        # Vérification des mots-clés de niche
        is_niche = any(keyword in category_lower for keyword in niche_categories)
        
        # Vérification des catégories très compétitives
        is_high_competition = any(keyword in category_lower for keyword in high_competition)
        
        if is_niche:
            return "niche"
        elif is_high_competition and business_count > 20:
            return "very_high"
        elif business_count > 50:
            return "high"
        elif business_count > 20:
            return "medium"
        elif business_count > 5:
            return "low"
        else:
            return "very_low"
    
    def _analyze_industries(self, categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse la distribution par industrie"""
        industry_distribution = {}
        
        for category in categories:
            industry = category["industry_type"]
            if industry not in industry_distribution:
                industry_distribution[industry] = {
                    "category_count": 0,
                    "business_count": 0,
                    "categories": []
                }
            
            industry_distribution[industry]["category_count"] += 1
            industry_distribution[industry]["business_count"] += category["business_count"]
            industry_distribution[industry]["categories"].append(category["name"])
        
        # Tri par nombre d'entreprises
        sorted_industries = dict(sorted(industry_distribution.items(), 
                                     key=lambda x: x[1]["business_count"], reverse=True))
        
        return {
            "total_industries": len(industry_distribution),
            "distribution": sorted_industries,
            "dominant_industry": max(industry_distribution.items(), key=lambda x: x[1]["business_count"])[0] if industry_distribution else None
        }
    
    def _analyze_category_diversity(self, categories: List[Dict[str, Any]], total_count: int) -> Dict[str, Any]:
        """Analyse la diversité des catégories"""
        if not categories:
            return {"diversity_level": "none"}
        
        # Calcul de l'indice de concentration
        top_3_percentage = sum(cat["percentage_of_total"] for cat in categories[:3])
        top_5_percentage = sum(cat["percentage_of_total"] for cat in categories[:5])
        
        # Classification de la diversité
        if top_3_percentage > 70:
            diversity_level = "low"
        elif top_3_percentage > 50:
            diversity_level = "medium"
        elif top_5_percentage < 50:
            diversity_level = "high"
        else:
            diversity_level = "medium"
        
        return {
            "diversity_level": diversity_level,
            "concentration_metrics": {
                "top_3_percentage": round(top_3_percentage, 1),
                "top_5_percentage": round(top_5_percentage, 1),
                "herfindahl_index": self._calculate_herfindahl_index(categories)
            },
            "long_tail_categories": len([cat for cat in categories if cat["percentage_of_total"] < 2])
        }
    
    def _calculate_diversity_index(self, categories: List[Dict[str, Any]]) -> float:
        """Calcule un indice de diversité Simpson"""
        if not categories:
            return 0
        
        total = sum(cat["business_count"] for cat in categories)
        if total == 0:
            return 0
        
        simpson_index = sum((cat["business_count"] / total) ** 2 for cat in categories)
        diversity_index = 1 - simpson_index
        
        return round(diversity_index, 3)
    
    def _calculate_herfindahl_index(self, categories: List[Dict[str, Any]]) -> float:
        """Calcule l'indice de Herfindahl-Hirschman pour la concentration"""
        if not categories:
            return 0
        
        hhi = sum(cat["percentage_of_total"] ** 2 for cat in categories)
        return round(hhi, 1)
    
    def _identify_improvement_opportunities(self, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifie les opportunités d'amélioration par catégorie"""
        opportunities = []
        
        for category in categories:
            category_opportunities = []
            
            # Taux de revendication faible
            if category["category_quality"]["claimed_rate"] < 60:
                category_opportunities.append("Améliorer le taux de revendication des entreprises")
            
            # Notes moyennes faibles
            if category["category_quality"]["average_rating"] < 4.0 and category["category_quality"]["average_rating"] > 0:
                category_opportunities.append("Travailler sur la satisfaction client")
            
            # Peu d'avis
            avg_review_count = sum(b["rating_count"] for b in category["businesses"]) / len(category["businesses"]) if category["businesses"] else 0
            if avg_review_count < 10:
                category_opportunities.append("Encourager plus d'avis clients")
            
            # Informations incomplètes
            complete_info_rate = sum(1 for b in category["businesses"] if b["phone"] and b["address"]) / len(category["businesses"]) * 100 if category["businesses"] else 0
            if complete_info_rate < 80:
                category_opportunities.append("Compléter les informations des entreprises")
            
            if category_opportunities:
                opportunities.append({
                    "category": category["name"],
                    "business_count": category["business_count"],
                    "opportunities": category_opportunities,
                    "priority": "high" if category["percentage_of_total"] > 10 else "medium" if category["percentage_of_total"] > 5 else "low"
                })
        
        return sorted(opportunities, key=lambda x: x["business_count"], reverse=True)
    
    def _generate_category_recommendations(self, categories: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des catégories"""
        recommendations = []
        
        if not categories:
            return ["Aucune catégorie GMB trouvée pour ce domaine"]
        
        # Analyse de la diversité
        diversity_level = stats.get("category_concentration", {}).get("diversity_index", 0)
        if diversity_level > 0.8:
            recommendations.append("🌟 Excellente diversité de catégories, bon pour la visibilité locale")
        elif diversity_level < 0.3:
            recommendations.append("🎯 Concentration sur peu de catégories, opportunité de diversification")
        
        # Catégorie dominante
        most_common = stats.get("most_common_category")
        if most_common:
            recommendations.append(f"📊 Catégorie dominante: {most_common}")
        
        # Qualité globale
        high_quality_categories = stats.get("quality_metrics", {}).get("categories_with_high_quality", 0)
        total_categories = stats.get("total_categories", 1)
        quality_rate = (high_quality_categories / total_categories) * 100
        
        if quality_rate > 70:
            recommendations.append("⭐ Majorité des catégories de haute qualité")
        elif quality_rate < 30:
            recommendations.append("📈 Beaucoup de catégories à améliorer")
        
        # Taux de revendication global
        claimed_rate = stats.get("quality_metrics", {}).get("claimed_rate_all", 0)
        if claimed_rate < 60:
            recommendations.append(f"🏢 Taux de revendication faible ({claimed_rate}%), encouragez les propriétaires")
        elif claimed_rate > 90:
            recommendations.append("✅ Excellent taux de revendication des entreprises")
        
        # Catégories de niche
        niche_count = len([cat for cat in categories if cat["competitiveness"] == "niche"])
        if niche_count > 0:
            recommendations.append(f"💎 {niche_count} catégorie(s) de niche identifiée(s), opportunité unique")
        
        # Concentration du marché
        top_3_percentage = stats.get("category_concentration", {}).get("top_3_percentage", 0)
        if top_3_percentage > 80:
            recommendations.append("⚠️ Forte concentration sur 3 catégories, risque de dépendance")
        elif top_3_percentage < 40:
            recommendations.append("🌈 Bonne répartition entre catégories")
        
        # Opportunités par industrie
        if len(categories) > 10:
            recommendations.append("🔍 Analysez les opportunités par industrie spécifique")
        
        # Recommandation générale
        total_businesses = stats.get("total_businesses_analyzed", 0)
        if total_businesses > 100:
            recommendations.append("💪 Large écosystème d'entreprises, excellent pour le SEO local")
        
        return recommendations if recommendations else ["📊 Analyse des catégories GMB terminée"]
