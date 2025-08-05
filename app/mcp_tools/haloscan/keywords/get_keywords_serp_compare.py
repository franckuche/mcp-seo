"""
MCP Tool pour l'endpoint Haloscan keywords/serp/compare
Comparaison des SERPs d'un mot-clé à deux dates différentes
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool


class GetKeywordsSerpCompareTool(BaseMCPTool):
    """Outil MCP pour comparer les SERPs d'un mot-clé entre deux dates"""
    
    def get_name(self) -> str:
        return "get_keywords_serp_compare"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_keywords_serp_compare",
                "description": "Compare les positions SERP d'un domaine entre deux périodes pour analyser l'évolution",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Nom de domaine à analyser (ex: lemonde.fr)"
                        },
                        "lang": {
                            "type": "string",
                            "description": "Langue d'analyse (fr, en, es, de, it, pt, nl)",
                            "default": "fr"
                        },
                        "period": {
                            "type": "string",
                            "description": "Période prédéfinie de comparaison",
                            "enum": ["7d", "30d", "90d", "1y"]
                        },
                        "date_from": {
                            "type": "string",
                            "description": "Date de début personnalisée (YYYY-MM-DD)"
                        },
                        "date_to": {
                            "type": "string",
                            "description": "Date de fin personnalisée (YYYY-MM-DD)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Nombre maximum de résultats (défaut: 100)",
                            "default": 100
                        }
                    },
                    "required": ["domain"]
                }
            }
        }
    
    def get_description(self) -> str:
        return "Compare les SERPs d'un mot-clé entre deux dates et analyse l'évolution des positions"
    
    def get_openai_function_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Mot-clé à analyser pour la comparaison SERP"
                        },
                        "period": {
                            "type": "string",
                            "enum": ["1 month", "3 months", "6 months", "12 months", "custom"],
                            "description": "Période de comparaison des SERPs. Si 'custom', first_date et second_date doivent être fournis",
                            "default": "6 months"
                        },
                        "first_date": {
                            "type": "string",
                            "description": "Date de début au format YYYY-MM-DD (uniquement si period = custom)",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "second_date": {
                            "type": "string",
                            "description": "Date de fin au format YYYY-MM-DD (uniquement si period = custom)",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["keyword"]
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute la comparaison des SERPs"""
        
        # Construire les paramètres de la requête
        params = {
            "keyword": arguments["keyword"],
            "period": arguments.get("period", "6 months")
        }
        
        # Validation pour période custom
        if params["period"] == "custom":
            if "first_date" not in arguments or "second_date" not in arguments:
                return {
                    "tool": self.get_name(),
                    "success": False,
                    "error": "Les paramètres first_date et second_date sont obligatoires quand period = 'custom'"
                }
            
            params["first_date"] = arguments["first_date"]
            params["second_date"] = arguments["second_date"]
            
            # Validation basique du format de date
            import re
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, params["first_date"]) or not re.match(date_pattern, params["second_date"]):
                return {
                    "tool": self.get_name(),
                    "success": False,
                    "error": "Les dates doivent être au format YYYY-MM-DD"
                }
        
        # Appeler l'API Haloscan
        result = await self.client.request("keywords/serp/compare", params)
        
        # Analyser les résultats pour fournir un résumé
        summary = {
            "keyword": params["keyword"],
            "period": params["period"],
            "comparison_type": "custom" if params["period"] == "custom" else "predefined"
        }
        
        if isinstance(result, dict):
            # Analyser les dates de comparaison
            if "dates" in result and isinstance(result["dates"], list) and len(result["dates"]) >= 2:
                summary["comparison_dates"] = {
                    "old_date": result["dates"][0],
                    "new_date": result["dates"][1],
                    "time_span": result["dates"][1] + " vs " + result["dates"][0]
                }
            
            # Analyser les dates disponibles
            if "available_search_dates" in result and isinstance(result["available_search_dates"], list):
                summary["available_dates"] = {
                    "total_dates": len(result["available_search_dates"]),
                    "date_range": {
                        "earliest": min(result["available_search_dates"]) if result["available_search_dates"] else "N/A",
                        "latest": max(result["available_search_dates"]) if result["available_search_dates"] else "N/A"
                    }
                }
            
            # Analyser les résultats SERP
            if "results" in result and isinstance(result["results"], dict):
                old_serp = result["results"].get("old_serp", [])
                new_serp = result["results"].get("new_serp", [])
                
                # Analyser les changements
                position_changes = {
                    "improved": 0,
                    "declined": 0,
                    "stable": 0,
                    "new": 0,
                    "lost": 0
                }
                
                for page in old_serp:
                    diff = page.get("diff", "")
                    if diff.startswith("+") and diff != "+":
                        position_changes["improved"] += 1
                    elif diff.startswith("-") and diff != "-":
                        position_changes["declined"] += 1
                    elif diff == "=":
                        position_changes["stable"] += 1
                    elif diff == "lost":
                        position_changes["lost"] += 1
                
                for page in new_serp:
                    if page.get("diff") == "new":
                        position_changes["new"] += 1
                
                summary["serp_analysis"] = {
                    "old_serp_results": len(old_serp),
                    "new_serp_results": len(new_serp),
                    "position_changes": position_changes,
                    "volatility_score": round(
                        (position_changes["improved"] + position_changes["declined"] + 
                         position_changes["new"] + position_changes["lost"]) / 
                        max(len(old_serp), 1) * 100, 2
                    )
                }
                
                # Top changements
                significant_changes = []
                for page in old_serp[:10]:  # Top 10 de l'ancien SERP
                    diff = page.get("diff", "")
                    if diff.startswith("+") or diff.startswith("-") or diff == "lost":
                        significant_changes.append({
                            "url": page.get("url", "")[:50] + "..." if len(page.get("url", "")) > 50 else page.get("url", ""),
                            "old_position": page.get("position"),
                            "change": diff
                        })
                
                summary["top_changes"] = significant_changes[:5]
            
            # Temps de réponse
            if "response_time" in result:
                summary["response_time"] = result["response_time"]
        
        return {
            "tool": self.get_name(),
            "success": True,
            "data": result,
            "summary": summary
        }
