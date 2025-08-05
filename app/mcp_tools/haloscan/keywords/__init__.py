"""
Outils MCP pour les endpoints Keywords de Haloscan
Un fichier par fonction pour une modularité maximale
"""

# Outils Keywords validés avec spécifications complètes
from .analyze_keyword import AnalyzeKeywordTool
from .find_keyword_matches import FindKeywordMatchesTool
from .get_keyword_highlights import GetKeywordHighlightsTool
from .find_related_keywords import FindRelatedKeywordsTool
from .find_similar_keywords import FindSimilarKeywordsTool
from .get_keyword_questions import GetKeywordQuestionsTool
from .get_keyword_synonyms import GetKeywordSynonymsTool
from .find_keywords import FindKeywordsTool  # Outil de recherche avancée
from .get_keywords_site_structure import GetKeywordsSiteStructureTool
from .get_keywords_serp_compare import GetKeywordsSerpCompareTool
from .keywords_serp_compare import KeywordsSerpCompareTool
from .keywords_serp_available_dates import KeywordsSerpAvailableDatesTool
from .keywords_serp_page_evolution import KeywordsSerpPageEvolutionTool
from .keywords_bulk import KeywordsBulkTool
from .keywords_scrap import KeywordsScrapTool

# TODO: Créer ces outils avec spécifications utilisateur
# from .get_keywords_serp_page_evolution import GetKeywordsSerpPageEvolutionTool
# from .get_keywords_bulk import GetKeywordsBulkTool
# from .get_keywords_scrap import GetKeywordsScrapTool

__all__ = [
    # Outils avec spécifications complètes Haloscan
    "AnalyzeKeywordTool",           # keywords/overview
    "FindKeywordMatchesTool",       # keywords/match
    "GetKeywordHighlightsTool",     # keywords/highlights
    "FindRelatedKeywordsTool",      # keywords/related
    "FindSimilarKeywordsTool",      # keywords/similar
    "GetKeywordQuestionsTool",      # keywords/questions
    "GetKeywordSynonymsTool",       # keywords/synonyms
    "FindKeywordsTool",             # keywords/find
    "GetKeywordsSiteStructureTool", # keywords/siteStructure
    "GetKeywordsSerpCompareTool",   # keywords/serp/compare (domains)
    "KeywordsSerpCompareTool",      # keywords/serp/compare (keywords)
    "KeywordsSerpAvailableDatesTool", # keywords/serp/availableDates
    "KeywordsSerpPageEvolutionTool",  # keywords/serp/pageEvolution
    "KeywordsBulkTool",               # keywords/bulk
    "KeywordsScrapTool"               # keywords/scrap
]
