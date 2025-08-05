"""
MCP Tool pour l'endpoint Haloscan domains/history/visibilityTrends
Permet d'analyser les tendances de visibilité d'un ou plusieurs domaines dans le temps
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_visibility_trends_tool")

class DomainsVisibilityTrendsTool(BaseMCPTool):
    """Outil MCP pour analyser les tendances de visibilité des domaines via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainsvisibilitytrends"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour l'analyse des tendances de visibilité"""
        return {
            "type": "function",
            "function": {
                "name": "domains_visibility_trends",
                "description": "Analyze visibility trends over time for one or multiple domains to track SEO performance evolution and identify patterns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of domains or URLs to analyze (e.g., ['example1.com', 'example2.com'])",
                            "minItems": 1,
                            "maxItems": 10
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["auto", "root", "domain", "url"],
                            "description": "Whether to look for a domain or a full URL. Leave empty for auto detection",
                            "default": "auto"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["trends", "first", "highest", "index"],
                            "description": "Determines how returned values are computed. 'trends' shows evolution over time",
                            "default": "trends"
                        }
                    },
                    "required": ["input"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse des tendances de visibilité des domaines"""
        try:
            # Validation des paramètres requis
            input_domains = kwargs.get("input", [])
            
            if not input_domains or not isinstance(input_domains, list):
                return {"error": "Le paramètre 'input' est requis et doit être une liste de domaines"}
            if len(input_domains) > 10:
                return {"error": "Maximum 10 domaines autorisés par requête"}
            
            # Préparation des paramètres
            params = {
                "input": input_domains,
                "mode": kwargs.get("mode", "auto"),
                "type": kwargs.get("type", "trends")
            }
            
            logger.info(f"🔍 Analyse des tendances de visibilité pour {len(input_domains)} domaine(s): {', '.join(input_domains[:3])}{'...' if len(input_domains) > 3 else ''}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/history/visibilityTrends", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_visibility_trends_results(response, input_domains)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des tendances de visibilité: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des tendances de visibilité: {str(e)}"}
    
    def _analyze_visibility_trends_results(self, response: Dict[str, Any], input_domains: List[str]) -> Dict[str, Any]:
        """Analyse et synthèse des résultats des tendances de visibilité"""
        try:
            results = response.get("results", [])
            
            if not results:
                return {
                    "summary": f"Aucune donnée de visibilité trouvée pour les domaines: {', '.join(input_domains)}",
                    "domains": input_domains,
                    "total_domains": len(input_domains),
                    "domains_with_data": 0,
                    "trends_analysis": []
                }
            
            # Analyse des domaines individuels
            domains_analysis = []
            for domain_result in results:
                domain_name = domain_result.get("name", "")
                data_points = domain_result.get("data", [])
                
                if not data_points:
                    continue
                
                # Analyse des métriques temporelles
                visibility_values = [point.get("visibility_index", 0) for point in data_points]
                dates = [point.get("agg_date", "") for point in data_points]
                
                # Calculs statistiques
                current_visibility = visibility_values[-1] if visibility_values else 0
                max_visibility = max(visibility_values) if visibility_values else 0
                min_visibility = min(visibility_values) if visibility_values else 0
                avg_visibility = sum(visibility_values) / len(visibility_values) if visibility_values else 0
                
                # Analyse de tendance
                trend_analysis = self._calculate_trend_analysis(visibility_values, dates)
                
                # Détection des événements significatifs
                significant_events = self._detect_significant_events(data_points)
                
                # Analyse de volatilité
                volatility_score = self._calculate_volatility(visibility_values)
                
                domain_analysis = {
                    "domain": domain_name,
                    "data_points_count": len(data_points),
                    "date_range": {
                        "start": dates[0] if dates else "",
                        "end": dates[-1] if dates else ""
                    },
                    "visibility_metrics": {
                        "current": current_visibility,
                        "maximum": max_visibility,
                        "minimum": min_visibility,
                        "average": round(avg_visibility, 2),
                        "range": max_visibility - min_visibility
                    },
                    "trend_analysis": trend_analysis,
                    "volatility": {
                        "score": volatility_score,
                        "level": self._classify_volatility(volatility_score)
                    },
                    "significant_events": significant_events,
                    "performance_category": self._categorize_performance(current_visibility, avg_visibility, trend_analysis),
                    "raw_data": data_points
                }
                domains_analysis.append(domain_analysis)
            
            # Analyse comparative (si plusieurs domaines)
            comparative_analysis = {}
            if len(domains_analysis) > 1:
                comparative_analysis = self._perform_comparative_analysis(domains_analysis)
            
            # Statistiques globales
            stats = {
                "total_domains_requested": len(input_domains),
                "domains_with_data": len(domains_analysis),
                "missing_domains": [domain for domain in input_domains if domain not in [d["domain"] for d in domains_analysis]],
                "overall_metrics": self._calculate_overall_metrics(domains_analysis),
                "time_period": self._determine_time_period(domains_analysis)
            }
            
            return {
                "summary": f"Analyse des tendances de visibilité pour {len(domains_analysis)} domaine(s) sur {len(input_domains)} demandé(s)",
                "domains": input_domains,
                "statistics": stats,
                "domains_analysis": domains_analysis,
                "comparative_analysis": comparative_analysis,
                "recommendations": self._generate_visibility_recommendations(domains_analysis, stats),
                "response_metadata": {
                    "response_time": response.get("response_time", ""),
                    "response_code": response.get("response_code"),
                    "failure_reason": response.get("failure_reason")
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des résultats: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des résultats: {str(e)}"}
    
    def _calculate_trend_analysis(self, values: List[float], dates: List[str]) -> Dict[str, Any]:
        """Calcule l'analyse de tendance des valeurs de visibilité"""
        if len(values) < 2:
            return {"direction": "insufficient_data", "strength": 0, "change_percentage": 0}
        
        # Calcul de la tendance générale (régression linéaire simple)
        n = len(values)
        x_values = list(range(n))
        
        # Moyennes
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        # Calcul de la pente
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Changement en pourcentage
        start_value = values[0]
        end_value = values[-1]
        change_percentage = ((end_value - start_value) / start_value * 100) if start_value != 0 else 0
        
        # Direction et force de la tendance
        if slope > 0.5:
            direction = "strongly_increasing"
        elif slope > 0.1:
            direction = "increasing"
        elif slope > -0.1:
            direction = "stable"
        elif slope > -0.5:
            direction = "decreasing"
        else:
            direction = "strongly_decreasing"
        
        return {
            "direction": direction,
            "slope": round(slope, 4),
            "strength": abs(slope),
            "change_percentage": round(change_percentage, 2),
            "start_value": start_value,
            "end_value": end_value
        }
    
    def _detect_significant_events(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détecte les événements significatifs dans les données de visibilité"""
        if len(data_points) < 3:
            return []
        
        events = []
        values = [point.get("visibility_index", 0) for point in data_points]
        
        # Calcul de la moyenne mobile pour détecter les anomalies
        window_size = min(5, len(values) // 3)
        if window_size < 2:
            return []
        
        for i in range(window_size, len(values) - window_size):
            current_value = values[i]
            
            # Moyenne des valeurs précédentes et suivantes
            prev_avg = sum(values[i-window_size:i]) / window_size
            next_avg = sum(values[i+1:i+window_size+1]) / window_size
            context_avg = (prev_avg + next_avg) / 2
            
            # Détection d'anomalies (variation > 30%)
            if context_avg > 0:
                variation_percentage = abs((current_value - context_avg) / context_avg * 100)
                
                if variation_percentage > 30:
                    event_type = "spike" if current_value > context_avg else "drop"
                    events.append({
                        "date": data_points[i].get("agg_date", ""),
                        "type": event_type,
                        "visibility_value": current_value,
                        "expected_value": round(context_avg, 2),
                        "variation_percentage": round(variation_percentage, 2)
                    })
        
        return events
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calcule un score de volatilité basé sur l'écart-type"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # Score de volatilité normalisé (0-100)
        volatility_score = (std_dev / mean * 100) if mean > 0 else 0
        return round(volatility_score, 2)
    
    def _classify_volatility(self, volatility_score: float) -> str:
        """Classifie le niveau de volatilité"""
        if volatility_score < 10:
            return "low"
        elif volatility_score < 25:
            return "moderate"
        elif volatility_score < 50:
            return "high"
        else:
            return "very_high"
    
    def _categorize_performance(self, current: float, average: float, trend: Dict[str, Any]) -> str:
        """Catégorise la performance globale du domaine"""
        trend_direction = trend.get("direction", "stable")
        
        if current >= 80 and trend_direction in ["increasing", "strongly_increasing"]:
            return "excellent"
        elif current >= 60 and trend_direction != "strongly_decreasing":
            return "good"
        elif current >= 40 and trend_direction in ["stable", "increasing"]:
            return "average"
        elif trend_direction in ["decreasing", "strongly_decreasing"]:
            return "declining"
        else:
            return "poor"
    
    def _perform_comparative_analysis(self, domains_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Effectue une analyse comparative entre plusieurs domaines"""
        current_values = [d["visibility_metrics"]["current"] for d in domains_analysis]
        avg_values = [d["visibility_metrics"]["average"] for d in domains_analysis]
        
        # Classement par visibilité actuelle
        ranked_domains = sorted(domains_analysis, key=lambda x: x["visibility_metrics"]["current"], reverse=True)
        
        # Analyse des tendances
        trending_up = [d for d in domains_analysis if d["trend_analysis"]["direction"] in ["increasing", "strongly_increasing"]]
        trending_down = [d for d in domains_analysis if d["trend_analysis"]["direction"] in ["decreasing", "strongly_decreasing"]]
        
        return {
            "leader": ranked_domains[0]["domain"] if ranked_domains else None,
            "laggard": ranked_domains[-1]["domain"] if ranked_domains else None,
            "visibility_range": {
                "highest": max(current_values) if current_values else 0,
                "lowest": min(current_values) if current_values else 0,
                "average": round(sum(current_values) / len(current_values), 2) if current_values else 0
            },
            "trending_up_count": len(trending_up),
            "trending_down_count": len(trending_down),
            "most_volatile": max(domains_analysis, key=lambda x: x["volatility"]["score"])["domain"] if domains_analysis else None,
            "most_stable": min(domains_analysis, key=lambda x: x["volatility"]["score"])["domain"] if domains_analysis else None
        }
    
    def _calculate_overall_metrics(self, domains_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les métriques globales pour tous les domaines"""
        if not domains_analysis:
            return {}
        
        all_current = [d["visibility_metrics"]["current"] for d in domains_analysis]
        all_averages = [d["visibility_metrics"]["average"] for d in domains_analysis]
        all_volatility = [d["volatility"]["score"] for d in domains_analysis]
        
        return {
            "average_current_visibility": round(sum(all_current) / len(all_current), 2),
            "average_historical_visibility": round(sum(all_averages) / len(all_averages), 2),
            "average_volatility": round(sum(all_volatility) / len(all_volatility), 2),
            "total_data_points": sum(d["data_points_count"] for d in domains_analysis)
        }
    
    def _determine_time_period(self, domains_analysis: List[Dict[str, Any]]) -> Dict[str, str]:
        """Détermine la période temporelle couverte par l'analyse"""
        if not domains_analysis:
            return {"start": "", "end": ""}
        
        all_starts = [d["date_range"]["start"] for d in domains_analysis if d["date_range"]["start"]]
        all_ends = [d["date_range"]["end"] for d in domains_analysis if d["date_range"]["end"]]
        
        return {
            "earliest_start": min(all_starts) if all_starts else "",
            "latest_end": max(all_ends) if all_ends else ""
        }
    
    def _generate_visibility_recommendations(self, domains_analysis: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des tendances de visibilité"""
        recommendations = []
        
        if not domains_analysis:
            return ["Aucune donnée de visibilité disponible pour les domaines analysés"]
        
        # Analyse des performances individuelles
        excellent_domains = [d for d in domains_analysis if d["performance_category"] == "excellent"]
        declining_domains = [d for d in domains_analysis if d["performance_category"] == "declining"]
        
        if excellent_domains:
            recommendations.append(f"🏆 {len(excellent_domains)} domaine(s) excellent(s): {', '.join([d['domain'] for d in excellent_domains[:3]])}")
        
        if declining_domains:
            recommendations.append(f"⚠️ {len(declining_domains)} domaine(s) en déclin: action corrective nécessaire")
        
        # Analyse des tendances
        overall_avg = stats.get("overall_metrics", {}).get("average_current_visibility", 0)
        if overall_avg > 70:
            recommendations.append("🚀 Visibilité globale excellente, maintenez vos efforts SEO")
        elif overall_avg < 40:
            recommendations.append("📈 Visibilité globale faible, stratégie SEO à revoir")
        
        # Analyse de la volatilité
        high_volatility_domains = [d for d in domains_analysis if d["volatility"]["level"] in ["high", "very_high"]]
        if high_volatility_domains:
            recommendations.append(f"📊 {len(high_volatility_domains)} domaine(s) très volatil(s): stabilisez vos positions")
        
        # Événements significatifs
        domains_with_events = [d for d in domains_analysis if d["significant_events"]]
        if domains_with_events:
            recommendations.append(f"🔍 Événements détectés sur {len(domains_with_events)} domaine(s): analysez les causes")
        
        # Analyse comparative
        if len(domains_analysis) > 1:
            leader = max(domains_analysis, key=lambda x: x["visibility_metrics"]["current"])
            recommendations.append(f"🌟 Leader en visibilité: {leader['domain']} ({leader['visibility_metrics']['current']:.1f})")
        
        # Recommandations sur les tendances
        trending_up = [d for d in domains_analysis if d["trend_analysis"]["direction"] in ["increasing", "strongly_increasing"]]
        if trending_up:
            recommendations.append(f"📈 {len(trending_up)} domaine(s) en progression: capitalisez sur cette dynamique")
        
        return recommendations if recommendations else ["📊 Analyse des tendances terminée, consultez les données détaillées"]
