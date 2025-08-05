"""
Outil MCP pour l'endpoint Haloscan keywords/serp/pageEvolution
Retourne l'historique des positions d'une URL dans les SERPs d'un mot-clé entre deux dates
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool


class KeywordsSerpPageEvolutionTool(BaseMCPTool):
    """Outil pour analyser l'évolution des positions d'une page dans les SERPs d'un mot-clé"""
    
    def get_name(self) -> str:
        return "keywords_serp_page_evolution"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "keywords_serp_page_evolution",
                "description": "Retourne l'historique des positions d'une URL dans les SERPs d'un mot-clé entre deux dates, avec l'historique du volume de recherche",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé à analyser"
                        },
                        "url": {
                            "type": "string",
                            "description": "L'URL dont analyser l'évolution des positions"
                        },
                        "first_date": {
                            "type": "string",
                            "description": "Date de début (YYYY-MM-DD)"
                        },
                        "second_date": {
                            "type": "string",
                            "description": "Date de fin (YYYY-MM-DD)"
                        }
                    },
                    "required": ["keyword", "url", "first_date", "second_date"]
                }
            }
        }
    
    def get_description(self) -> str:
        return "Analyse l'évolution des positions d'une URL spécifique dans les SERPs d'un mot-clé avec historique du volume"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "keyword",
                "type": "string",
                "required": True,
                "description": "Le mot-clé à analyser"
            },
            {
                "name": "url",
                "type": "string",
                "required": True,
                "description": "L'URL dont analyser l'évolution des positions"
            },
            {
                "name": "first_date",
                "type": "string",
                "required": True,
                "description": "Date de début au format YYYY-MM-DD"
            },
            {
                "name": "second_date",
                "type": "string",
                "required": True,
                "description": "Date de fin au format YYYY-MM-DD"
            }
        ]
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute l'analyse d'évolution des positions"""
        
        # Validation des paramètres
        keyword = arguments.get("keyword")
        url = arguments.get("url")
        first_date = arguments.get("first_date")
        second_date = arguments.get("second_date")
        
        if not all([keyword, url, first_date, second_date]):
            raise ValueError("Tous les paramètres (keyword, url, first_date, second_date) sont requis")
        
        # Validation du format des dates
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, first_date) or not re.match(date_pattern, second_date):
            raise ValueError("Les dates doivent être au format YYYY-MM-DD")
        
        # Préparation des paramètres pour l'API
        params = {
            "keyword": keyword,
            "url": url,
            "first_date": first_date,
            "second_date": second_date
        }
        
        # Appel à l'API Haloscan
        result = await self.client.request("keywords/serp/pageEvolution", params)
        
        # Analyse et résumé des résultats
        if "results" in result and result["results"]:
            analysis = self._analyze_page_evolution(result)
            return {
                "keyword": result.get("keyword", keyword),
                "url": result.get("url", url),
                "dates_analyzed": result.get("dates", [first_date, second_date]),
                "response_time": result.get("response_time"),
                "analysis": analysis,
                "position_history": result.get("results", {}).get("position_history", []),
                "volume_history": result.get("results", {}).get("volume_history", [])
            }
        else:
            return {
                "keyword": keyword,
                "url": url,
                "error": "Aucune donnée d'évolution disponible pour cette URL/mot-clé",
                "raw_data": result
            }
    
    def _analyze_page_evolution(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse l'évolution des positions d'une page"""
        
        results = result.get("results", {})
        position_history = results.get("position_history", [])
        volume_history = results.get("volume_history", [])
        
        if not position_history:
            return {
                "summary": "Aucune donnée de position disponible",
                "trends": {},
                "performance": {}
            }
        
        # Analyse des positions
        positions = []
        dates = []
        valid_positions = []
        
        for entry in position_history:
            date = entry.get("search_date")
            position = entry.get("position")
            
            dates.append(date)
            positions.append(position)
            
            # Filtrer les positions valides (pas "NA")
            if position != "NA" and isinstance(position, (int, float)):
                valid_positions.append(int(position))
        
        # Statistiques de base
        if valid_positions:
            best_position = min(valid_positions)
            worst_position = max(valid_positions)
            avg_position = round(sum(valid_positions) / len(valid_positions), 1)
            
            # Calcul de la tendance
            if len(valid_positions) >= 2:
                first_pos = valid_positions[0]
                last_pos = valid_positions[-1]
                trend = "amélioration" if last_pos < first_pos else "dégradation" if last_pos > first_pos else "stable"
                trend_value = first_pos - last_pos  # Positif = amélioration
            else:
                trend = "insuffisant"
                trend_value = 0
        else:
            best_position = None
            worst_position = None
            avg_position = None
            trend = "aucune donnée"
            trend_value = 0
        
        # Analyse de la volatilité
        volatility_score = 0
        if len(valid_positions) >= 2:
            changes = []
            for i in range(1, len(valid_positions)):
                changes.append(abs(valid_positions[i] - valid_positions[i-1]))
            volatility_score = round(sum(changes) / len(changes), 1) if changes else 0
        
        # Analyse du volume
        volume_analysis = {}
        if volume_history:
            volumes = [v.get("volume", 0) for v in volume_history if isinstance(v.get("volume"), (int, float))]
            if volumes:
                volume_analysis = {
                    "min_volume": min(volumes),
                    "max_volume": max(volumes),
                    "avg_volume": round(sum(volumes) / len(volumes)),
                    "volume_trend": "croissant" if len(volumes) >= 2 and volumes[-1] > volumes[0] else "décroissant" if len(volumes) >= 2 and volumes[-1] < volumes[0] else "stable"
                }
        
        # Périodes de visibilité
        visible_days = len([p for p in positions if p != "NA" and isinstance(p, (int, float))])
        total_days = len(positions)
        visibility_rate = round((visible_days / total_days) * 100, 1) if total_days > 0 else 0
        
        return {
            "summary": {
                "total_data_points": len(position_history),
                "visible_days": visible_days,
                "visibility_rate": f"{visibility_rate}%",
                "date_range": f"{dates[0]} à {dates[-1]}" if dates else "N/A"
            },
            "position_stats": {
                "best_position": best_position,
                "worst_position": worst_position,
                "average_position": avg_position,
                "volatility_score": volatility_score
            },
            "trends": {
                "overall_trend": trend,
                "trend_value": trend_value,
                "trend_description": f"Position {'améliorée' if trend_value > 0 else 'dégradée' if trend_value < 0 else 'stable'} de {abs(trend_value)} places" if trend_value != 0 else "Position stable"
            },
            "volume_analysis": volume_analysis,
            "performance_rating": self._get_performance_rating(best_position, avg_position, visibility_rate, trend_value)
        }
    
    def _get_performance_rating(self, best_pos: Optional[int], avg_pos: Optional[float], visibility: float, trend: float) -> str:
        """Évalue la performance globale de la page"""
        
        if not best_pos or not avg_pos:
            return "Données insuffisantes"
        
        score = 0
        
        # Score basé sur la meilleure position
        if best_pos <= 3:
            score += 40
        elif best_pos <= 10:
            score += 30
        elif best_pos <= 20:
            score += 20
        else:
            score += 10
        
        # Score basé sur la position moyenne
        if avg_pos <= 5:
            score += 30
        elif avg_pos <= 15:
            score += 20
        elif avg_pos <= 30:
            score += 10
        
        # Score basé sur la visibilité
        if visibility >= 90:
            score += 20
        elif visibility >= 70:
            score += 15
        elif visibility >= 50:
            score += 10
        
        # Bonus/malus tendance
        if trend > 5:
            score += 10
        elif trend < -5:
            score -= 10
        
        # Évaluation finale
        if score >= 80:
            return "Excellente"
        elif score >= 60:
            return "Bonne"
        elif score >= 40:
            return "Moyenne"
        else:
            return "Faible"
