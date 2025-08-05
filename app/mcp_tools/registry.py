"""
Registre centralisé pour tous les outils MCP
Architecture modulaire et extensible
"""
from typing import Dict, Any, List, Optional
from .base import MCPToolRegistry
from .haloscan import (
    # Keywords tools (validés avec spécifications complètes)
    AnalyzeKeywordTool,
    FindSimilarKeywordsTool,
    GetKeywordQuestionsTool,
    FindKeywordMatchesTool,
    GetKeywordHighlightsTool,
    FindRelatedKeywordsTool,
    GetKeywordSynonymsTool,
    FindKeywordsTool,
    GetKeywordsSiteStructureTool,
    GetKeywordsSerpCompareTool,
    KeywordsSerpCompareTool,
    KeywordsSerpAvailableDatesTool,
    KeywordsSerpPageEvolutionTool,
    KeywordsBulkTool,
    KeywordsScrapTool,
    # Domain tools (validés)
    AnalyzeDomainTool,
    FindDomainCompetitorsTool,
    GetDomainTopPagesTool,
    SearchKeywordsByPositionTool,
    DomainsTopPagesTool,
    DomainsHistoryPositionsTool,
    DomainsHistoryPagesTool,
    PageBestKeywordsTool,
    DomainsKeywordsTool,
    DomainsBulkTool,
    DomainsCompetitorsTool,
    DomainsCompetitorsKeywordsDiffTool,
    DomainsVisibilityTrendsTool,
    DomainsExpiredRevealTool,
    DomainsGmbBacklinksTool,
    DomainsGmbBacklinksMapTool,
    DomainsGmbBacklinksCategoresTool,
    # User tools (validés)
    GetUserCreditsTool
)
from ..dependencies import HaloscanClient
from ..logging_config import get_logger

logger = get_logger("mcp_registry")

