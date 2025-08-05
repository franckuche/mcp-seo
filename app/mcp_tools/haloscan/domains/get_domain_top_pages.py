"""
Outil MCP pour domains/top-pages - Pages les plus performantes d'un domaine
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class GetDomainTopPagesTool(BaseMCPTool):
    """Outil MCP pour domains/top-pages"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_domain_top_pages",
                "description": "Récupère les pages les plus performantes d'un domaine en termes de trafic SEO",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Le domaine à analyser"
                        }
                    },
                    "required": ["domain"]
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        domain = arguments["domain"]
        
        result = await self.client.get_domains_top_pages(domain)
        
        return {
            "domain": domain,
            "top_pages": result
        }
