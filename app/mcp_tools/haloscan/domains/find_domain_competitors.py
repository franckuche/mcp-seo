"""
Outil MCP pour domains/competitors - Trouve les concurrents organiques d'un domaine
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class FindDomainCompetitorsTool(BaseMCPTool):
    """Outil MCP pour domains/competitors"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_domain_competitors",
                "description": "Trouve les concurrents organiques d'un domaine basés sur les mots-clés communs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Le domaine pour lequel chercher des concurrents"
                        }
                    },
                    "required": ["domain"]
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        domain = arguments["domain"]
        
        result = await self.client.get_domains_competitors(domain)
        
        return {
            "domain": domain,
            "competitors": result
        }
