"""
Outil MCP pour keywords/related - Mots-clés connexes avec profondeur d'analyse
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class FindRelatedKeywordsTool(BaseMCPTool):
    """Outil MCP pour keywords/related - Mots-clés connexes avec profondeur d'analyse"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_related_keywords",
                "description": "Trouve des mots-clés connexes et sémantiquement liés avec analyse de profondeur",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé de base pour trouver des connexes"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Champ de tri : default, depth, keyword, volume, cpc, competition, kgr, allintitle",
                            "default": "depth"
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
                        "depth_min": {
                            "type": "number",
                            "description": "Profondeur d'analyse minimum"
                        },
                        "depth_max": {
                            "type": "number",
                            "description": "Profondeur d'analyse maximum"
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
            "order_by": arguments.get("order_by", "depth"),
            "order": arguments.get("order", "desc"),
            "lineCount": arguments.get("lineCount", 20),
            "page": 1
        }
        
        # Ajouter les filtres optionnels
        optional_filters = [
            "depth_min", "depth_max", "volume_min", "volume_max",
            "cpc_min", "cpc_max", "competition_min", "competition_max"
        ]
        
        for filter_name in optional_filters:
            if filter_name in arguments:
                api_data[filter_name] = arguments[filter_name]
        
        result = await self.client.request("keywords/related", api_data)
        
        return {
            "keyword": arguments["keyword"],
            "search_type": "related_keywords",
            "depth_analysis": True,
            "results": result
        }
