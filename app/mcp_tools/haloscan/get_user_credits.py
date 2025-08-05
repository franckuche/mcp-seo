"""
Outil MCP pour user/credit - Informations de crédits utilisateur
"""
from typing import Dict, Any
from ..base import BaseMCPTool

class GetUserCreditsTool(BaseMCPTool):
    """Outil MCP pour user/credit"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user_credits",
                "description": "Récupère les informations de crédits disponibles pour l'utilisateur Haloscan",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.client.get_user_credit()
        
        return {
            "credits_info": result
        }
