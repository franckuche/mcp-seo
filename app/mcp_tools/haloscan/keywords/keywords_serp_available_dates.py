"""
Outil MCP pour l'endpoint Haloscan keywords/serp/availableDates
Retourne la liste des dates disponibles pour les SERPs d'un mot-clé
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool


class KeywordsSerpAvailableDatesTool(BaseMCPTool):
    """Outil pour récupérer les dates SERP disponibles pour un mot-clé"""
    
    def get_name(self) -> str:
        return "keywords_serp_available_dates"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "keywords_serp_available_dates",
                "description": "Retourne la liste des dates pour lesquelles les SERPs d'un mot-clé sont disponibles",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé pour lequel récupérer les dates SERP disponibles"
                        }
                    },
                    "required": ["keyword"]
                }
            }
        }
    
    def get_description(self) -> str:
        return "Récupère la liste des dates disponibles pour les SERPs d'un mot-clé (aucun crédit consommé)"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "keyword",
                "type": "string",
                "required": True,
                "description": "Le mot-clé pour lequel récupérer les dates SERP disponibles"
            }
        ]
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute la récupération des dates SERP disponibles"""
        
        # Validation des paramètres
        keyword = arguments.get("keyword")
        if not keyword:
            raise ValueError("Le paramètre 'keyword' est requis")
        
        # Préparation des paramètres pour l'API
        params = {
            "keyword": keyword
        }
        
        # Appel à l'API Haloscan
        result = await self.client.request("keywords/serp/availableDates", params)
        
        # Analyse et résumé des résultats
        if "available_search_dates" in result:
            analysis = self._analyze_available_dates(result)
            return {
                "keyword": result.get("keyword", keyword),
                "response_time": result.get("response_time"),
                "total_dates": len(result.get("available_search_dates", [])),
                "date_range": analysis.get("date_range"),
                "recent_dates": analysis.get("recent_dates"),
                "analysis": analysis,
                "available_dates": result.get("available_search_dates", [])
            }
        else:
            return {
                "keyword": keyword,
                "error": "Aucune date SERP disponible pour ce mot-clé",
                "raw_data": result
            }
    
    def _analyze_available_dates(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les dates disponibles"""
        
        available_dates = result.get("available_search_dates", [])
        
        if not available_dates:
            return {
                "total_dates": 0,
                "date_range": None,
                "recent_dates": [],
                "monthly_distribution": {},
                "yearly_distribution": {}
            }
        
        # Tri des dates
        sorted_dates = sorted(available_dates)
        
        # Plage de dates
        first_date = sorted_dates[0] if sorted_dates else None
        last_date = sorted_dates[-1] if sorted_dates else None
        
        # Dates récentes (dernières 10)
        recent_dates = sorted_dates[-10:] if len(sorted_dates) >= 10 else sorted_dates
        
        # Distribution mensuelle
        monthly_distribution = {}
        yearly_distribution = {}
        
        for date in available_dates:
            try:
                year = date[:4]
                month = date[:7]  # YYYY-MM
                
                # Distribution annuelle
                yearly_distribution[year] = yearly_distribution.get(year, 0) + 1
                
                # Distribution mensuelle
                monthly_distribution[month] = monthly_distribution.get(month, 0) + 1
                
            except (IndexError, ValueError):
                continue  # Ignorer les dates mal formatées
        
        # Statistiques de fréquence
        total_dates = len(available_dates)
        
        # Calcul de la période couverte en jours
        days_covered = 0
        if first_date and last_date:
            try:
                from datetime import datetime
                start = datetime.strptime(first_date, "%Y-%m-%d")
                end = datetime.strptime(last_date, "%Y-%m-%d")
                days_covered = (end - start).days
            except ValueError:
                days_covered = 0
        
        # Fréquence moyenne
        avg_frequency = round(days_covered / total_dates, 1) if total_dates > 0 and days_covered > 0 else 0
        
        return {
            "total_dates": total_dates,
            "date_range": {
                "first_date": first_date,
                "last_date": last_date,
                "days_covered": days_covered,
                "average_frequency_days": avg_frequency
            },
            "recent_dates": recent_dates,
            "distribution": {
                "by_year": dict(sorted(yearly_distribution.items())),
                "by_month": dict(sorted(monthly_distribution.items())[-12:])  # 12 derniers mois
            },
            "statistics": {
                "most_active_year": max(yearly_distribution.items(), key=lambda x: x[1])[0] if yearly_distribution else None,
                "most_active_month": max(monthly_distribution.items(), key=lambda x: x[1])[0] if monthly_distribution else None,
                "data_availability": "Excellent" if total_dates > 100 else "Bon" if total_dates > 50 else "Limité"
            }
        }
