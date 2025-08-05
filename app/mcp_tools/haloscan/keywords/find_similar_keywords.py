"""
Outil MCP pour keywords/similar - Mots-clés similaires et suggestions
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class FindSimilarKeywordsTool(BaseMCPTool):
    """Outil MCP pour keywords/similar"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_similar_keywords",
                "description": "Trouve des mots-clés similaires et suggestions pour un mot-clé donné",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé de base pour trouver des similaires"
                        },
                        "lang": {
                            "type": "string",
                            "description": "Langue de recherche",
                            "default": "fr"
                        }
                    },
                    "required": ["keyword"]
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        keyword = arguments["keyword"]
        lang = arguments.get("lang", "fr")
        
        result = await self.client.get_keywords_similar(keyword, lang)
        
        return {
            "base_keyword": keyword,
            "language": lang,
            "similar_keywords": result
        }
