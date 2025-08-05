"""
Outil MCP pour domains/overview - Analyse complète d'un domaine
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class AnalyzeDomainTool(BaseMCPTool):
    """Outil MCP pour domains/overview"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "analyze_domain",
                "description": "Analyse complète d'un domaine : trafic, autorité, mots-clés, pages positionnées",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Le domaine à analyser (ex: example.com)"
                        },
                        "lang": {
                            "type": "string",
                            "description": "Langue d'analyse",
                            "default": "fr"
                        }
                    },
                    "required": ["domain"]
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        domain = arguments["domain"]
        lang = arguments.get("lang", "fr")
        
        result = await self.client.get_domains_overview(domain, lang)
        
        return {
            "domain": domain,
            "language": lang,
            "overview": result
        }
