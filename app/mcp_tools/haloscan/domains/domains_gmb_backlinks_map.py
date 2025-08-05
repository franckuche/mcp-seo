"""
MCP Tool pour l'endpoint Haloscan domains/gmbBacklinks/map
Permet d'obtenir une visualisation cartographique des backlinks Google My Business d'un domaine
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_gmb_backlinks_map_tool")

class DomainsGmbBacklinksMapTool(BaseMCPTool):
    """Outil MCP pour la visualisation cartographique des backlinks Google My Business via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainsgmbbacklinksmap"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour la carte des backlinks GMB"""
        return {
            "type": "function",
            "function": {
                "name": "domains_gmb_backlinks_map",
                "description": "Generate a map visualization of Google My Business backlinks for a domain, showing geographic distribution of local businesses linking to the domain.",
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
                            "description": "Maximum number of results to return for the map",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 200
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number for pagination",
                            "default": 1,
                            "minimum": 1
                        },
                        "map_zoom": {
                            "type": "integer",
                            "description": "Zoom level for the map visualization",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "map_center_lat": {
                            "type": "number",
                            "description": "Latitude for map center (auto-calculated if not provided)"
                        },
                        "map_center_lng": {
                            "type": "number",
                            "description": "Longitude for map center (auto-calculated if not provided)"
                        },
                        "rating_count_min": {
                            "type": "integer",
                            "description": "Minimum rating count filter for businesses to show on map",
                            "minimum": 0
                        },
                        "rating_value_min": {
                            "type": "number",
                            "description": "Minimum rating value filter (0-5) for businesses to show on map",
                            "minimum": 0,
                            "maximum": 5
                        },
                        "is_claimed": {
                            "type": "boolean",
                            "description": "Filter to show only claimed (true) or unclaimed (false) businesses on map"
                        },
                        "categories_include": {
                            "type": "string",
                            "description": "Regular expression for categories to be included on the map"
                        }
                    },
                    "required": ["input"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute la génération de la carte des backlinks GMB"""
        try:
            # Validation des paramètres requis
            input_domain = kwargs.get("input", "").strip()
            
            if not input_domain:
                return {"error": "Le paramètre 'input' (domaine) est requis"}
            
            # Préparation des paramètres
            params = {
                "input": input_domain,
                "mode": kwargs.get("mode", "auto"),
                "lineCount": kwargs.get("lineCount", 50),
                "page": kwargs.get("page", 1)
            }
            
            # Paramètres de carte
            map_params = ["map_zoom", "map_center_lat", "map_center_lng"]
            for param in map_params:
                if param in kwargs and kwargs[param] is not None:
                    params[param] = kwargs[param]
            
            # Filtres optionnels
            optional_filters = [
                "rating_count_min", "rating_value_min", "is_claimed", "categories_include"
            ]
            
            for filter_param in optional_filters:
                if filter_param in kwargs and kwargs[filter_param] is not None:
                    params[filter_param] = kwargs[filter_param]
            
            logger.info(f"🗺️ Génération de la carte GMB pour {input_domain}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/gmbBacklinks/map", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_gmb_map_results(response, input_domain)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération de la carte GMB: {str(e)}")
            return {"error": f"Erreur lors de la génération de la carte GMB: {str(e)}"}
    
    def _analyze_gmb_map_results(self, response: Dict[str, Any], input_domain: str) -> Dict[str, Any]:
        """Analyse et synthèse des résultats de la carte GMB"""
        try:
            results = response.get("results", [])
            map_data = response.get("map_data", {})
            total_count = response.get("total_result_count", 0)
            
            if not results:
                return {
                    "summary": f"Aucune donnée de carte GMB trouvée pour {input_domain}",
                    "domain": input_domain,
                    "map_available": False,
                    "businesses_on_map": 0
                }
            
            # Analyse des points sur la carte
            map_points = []
            geographic_clusters = {}
            
            for business in results:
                lat = business.get("latitude")
                lng = business.get("longitude")
                
                if lat is not None and lng is not None:
                    point = {
                        "cid": business.get("cid", ""),
                        "name": business.get("name", ""),
                        "address": business.get("address", ""),
                        "coordinates": {"lat": lat, "lng": lng},
                        "rating": {
                            "count": business.get("rating_count", 0),
                            "value": business.get("rating_value", 0)
                        },
                        "categories": business.get("categories", ""),
                        "is_claimed": bool(business.get("is_claimed", 0)),
                        "marker_priority": self._calculate_marker_priority(business),
                        "cluster_id": self._assign_cluster(lat, lng, geographic_clusters)
                    }
                    map_points.append(point)
            
            # Analyse des clusters géographiques
            cluster_analysis = self._analyze_geographic_clusters(map_points)
            
            # Calcul du centre de carte optimal
            optimal_center = self._calculate_optimal_map_center(map_points)
            
            # Calcul du zoom optimal
            optimal_zoom = self._calculate_optimal_zoom(map_points)
            
            # Analyse de la densité
            density_analysis = self._analyze_point_density(map_points)
            
            # Points remarquables
            high_priority_points = [p for p in map_points if p["marker_priority"] >= 80]
            claimed_businesses = [p for p in map_points if p["is_claimed"]]
            highly_rated = [p for p in map_points if p["rating"]["value"] >= 4.5 and p["rating"]["count"] >= 10]
            
            # Configuration de carte recommandée
            map_config = {
                "center": optimal_center,
                "zoom": optimal_zoom,
                "total_markers": len(map_points),
                "marker_clustering": len(cluster_analysis["clusters"]) > 1,
                "heat_map_overlay": len(map_points) > 20,
                "custom_markers": {
                    "high_priority": len(high_priority_points),
                    "claimed": len(claimed_businesses),
                    "highly_rated": len(highly_rated)
                }
            }
            
            # Statistiques de la carte
            map_stats = {
                "businesses_with_location": len(map_points),
                "businesses_without_location": total_count - len(map_points),
                "location_coverage": round((len(map_points) / total_count * 100), 1) if total_count > 0 else 0,
                "geographic_spread": self._calculate_geographic_spread(map_points),
                "density_level": density_analysis["density_level"],
                "cluster_count": len(cluster_analysis["clusters"])
            }
            
            return {
                "summary": f"Carte GMB générée avec {len(map_points)} point(s) géolocalisé(s) pour {input_domain}",
                "domain": input_domain,
                "map_available": len(map_points) > 0,
                "map_configuration": map_config,
                "map_statistics": map_stats,
                "geographic_clusters": cluster_analysis,
                "density_analysis": density_analysis,
                "map_points": map_points,
                "high_priority_businesses": high_priority_points,
                "claimed_businesses": claimed_businesses,
                "highly_rated_businesses": highly_rated,
                "visualization_recommendations": self._generate_map_recommendations(map_points, map_stats),
                "response_metadata": {
                    "response_time": response.get("response_time", ""),
                    "total_businesses": total_count,
                    "map_data_available": bool(map_data)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des résultats de carte: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des résultats de carte: {str(e)}"}
    
    def _calculate_marker_priority(self, business: Dict[str, Any]) -> int:
        """Calcule la priorité d'affichage d'un marqueur sur la carte"""
        score = 0
        
        # Statut revendiqué
        if business.get("is_claimed", 0):
            score += 30
        
        # Qualité des avis
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
        
        # Informations complètes
        if business.get("phone"):
            score += 5
        if business.get("address"):
            score += 5
        
        return min(score, 100)
    
    def _assign_cluster(self, lat: float, lng: float, clusters: Dict[str, Any]) -> str:
        """Assigne un point à un cluster géographique"""
        cluster_radius = 0.01  # Environ 1km
        
        for cluster_id, cluster_data in clusters.items():
            center_lat = cluster_data["center_lat"]
            center_lng = cluster_data["center_lng"]
            
            distance = ((lat - center_lat) ** 2 + (lng - center_lng) ** 2) ** 0.5
            if distance <= cluster_radius:
                # Mettre à jour le centre du cluster
                cluster_data["points"] += 1
                cluster_data["center_lat"] = (cluster_data["center_lat"] * (cluster_data["points"] - 1) + lat) / cluster_data["points"]
                cluster_data["center_lng"] = (cluster_data["center_lng"] * (cluster_data["points"] - 1) + lng) / cluster_data["points"]
                return cluster_id
        
        # Créer un nouveau cluster
        cluster_id = f"cluster_{len(clusters) + 1}"
        clusters[cluster_id] = {
            "center_lat": lat,
            "center_lng": lng,
            "points": 1
        }
        return cluster_id
    
    def _analyze_geographic_clusters(self, map_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les clusters géographiques des points"""
        clusters = {}
        
        for point in map_points:
            cluster_id = point.get("cluster_id", "unknown")
            if cluster_id not in clusters:
                clusters[cluster_id] = {
                    "id": cluster_id,
                    "business_count": 0,
                    "businesses": [],
                    "average_rating": 0,
                    "claimed_count": 0
                }
            
            cluster = clusters[cluster_id]
            cluster["business_count"] += 1
            cluster["businesses"].append(point["name"])
            
            if point["rating"]["value"] > 0:
                cluster["average_rating"] = (cluster["average_rating"] * (cluster["business_count"] - 1) + point["rating"]["value"]) / cluster["business_count"]
            
            if point["is_claimed"]:
                cluster["claimed_count"] += 1
        
        # Finaliser les clusters
        for cluster in clusters.values():
            cluster["average_rating"] = round(cluster["average_rating"], 2)
            cluster["claimed_rate"] = round((cluster["claimed_count"] / cluster["business_count"]) * 100, 1)
        
        return {
            "cluster_count": len(clusters),
            "clusters": list(clusters.values()),
            "largest_cluster": max(clusters.values(), key=lambda x: x["business_count"]) if clusters else None
        }
    
    def _calculate_optimal_map_center(self, map_points: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcule le centre optimal pour la carte"""
        if not map_points:
            return {"lat": 0, "lng": 0}
        
        total_lat = sum(point["coordinates"]["lat"] for point in map_points)
        total_lng = sum(point["coordinates"]["lng"] for point in map_points)
        
        return {
            "lat": round(total_lat / len(map_points), 6),
            "lng": round(total_lng / len(map_points), 6)
        }
    
    def _calculate_optimal_zoom(self, map_points: List[Dict[str, Any]]) -> int:
        """Calcule le niveau de zoom optimal"""
        if len(map_points) <= 1:
            return 15
        
        # Calcul de la dispersion
        lats = [point["coordinates"]["lat"] for point in map_points]
        lngs = [point["coordinates"]["lng"] for point in map_points]
        
        lat_range = max(lats) - min(lats)
        lng_range = max(lngs) - min(lngs)
        max_range = max(lat_range, lng_range)
        
        # Mapping approximatif range -> zoom
        if max_range > 10:
            return 6
        elif max_range > 5:
            return 7
        elif max_range > 2:
            return 8
        elif max_range > 1:
            return 9
        elif max_range > 0.5:
            return 10
        elif max_range > 0.1:
            return 12
        elif max_range > 0.05:
            return 13
        else:
            return 14
    
    def _analyze_point_density(self, map_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse la densité des points sur la carte"""
        if len(map_points) <= 1:
            return {"density_level": "very_low", "points_per_km2": 0}
        
        # Calcul de la zone couverte (approximatif)
        lats = [point["coordinates"]["lat"] for point in map_points]
        lngs = [point["coordinates"]["lng"] for point in map_points]
        
        lat_range = max(lats) - min(lats)
        lng_range = max(lngs) - min(lngs)
        
        # Conversion approximative en km²
        area_km2 = lat_range * lng_range * 111 * 111  # 1 degré ≈ 111 km
        
        if area_km2 == 0:
            density = len(map_points)
        else:
            density = len(map_points) / area_km2
        
        # Classification de la densité
        if density > 100:
            density_level = "very_high"
        elif density > 50:
            density_level = "high"
        elif density > 10:
            density_level = "medium"
        elif density > 1:
            density_level = "low"
        else:
            density_level = "very_low"
        
        return {
            "density_level": density_level,
            "points_per_km2": round(density, 2),
            "coverage_area_km2": round(area_km2, 2)
        }
    
    def _calculate_geographic_spread(self, map_points: List[Dict[str, Any]]) -> str:
        """Calcule l'étendue géographique des points"""
        if len(map_points) <= 1:
            return "single_point"
        
        lats = [point["coordinates"]["lat"] for point in map_points]
        lngs = [point["coordinates"]["lng"] for point in map_points]
        
        lat_range = max(lats) - min(lats)
        lng_range = max(lngs) - min(lngs)
        max_range = max(lat_range, lng_range)
        
        if max_range > 5:
            return "very_wide"
        elif max_range > 1:
            return "wide"
        elif max_range > 0.1:
            return "medium"
        elif max_range > 0.01:
            return "narrow"
        else:
            return "very_narrow"
    
    def _generate_map_recommendations(self, map_points: List[Dict[str, Any]], map_stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations pour la visualisation de carte"""
        recommendations = []
        
        if not map_points:
            return ["Aucune donnée géographique disponible pour la carte"]
        
        # Couverture géographique
        location_coverage = map_stats.get("location_coverage", 0)
        if location_coverage < 70:
            recommendations.append(f"📍 Seulement {location_coverage}% des entreprises ont des coordonnées, complétez les données")
        elif location_coverage > 95:
            recommendations.append("🎯 Excellente couverture géographique des données")
        
        # Densité
        density_level = map_stats.get("density_level", "")
        if density_level == "very_high":
            recommendations.append("🗺️ Utilisez le clustering de marqueurs pour éviter la surcharge visuelle")
        elif density_level == "very_low":
            recommendations.append("📌 Densité faible, zoom plus important recommandé")
        
        # Clusters
        cluster_count = map_stats.get("cluster_count", 0)
        if cluster_count > 5:
            recommendations.append(f"🎯 {cluster_count} zones géographiques identifiées, analysez chaque cluster")
        elif cluster_count == 1:
            recommendations.append("📍 Concentration géographique forte, opportunité de domination locale")
        
        # Étendue géographique
        geographic_spread = map_stats.get("geographic_spread", "")
        if geographic_spread == "very_wide":
            recommendations.append("🌍 Couverture géographique très large, segmentez par région")
        elif geographic_spread == "very_narrow":
            recommendations.append("🎯 Zone géographique concentrée, excellent pour le SEO local")
        
        # Qualité des marqueurs
        high_priority_count = len([p for p in map_points if p["marker_priority"] >= 80])
        if high_priority_count > 0:
            recommendations.append(f"⭐ {high_priority_count} entreprise(s) prioritaire(s) à mettre en avant sur la carte")
        
        # Recommandations techniques
        if len(map_points) > 50:
            recommendations.append("⚡ Activez la carte de chaleur pour une meilleure visualisation")
        
        if len(map_points) > 20:
            recommendations.append("🔧 Implémentez des filtres interactifs (note, statut, catégorie)")
        
        return recommendations if recommendations else ["🗺️ Carte GMB générée avec succès"]
