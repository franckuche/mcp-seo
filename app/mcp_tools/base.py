"""
Base classes pour les outils MCP Haloscan
Architecture modulaire et scalable
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..dependencies import HaloscanClient
from ..logging_config import get_logger

logger = get_logger("mcp_tools")

class BaseMCPTool(ABC):
    """Classe de base pour tous les outils MCP Haloscan"""
    
    def __init__(self, client: HaloscanClient):
        self.client = client
        # Utiliser le nom de la fonction OpenAI au lieu du nom de classe
        tool_def = self.get_tool_definition()
        self.tool_name = tool_def["function"]["name"]
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """Retourne la définition OpenAI de l'outil"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute l'outil avec les arguments donnés"""
        pass
    
    def _log_execution_start(self, arguments: Dict[str, Any]):
        """Log le début d'exécution"""
        logger.info(f"🔧 DÉBUT Exécution de l'outil: {self.tool_name}")
        logger.info(f"📝 Arguments reçus: {arguments}")
    
    def _log_execution_success(self, result: Any):
        """Log le succès d'exécution"""
        logger.info(f"✅ Outil {self.tool_name} exécuté avec succès")
        if isinstance(result, dict) and 'keywords_found' in result:
            logger.info(f"📊 Résultats: {result['keywords_found']} éléments trouvés")
    
    def _log_execution_error(self, error: Exception, arguments: Dict[str, Any]):
        """Log l'erreur d'exécution"""
        logger.error(f"❌ ERREUR dans {self.tool_name}: {str(error)}")
        logger.error(f"📍 Arguments: {arguments}")
        import traceback
        logger.error(f"📚 Stack trace: {traceback.format_exc()}")
    
    async def safe_execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécution sécurisée avec gestion d'erreurs"""
        self._log_execution_start(arguments)
        
        try:
            result = await self.execute(arguments)
            self._log_execution_success(result)
            
            return {
                "tool": self.tool_name,
                "success": True,
                "data": result
            }
            
        except Exception as e:
            self._log_execution_error(e, arguments)
            
            return {
                "tool": self.tool_name,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "arguments_used": arguments
            }

class MCPToolRegistry:
    """Registre centralisé pour tous les outils MCP"""
    
    def __init__(self):
        self.tools: Dict[str, BaseMCPTool] = {}
    
    def register_tool(self, tool: BaseMCPTool):
        """Enregistre un nouvel outil"""
        self.tools[tool.tool_name] = tool
        logger.info(f"🔧 Outil MCP enregistré: {tool.tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseMCPTool]:
        """Récupère un outil par son nom"""
        return self.tools.get(tool_name)
    
    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """Retourne toutes les définitions d'outils pour OpenAI"""
        return [tool.get_tool_definition() for tool in self.tools.values()]
    
    def list_tools(self) -> List[str]:
        """Liste tous les outils disponibles"""
        return list(self.tools.keys())
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil par son nom"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "tool": tool_name,
                "success": False,
                "error": f"Outil '{tool_name}' non trouvé. Outils disponibles: {self.list_tools()}"
            }
        
        return await tool.safe_execute(arguments)