class GlobalMCPRegistry:
    """Registre global pour tous les providers MCP (Haloscan, Google Analytics, etc.)"""
    
    def __init__(self):
        self.registries: Dict[str, MCPToolRegistry] = {}
        self.clients: Dict[str, Any] = {}
    
    def register_haloscan_tools(self, haloscan_client: HaloscanClient):
        """Enregistre tous les outils Haloscan"""
        logger.info("🔧 Enregistrement des outils Haloscan...")
        
        # Créer le registre Haloscan
        haloscan_registry = MCPToolRegistry()
        
        # Enregistrer tous les outils Haloscan validés
        tools = [
            # Keyword tools (avec spécifications complètes)
            AnalyzeKeywordTool(haloscan_client),           # keywords/overview
            FindSimilarKeywordsTool(haloscan_client),      # keywords/similar
            GetKeywordQuestionsTool(haloscan_client),      # keywords/questions
            FindKeywordMatchesTool(haloscan_client),       # keywords/match
            GetKeywordHighlightsTool(haloscan_client),     # keywords/highlights
            FindRelatedKeywordsTool(haloscan_client),      # keywords/related
            GetKeywordSynonymsTool(haloscan_client),       # keywords/synonyms
            FindKeywordsTool(haloscan_client),             # keywords/find
            GetKeywordsSiteStructureTool(haloscan_client), # keywords/siteStructure
            GetKeywordsSerpCompareTool(haloscan_client),   # keywords/serp/compare (domains)
            KeywordsSerpCompareTool(haloscan_client),      # keywords/serp/compare (keywords)
            KeywordsSerpAvailableDatesTool(haloscan_client), # keywords/serp/availableDates
            KeywordsSerpPageEvolutionTool(haloscan_client), # keywords/serp/pageEvolution
            KeywordsBulkTool(haloscan_client),              # keywords/bulk
            KeywordsScrapTool(haloscan_client),             # keywords/scrap
            
            # Domain tools (validés)
            AnalyzeDomainTool(haloscan_client),            # domains/overview
            DomainsCompetitorsTool(haloscan_client),       # domains/competitors (avec fallback)
            GetDomainTopPagesTool(haloscan_client),        # domains/top-pages
            SearchKeywordsByPositionTool(haloscan_client), # domains/positions
            DomainsTopPagesTool(haloscan_client),          # domains/topPages
            DomainsHistoryPositionsTool(haloscan_client),  # domains/history
            DomainsHistoryPagesTool(haloscan_client),      # domains/pagesHistory
            PageBestKeywordsTool(haloscan_client),         # page/bestKeywords
            DomainsKeywordsTool(haloscan_client),          # domains/keywords
            DomainsBulkTool(haloscan_client),              # domains/bulk
            DomainsCompetitorsKeywordsDiffTool(haloscan_client), # domains/siteCompetitors/keywordsDiff
            DomainsVisibilityTrendsTool(haloscan_client),        # domains/history/visibilityTrends
            DomainsExpiredRevealTool(haloscan_client),           # domains/expired/reveal
            DomainsGmbBacklinksTool(haloscan_client),            # domains/gmbBacklinks
            DomainsGmbBacklinksMapTool(haloscan_client),         # domains/gmbBacklinks/map
            DomainsGmbBacklinksCategoresTool(haloscan_client),   # domains/gmbBacklinks/categories
            
            # User tools (validés)
            GetUserCreditsTool(haloscan_client)            # user/credit
        ]
        
        for tool in tools:
            haloscan_registry.register_tool(tool)
        
        self.registries["haloscan"] = haloscan_registry
        self.clients["haloscan"] = haloscan_client
        
        logger.info(f"✅ {len(tools)} outils Haloscan enregistrés")
    
    def register_future_provider(self, provider_name: str, client: Any, tools: List[Any]):
        """Méthode pour enregistrer de futurs providers (Google Analytics, SEMrush, etc.)"""
        logger.info(f"🔧 Enregistrement des outils {provider_name}...")
        
        provider_registry = MCPToolRegistry()
        
        for tool in tools:
            provider_registry.register_tool(tool)
        
        self.registries[provider_name] = provider_registry
        self.clients[provider_name] = client
        
        logger.info(f"✅ {len(tools)} outils {provider_name} enregistrés")
    
    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """Retourne toutes les définitions d'outils de tous les providers"""
        all_definitions = []
        
        for provider, registry in self.registries.items():
            provider_definitions = registry.get_all_tool_definitions()
            all_definitions.extend(provider_definitions)
            logger.debug(f"📊 {len(provider_definitions)} outils de {provider} ajoutés")
        
        logger.info(f"🎯 Total: {len(all_definitions)} outils MCP disponibles")
        return all_definitions
    
    def get_tool_by_name(self, tool_name: str) -> Optional[Any]:
        """Trouve un outil par son nom dans tous les providers"""
        for provider, registry in self.registries.items():
            tool = registry.get_tool(tool_name)
            if tool:
                logger.debug(f"🔍 Outil '{tool_name}' trouvé dans {provider}")
                return tool
        
        logger.warning(f"❌ Outil '{tool_name}' non trouvé")
        return None
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil par son nom"""
        logger.info(f"🚀 Exécution de l'outil: {tool_name}")
        
        # Chercher l'outil dans tous les providers
        for provider, registry in self.registries.items():
            tool = registry.get_tool(tool_name)
            if tool:
                logger.info(f"📍 Outil trouvé dans le provider: {provider}")
                return await registry.execute_tool(tool_name, arguments)
        
        # Outil non trouvé
        available_tools = self.list_all_tools()
        error_msg = f"Outil '{tool_name}' non trouvé. Outils disponibles: {available_tools}"
        logger.error(error_msg)
        
        return {
            "tool": tool_name,
            "success": False,
            "error": error_msg,
            "available_tools": available_tools
        }
    
    def list_all_tools(self) -> List[str]:
        """Liste tous les outils disponibles de tous les providers"""
        all_tools = []
        
        for provider, registry in self.registries.items():
            provider_tools = registry.list_tools()
            all_tools.extend(provider_tools)
        
        return sorted(all_tools)
    
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """Retourne des informations sur tous les providers"""
        info = {}
        
        for provider, registry in self.registries.items():
            tools = registry.list_tools()
            info[provider] = {
                "tool_count": len(tools),
                "tools": tools,
                "client_type": type(self.clients[provider]).__name__
            }
        
        return info

# Instance globale du registre
global_mcp_registry = GlobalMCPRegistry()
