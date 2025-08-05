"""
Outils MCP pour l'API Haloscan
Architecture ultra-modulaire : un fichier par fonction, organisé par catégorie
"""

# Import des outils Keywords depuis le sous-répertoire keywords/
from .keywords import (
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
    KeywordsScrapTool
)

# Import des outils Domains depuis le sous-répertoire domains/
from .domains import (
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
    DomainsGmbBacklinksCategoresTool
)

# Import de l'outil User (fichier unique à la racine)
from .get_user_credits import GetUserCreditsTool

__all__ = [
    # Keyword tools (validés avec spécifications complètes)
    "AnalyzeKeywordTool",           # keywords/overview
    "FindSimilarKeywordsTool",      # keywords/similar
    "GetKeywordQuestionsTool",      # keywords/questions
    "FindKeywordMatchesTool",       # keywords/match
    "GetKeywordHighlightsTool",     # keywords/highlights
    "FindRelatedKeywordsTool",      # keywords/related
    "GetKeywordSynonymsTool",       # keywords/synonyms
    "FindKeywordsTool",             # keywords/find
    "GetKeywordsSiteStructureTool", # keywords/siteStructure
    "GetKeywordsSerpCompareTool",   # keywords/serp/compare (domains)
    "KeywordsSerpCompareTool",      # keywords/serp/compare (keywords)
    "KeywordsSerpAvailableDatesTool",
    "KeywordsSerpPageEvolutionTool",  # keywords/serp/pageEvolution
    "KeywordsBulkTool",               # keywords/bulk
    "KeywordsScrapTool",              # keywords/scrap
    
    # Domain tools (validés)
    "AnalyzeDomainTool",            # domains/overview
    "FindDomainCompetitorsTool",    # domains/competitors
    "GetDomainTopPagesTool",        # domains/top-pages
    "SearchKeywordsByPositionTool",
    "DomainsTopPagesTool",             # domains/topPages
    "DomainsHistoryPositionsTool",     # domains/history
    "DomainsHistoryPagesTool",         # domains/pagesHistory
    "PageBestKeywordsTool",             # page/bestKeywords
    "DomainsKeywordsTool",              # domains/keywords
    "DomainsBulkTool",                  # domains/bulk
    "DomainsCompetitorsTool",            # domains/competitors (avec fallback)
    "DomainsCompetitorsKeywordsDiffTool", # domains/siteCompetitors/keywordsDiff
    "DomainsVisibilityTrendsTool",        # domains/history/visibilityTrends
    "DomainsExpiredRevealTool",           # domains/expired/reveal
    "DomainsGmbBacklinksTool",            # domains/gmbBacklinks
    "DomainsGmbBacklinksMapTool",         # domains/gmbBacklinks/map
    "DomainsGmbBacklinksCategoresTool",   # domains/gmbBacklinks/categories
    
    # User tools (validés)
    "GetUserCreditsTool"            # user/credit
]
