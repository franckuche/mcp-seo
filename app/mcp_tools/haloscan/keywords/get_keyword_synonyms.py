"""
Outil MCP pour keywords/synonyms - Synonymes de mots-clés avec filtres avancés
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class GetKeywordSynonymsTool(BaseMCPTool):
    """Outil MCP pour keywords/synonyms - Synonymes de mots-clés avec filtres avancés"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_keyword_synonyms",
                "description": "Trouve les synonymes et variations d'un mot-clé avec filtres de volume, CPC, concurrence, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé pour lequel chercher des synonymes"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Champ de tri : default, keyword, volume, cpc, competition, kgr, allintitle",
                            "default": "default"
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
                        "exact_match": {
                            "type": "boolean",
                            "description": "Correspondance exacte (accents, ponctuation, etc.)",
                            "default": True
                        },
                        "volume_min": {
                            "type": "integer",
                            "description": "Volume de recherche minimum"
                        },
                        "volume_max": {
                            "type": "integer",
                            "description": "Volume de recherche maximum"
                        },
                        "cpc_min": {
                            "type": "number",
                            "description": "CPC minimum"
                        },
                        "cpc_max": {
                            "type": "number",
                            "description": "CPC maximum"
                        },
                        "competition_min": {
                            "type": "number",
                            "description": "Concurrence minimum (0-1)"
                        },
                        "competition_max": {
                            "type": "number",
                            "description": "Concurrence maximum (0-1)"
                        },
                        "word_count_min": {
                            "type": "integer",
                            "description": "Nombre minimum de mots"
                        },
                        "word_count_max": {
                            "type": "integer",
                            "description": "Nombre maximum de mots"
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
            "order_by": arguments.get("order_by", "default"),
            "order": arguments.get("order", "desc"),
            "lineCount": arguments.get("lineCount", 20),
            "page": 1
        }
        
        # Ajouter les filtres optionnels
        optional_filters = [
            "exact_match", "volume_min", "volume_max", "cpc_min", "cpc_max",
            "competition_min", "competition_max", "word_count_min", "word_count_max"
        ]
        
        for filter_name in optional_filters:
            if filter_name in arguments:
                api_data[filter_name] = arguments[filter_name]
        
        result = await self.client.request("keywords/synonyms", api_data)
        
        return {
            "keyword": arguments["keyword"],
            "search_type": "synonyms",
            "filters_applied": {k: v for k, v in arguments.items() if k in optional_filters},
            "results": result
        }
