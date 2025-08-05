"""
MCP Tool pour l'endpoint Haloscan keywords/siteStructure
Analyse de la structure de site et détection de cannibalisation de mots-clés
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool


class GetKeywordsSiteStructureTool(BaseMCPTool):
    """Outil MCP pour analyser la structure de site et détecter la cannibalisation"""
    
    def get_name(self) -> str:
        return "get_keywords_site_structure"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_keywords_site_structure",
                "description": "Analyse la structure de site et détecte la cannibalisation de mots-clés entre pages",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Nom de domaine à analyser (ex: lemonde.fr)"
                        },
                        "lang": {
                            "type": "string",
                            "description": "Langue d'analyse (fr, en, es, de, it, pt, nl)",
                            "default": "fr"
                        },
                        "mode": {
                            "type": "string",
                            "description": "Mode de groupement (multi ou manual)",
                            "enum": ["multi", "manual"],
                            "default": "multi"
                        },
                        "granularity": {
                            "type": "string",
                            "description": "Granularité de l'analyse (page, directory, subdomain)",
                            "enum": ["page", "directory", "subdomain"],
                            "default": "page"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Nombre maximum de résultats (défaut: 100)",
                            "default": 100
                        }
                    },
                    "required": ["domain"]
                }
            }
        }
    
    def get_description(self) -> str:
        return "Analyse la structure de site et détecte la cannibalisation de mots-clés avec groupement automatique ou manuel"
    
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
                            "description": "Mot-clé principal à analyser (ignoré si keywords est fourni)"
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Liste de mots-clés pour analyse en lot (minimum 50 mots-clés)",
                            "minItems": 50
                        },
                        "exact_match": {
                            "type": "boolean",
                            "description": "Correspondance exacte (ignorer accents, ponctuation si False)",
                            "default": True
                        },
                        "neighbours_sources": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["ngram", "serp", "related", "highlights", "categories"]},
                            "description": "Stratégies pour trouver les mots-clés voisins (ignoré si keywords est utilisé)"
                        },
                        "multipartite_modes": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["ngram", "serp", "related", "highlights", "categories"]},
                            "description": "Sources de données pour construire le graphe multipartite (ignoré si mode≠multi)"
                        },
                        "neighbours_sample_max_size": {
                            "type": "integer",
                            "description": "Nombre maximum de résultats retournés (10-2000, uniquement pour un seul mot-clé)",
                            "default": 1000,
                            "minimum": 10,
                            "maximum": 2000
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["multi", "manual"],
                            "description": "Mode de groupement : 'multi' (automatique hiérarchique) ou 'manual' (basé sur URLs communes)",
                            "default": "multi"
                        },
                        "granularity": {
                            "type": "number",
                            "description": "Granularité du groupement (ignoré si mode=manual). Valeurs: 0.001 (insuffisant), 0.01 (très faible), 0.05 (faible), 0.1 (modéré), 0.25 (moyen), 0.67 (élevé), 1 (très élevé), 10 (excessif)",
                            "default": 1,
                            "minimum": 0.001,
                            "maximum": 10
                        },
                        "manual_common_10": {
                            "type": "integer",
                            "description": "Nombre d'URLs communes dans le top 10 pour grouper (mode manual uniquement)",
                            "default": 2,
                            "minimum": 1
                        },
                        "manual_common_100": {
                            "type": "integer",
                            "description": "Nombre d'URLs communes dans le top 100 pour grouper (mode manual uniquement)",
                            "default": 10,
                            "minimum": 1
                        }
                    },
                    "required": []  # Aucun paramètre obligatoire selon la doc
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute l'analyse de structure de site"""
        
        # Construire les paramètres de la requête
        params = {}
        
        # Paramètres de base - mot-clé ou liste de mots-clés
        if "keywords" in arguments and arguments["keywords"]:
            if len(arguments["keywords"]) < 50:
                return {
                    "tool": self.get_name(),
                    "success": False,
                    "error": "L'analyse en lot nécessite au moins 50 mots-clés"
                }
            params["keywords"] = arguments["keywords"]
        elif "keyword" in arguments:
            params["keyword"] = arguments["keyword"]
        else:
            # Si aucun mot-clé n'est fourni, utiliser un exemple
            params["keyword"] = "plombier"
        
        # Paramètres optionnels avec valeurs par défaut
        params["exact_match"] = arguments.get("exact_match", True)
        params["mode"] = arguments.get("mode", "multi")
        
        # Paramètres spécifiques au mode multi
        if params["mode"] == "multi":
            params["granularity"] = arguments.get("granularity", 1)
            if "multipartite_modes" in arguments:
                params["multipartite_modes"] = arguments["multipartite_modes"]
        
        # Paramètres spécifiques au mode manual
        if params["mode"] == "manual":
            params["manual_common_10"] = arguments.get("manual_common_10", 2)
            params["manual_common_100"] = arguments.get("manual_common_100", 10)
        
        # Paramètres pour un seul mot-clé
        if "keyword" in params:
            params["neighbours_sample_max_size"] = arguments.get("neighbours_sample_max_size", 1000)
            if "neighbours_sources" in arguments:
                params["neighbours_sources"] = arguments["neighbours_sources"]
        
        # Appeler l'API Haloscan
        result = await self.client.request("keywords/siteStructure", params)
        
        # Analyser les résultats pour fournir un résumé
        summary = {
            "analysis_type": "bulk" if "keywords" in params else "single",
            "mode": params["mode"],
            "seed_keyword": params.get("keyword", f"{len(params.get('keywords', []))} mots-clés")
        }
        
        if isinstance(result, dict):
            # Analyser la cannibalisation
            if "cannibalisation" in result and isinstance(result["cannibalisation"], list):
                groups = {}
                for item in result["cannibalisation"]:
                    group_name = item.get("groupe", "Unknown")
                    if group_name not in groups:
                        groups[group_name] = []
                    groups[group_name].append(item.get("keyword", ""))
                
                summary["cannibalization"] = {
                    "total_groups": len(groups),
                    "total_keywords": len(result["cannibalisation"]),
                    "largest_group": max(len(keywords) for keywords in groups.values()) if groups else 0,
                    "groups_preview": list(groups.keys())[:5]
                }
            
            # Analyser le graphe hiérarchique
            if "graph" in result and isinstance(result["graph"], dict):
                summary["graph_structure"] = {
                    "has_hierarchy": "children" in result["graph"],
                    "response_time": result.get("response_time", "N/A")
                }
            
            # Analyser le tableau de données
            if "table" in result and isinstance(result["table"], list):
                summary["data_table"] = {
                    "total_keywords": len(result["table"]),
                    "has_volume_data": any(item.get("volume") for item in result["table"][:5]),
                    "has_competition_data": any(item.get("competition") for item in result["table"][:5])
                }
        
        return {
            "tool": self.get_name(),
            "success": True,
            "data": result,
            "summary": summary
        }
