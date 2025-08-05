"""
Outil MCP pour l'endpoint Haloscan keywords/serp/compare
Compare les SERPs d'un mot-clé entre deux dates et analyse l'évolution des positions
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool


class KeywordsSerpCompareTool(BaseMCPTool):
    """Outil pour comparer les SERPs d'un mot-clé entre deux dates"""
    
    def get_name(self) -> str:
        return "keywords_serp_compare"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "keywords_serp_compare",
                "description": "Compare les SERPs d'un mot-clé entre deux dates et analyse l'évolution des positions de chaque page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé à analyser"
                        },
                        "period": {
                            "type": "string",
                            "description": "Période de comparaison prédéfinie",
                            "enum": ["1 month", "3 months", "6 months", "12 months", "custom"],
                            "default": "6 months"
                        },
                        "first_date": {
                            "type": "string",
                            "description": "Date de début personnalisée (YYYY-MM-DD). Requis si period = custom"
                        },
                        "second_date": {
                            "type": "string",
                            "description": "Date de fin personnalisée (YYYY-MM-DD). Requis si period = custom"
                        }
                    },
                    "required": ["keyword"]
                }
            }
        }
    
    def get_description(self) -> str:
        return "Compare les SERPs d'un mot-clé entre deux dates et analyse l'évolution des positions de chaque page"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "keyword",
                "type": "string",
                "required": True,
                "description": "Le mot-clé à analyser"
            },
            {
                "name": "period",
                "type": "string",
                "required": False,
                "description": "Période de comparaison (1 month, 3 months, 6 months, 12 months, custom)",
                "default": "6 months"
            },
            {
                "name": "first_date",
                "type": "string",
                "required": False,
                "description": "Date de début personnalisée (YYYY-MM-DD) - requis si period = custom"
            },
            {
                "name": "second_date",
                "type": "string",
                "required": False,
                "description": "Date de fin personnalisée (YYYY-MM-DD) - requis si period = custom"
            }
        ]
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute la comparaison SERP pour un mot-clé"""
        
        # Validation des paramètres
        keyword = arguments.get("keyword")
        if not keyword:
            raise ValueError("Le paramètre 'keyword' est requis")
        
        period = arguments.get("period", "6 months")
        first_date = arguments.get("first_date")
        second_date = arguments.get("second_date")
        
        # Validation des dates personnalisées
        if period == "custom":
            if not first_date or not second_date:
                raise ValueError("Les paramètres 'first_date' et 'second_date' sont requis quand period = 'custom'")
            
            # Validation du format des dates
            import re
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, first_date) or not re.match(date_pattern, second_date):
                raise ValueError("Les dates doivent être au format YYYY-MM-DD")
        
        # Préparation des paramètres pour l'API
        params = {
            "keyword": keyword,
            "period": period
        }
        
        if period == "custom":
            params["first_date"] = first_date
            params["second_date"] = second_date
        
        # Appel à l'API Haloscan
        result = await self.client.request("keywords/serp/compare", params)
        
        # Analyse et résumé des résultats
        if "results" in result and result["results"]:
            analysis = self._analyze_serp_comparison(result)
            return {
                "keyword": result.get("keyword", keyword),
                "dates_compared": result.get("dates", []),
                "available_dates": result.get("available_search_dates", []),
                "response_time": result.get("response_time"),
                "analysis": analysis,
                "raw_data": result.get("results", {})
            }
        else:
            return {
                "keyword": keyword,
                "error": "Aucune donnée SERP disponible pour ce mot-clé",
                "raw_data": result
            }
    
    def _analyze_serp_comparison(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les résultats de comparaison SERP"""
        
        results = result.get("results", {})
        old_serp = results.get("old_serp", [])
        new_serp = results.get("new_serp", [])
        
        # Statistiques générales
        total_old = len(old_serp)
        total_new = len(new_serp)
        
        # Analyse des changements
        improvements = []  # Pages qui ont gagné des positions
        declines = []      # Pages qui ont perdu des positions
        new_entries = []   # Nouvelles pages
        lost_pages = []    # Pages qui ont disparu
        stable_pages = []  # Pages stables
        
        # Analyse de l'ancien SERP
        for page in old_serp:
            url = page.get("url", "")
            position = page.get("position", 0)
            diff = page.get("diff", "")
            
            if diff == "lost":
                lost_pages.append({
                    "url": url,
                    "old_position": position
                })
            elif diff.startswith("+") and diff != "+0":
                improvements.append({
                    "url": url,
                    "old_position": position,
                    "change": diff
                })
            elif diff.startswith("-") and diff != "-0":
                declines.append({
                    "url": url,
                    "old_position": position,
                    "change": diff
                })
            elif diff == "=":
                stable_pages.append({
                    "url": url,
                    "position": position
                })
        
        # Analyse du nouveau SERP pour les nouvelles entrées
        for page in new_serp:
            url = page.get("url", "")
            position = page.get("position", 0)
            diff = page.get("diff", "")
            
            if diff == "new":
                new_entries.append({
                    "url": url,
                    "new_position": position
                })
        
        # Calcul des métriques
        total_changes = len(improvements) + len(declines) + len(new_entries) + len(lost_pages)
        volatility_score = (total_changes / max(total_old, total_new)) * 100 if max(total_old, total_new) > 0 else 0
        
        return {
            "summary": {
                "total_old_results": total_old,
                "total_new_results": total_new,
                "total_changes": total_changes,
                "volatility_score": round(volatility_score, 2),
                "stability_rate": round(100 - volatility_score, 2)
            },
            "changes": {
                "improvements": len(improvements),
                "declines": len(declines),
                "new_entries": len(new_entries),
                "lost_pages": len(lost_pages),
                "stable_pages": len(stable_pages)
            },
            "top_improvements": improvements[:5],  # Top 5 améliorations
            "top_declines": declines[:5],          # Top 5 déclins
            "new_entries": new_entries[:5],        # Top 5 nouvelles entrées
            "lost_pages": lost_pages[:5]           # Top 5 pages perdues
        }
