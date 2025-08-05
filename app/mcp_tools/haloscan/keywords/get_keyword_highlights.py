"""
Outil MCP pour keywords/highlights - Points forts des mots-clés avec similarité
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class GetKeywordHighlightsTool(BaseMCPTool):
    """Outil MCP pour keywords/highlights - Points forts des mots-clés avec similarité"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_keyword_highlights",
                "description": "Trouve les points forts et mots-clés les plus pertinents avec score de similarité",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé de base pour l'analyse"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Champ de tri : default, keyword, similarity, volume, cpc, competition, kgr, allintitle",
                            "default": "similarity"
                        },
                        "order": {
                            "type": "string",
                            "description": "Ordre de tri : asc ou desc",
                            "default": "desc"
                        },
                        "lineCount": {
                            "type": "integer",
                            "description": "Nombre maximum de résultats",
                            "default": 20
                        },
                        "similarity_min": {
                            "type": "number",
                            "description": "Score de similarité minimum"
                        },
                        "similarity_max": {
                            "type": "number",
                            "description": "Score de similarité maximum"
                        },
                        "volume_min": {
                            "type": "integer",
                            "description": "Volume de recherche minimum"
                        },
                        "volume_max": {
                            "type": "integer",
                            "description": "Volume de recherche maximum"
                        }
                    },
                    "required": ["keyword"]
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Préparer les données pour l'API
        api_data = {
            "keyword": arguments["keyword"],
            "order_by": arguments.get("order_by", "similarity"),
            "order": arguments.get("order", "desc"),
            "lineCount": arguments.get("lineCount", 20),
            "page": 1
        }
        
        # Ajouter les filtres optionnels
        optional_filters = [
            "similarity_min", "similarity_max", "volume_min", "volume_max",
            "cpc_min", "cpc_max", "competition_min", "competition_max"
        ]
        
        for filter_name in optional_filters:
            if filter_name in arguments:
                api_data[filter_name] = arguments[filter_name]
        
        result = await self.client.request("keywords/highlights", api_data)
        
        return {
            "keyword": arguments["keyword"],
            "search_type": "highlights",
            "similarity_analysis": True,
            "results": result
        }
