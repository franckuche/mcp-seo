"""
Outil MCP pour keywords/overview - Analyse complète d'un mot-clé
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class AnalyzeKeywordTool(BaseMCPTool):
    """Outil MCP pour keywords/overview"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "analyze_keyword",
                "description": "Analyse complète d'un mot-clé SEO : volume, difficulté, CPC, SERP, concurrence",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Le mot-clé à analyser"
                        },
                        "lang": {
                            "type": "string",
                            "description": "Langue d'analyse (fr, en, es, de, it, pt, nl)",
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
        
        result = await self.client.get_keywords_overview(keyword, lang)
        
        return {
            "keyword": keyword,
            "language": lang,
            "analysis": result
        }
