"""
MCP Tool pour l'endpoint Haloscan keywords/find
Recherche avancée de mots-clés avec filtres multiples
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool


class FindKeywordsTool(BaseMCPTool):
    """Outil MCP pour rechercher des mots-clés avec filtres avancés"""
    
    def get_name(self) -> str:
        return "find_keywords"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_keywords",
                "description": "Recherche avancée de mots-clés avec filtres multiples : volume, CPC, concurrence, regex, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Mot-clé de base pour la recherche"
                        },
                        "lang": {
                            "type": "string",
                            "description": "Langue de recherche (fr, en, es, de, it, pt, nl)",
                            "default": "fr"
                        },
                        "volume_min": {
                            "type": "integer",
                            "description": "Volume de recherche minimum"
                        },
                        "volume_max": {
                            "type": "integer",
                            "description": "Volume de recherche maximum"
                        },
                        "cpc_min": {
                            "type": "number",
                            "description": "CPC minimum en euros"
                        },
                        "cpc_max": {
                            "type": "number",
                            "description": "CPC maximum en euros"
                        },
                        "competition_min": {
                            "type": "number",
                            "description": "Niveau de concurrence minimum (0-1)"
                        },
                        "competition_max": {
                            "type": "number",
                            "description": "Niveau de concurrence maximum (0-1)"
                        },
                        "regex": {
                            "type": "string",
                            "description": "Expression régulière pour filtrer les résultats"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Nombre maximum de résultats (défaut: 50)",
                            "default": 50
                        }
                    },
                    "required": ["keyword"]
                }
            }
        }
    
    def get_description(self) -> str:
        return "Recherche avancée de mots-clés avec filtres multiples (volume, CPC, concurrence, etc.)"
    
    def get_openai_function_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Mot-clé principal à rechercher (utiliser soit keyword soit keywords)"
                        },
                        "keywords": {
                            "type": "string",
                            "description": "Plusieurs mots-clés séparés par des virgules (ignoré si keyword est présent)"
                        },
                        "keywords_sources": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["match", "serp", "related", "highlights", "categories", "questions"]},
                            "description": "Stratégies de recherche à utiliser",
                            "default": ["serp", "related"]
                        },
                        "keep_seed": {
                            "type": "boolean",
                            "description": "Conserver le mot-clé d'entrée dans les résultats",
                            "default": True
                        },
                        "lineCount": {
                            "type": "integer",
                            "description": "Nombre maximum de résultats retournés",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "page": {
                            "type": "integer",
                            "description": "Numéro de page pour la pagination",
                            "default": 1,
                            "minimum": 1
                        },
                        "order_by": {
                            "type": "string",
                            "enum": ["default", "keyword", "volume", "cpc", "competition", "kgr", "allintitle"],
                            "description": "Champ utilisé pour le tri des résultats",
                            "default": "default"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Ordre de tri (croissant ou décroissant)",
                            "default": "asc"
                        },
                        "exact_match": {
                            "type": "boolean",
                            "description": "Correspondance exacte (ignorer accents, ponctuation si False)",
                            "default": True
                        },
                        "volume_min": {
                            "type": "integer",
                            "description": "Volume de recherche minimum",
                            "minimum": 0
                        },
                        "volume_max": {
                            "type": "integer",
                            "description": "Volume de recherche maximum",
                            "minimum": 0
                        },
                        "cpc_min": {
                            "type": "number",
                            "description": "Coût par clic minimum",
                            "minimum": 0
                        },
                        "cpc_max": {
                            "type": "number",
                            "description": "Coût par clic maximum",
                            "minimum": 0
                        },
                        "competition_min": {
                            "type": "number",
                            "description": "Niveau de concurrence minimum (0-1)",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "competition_max": {
                            "type": "number",
                            "description": "Niveau de concurrence maximum (0-1)",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "kgr_min": {
                            "type": "number",
                            "description": "KGR (Keyword Golden Ratio) minimum",
                            "minimum": 0
                        },
                        "kgr_max": {
                            "type": "number",
                            "description": "KGR (Keyword Golden Ratio) maximum",
                            "minimum": 0
                        },
                        "kvi_min": {
                            "type": "number",
                            "description": "KVI (Keyword Value Index) minimum",
                            "minimum": 0
                        },
                        "kvi_max": {
                            "type": "number",
                            "description": "KVI (Keyword Value Index) maximum",
                            "minimum": 0
                        },
                        "kvi_keep_na": {
                            "type": "boolean",
                            "description": "Conserver les mots-clés avec KVI non disponible"
                        },
                        "allintitle_min": {
                            "type": "integer",
                            "description": "Nombre minimum de résultats allintitle",
                            "minimum": 0
                        },
                        "allintitle_max": {
                            "type": "integer",
                            "description": "Nombre maximum de résultats allintitle",
                            "minimum": 0
                        },
                        "include": {
                            "type": "string",
                            "description": "Expression régulière pour inclure des mots-clés"
                        },
                        "exclude": {
                            "type": "string",
                            "description": "Expression régulière pour exclure des mots-clés"
                        }
                    },
                    "required": []  # Aucun paramètre obligatoire selon la doc
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute la recherche avancée de mots-clés"""
        
        # Construire les paramètres de la requête
        params = {}
        
        # Paramètres de base
        if "keyword" in arguments:
            params["keyword"] = arguments["keyword"]
        elif "keywords" in arguments:
            params["keywords"] = arguments["keywords"]
        else:
            # Si aucun mot-clé n'est fourni, utiliser un exemple
            params["keyword"] = "seo"
        
        # Paramètres optionnels avec valeurs par défaut
        params["keywords_sources"] = arguments.get("keywords_sources", ["serp", "related"])
        params["keep_seed"] = arguments.get("keep_seed", True)
        params["lineCount"] = arguments.get("lineCount", 20)
        params["page"] = arguments.get("page", 1)
        params["order_by"] = arguments.get("order_by", "default")
        params["order"] = arguments.get("order", "asc")
        params["exact_match"] = arguments.get("exact_match", True)
        
        # Filtres numériques (seulement si fournis)
        for filter_param in ["volume_min", "volume_max", "cpc_min", "cpc_max", 
                           "competition_min", "competition_max", "kgr_min", "kgr_max",
                           "kvi_min", "kvi_max", "allintitle_min", "allintitle_max"]:
            if filter_param in arguments:
                params[filter_param] = arguments[filter_param]
        
        # Paramètres booléens optionnels
        if "kvi_keep_na" in arguments:
            params["kvi_keep_na"] = arguments["kvi_keep_na"]
        
        # Filtres regex
        if "include" in arguments:
            params["include"] = arguments["include"]
        if "exclude" in arguments:
            params["exclude"] = arguments["exclude"]
        
        # Appeler l'API Haloscan
        result = await self.client.request("keywords/find", params)
        
        return {
            "tool": self.get_name(),
            "success": True,
            "data": result,
            "summary": {
                "total_results": result.get("total_result_count", 0),
                "filtered_results": result.get("filtered_result_count", 0),
                "returned_results": result.get("result_count", 0),
                "search_params": {
                    "keyword": params.get("keyword", params.get("keywords", "N/A")),
                    "sources": params["keywords_sources"],
                    "filters_applied": len([k for k in params.keys() if k.endswith(("_min", "_max", "include", "exclude"))])
                }
            }
        }
