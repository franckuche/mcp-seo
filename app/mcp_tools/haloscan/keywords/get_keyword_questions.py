"""
Outil MCP pour keywords/questions - Questions fréquemment posées liées à un mot-clé
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class GetKeywordQuestionsTool(BaseMCPTool):
    """Outil MCP pour keywords/questions - Questions fréquemment posées avec filtres avancés"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_keyword_questions",
                "description": "Récupère les questions fréquemment posées liées à un mot-clé avec filtres avancés (types de questions, PAA, profondeur, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé pour lequel chercher des questions"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Champ de tri : default, depth, question_type, keyword, volume, cpc, competition, kgr, allintitle",
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
                        "question_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["definition", "how", "how_expensive", "how_many", "what", "when", "where", "who", "why", "yesno", "how_long", "unknown"]
                            },
                            "description": "Types de questions à inclure"
                        },
                        "keep_only_paa": {
                            "type": "boolean",
                            "description": "Inclure seulement les questions PAA (People Also Ask) de Google",
                            "default": False
                        },
                        "exact_match": {
                            "type": "boolean",
                            "description": "Correspondance exacte (accents, ponctuation, etc.)",
                            "default": True
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
            "order_by": arguments.get("order_by", "default"),
            "order": arguments.get("order", "desc"),
            "lineCount": arguments.get("lineCount", 20),
            "page": 1
        }
        
        # Ajouter les filtres optionnels
        optional_filters = [
            "question_types", "keep_only_paa", "exact_match", "depth_min", "depth_max",
            "volume_min", "volume_max", "cpc_min", "cpc_max", "competition_min", "competition_max"
        ]
        
        for filter_name in optional_filters:
            if filter_name in arguments:
                api_data[filter_name] = arguments[filter_name]
        
        result = await self.client.request("keywords/questions", api_data)
        
        return {
            "keyword": arguments["keyword"],
            "search_type": "questions",
            "filters_applied": {k: v for k, v in arguments.items() if k in optional_filters},
            "results": result
        }
