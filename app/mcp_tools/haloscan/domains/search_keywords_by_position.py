"""
Outil MCP pour domains/positions - Recherche avancée par plage de positions
"""
from typing import Dict, Any
from ...base import BaseMCPTool

class SearchKeywordsByPositionTool(BaseMCPTool):
    """Outil MCP pour domains/positions - Recherche avancée par plage de positions"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_keywords_by_position",
                "description": "Recherche avancée : trouve tous les mots-clés d'un domaine dans une plage de positions spécifique (ex: page 2 = positions 11-20)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Le domaine à analyser"
                        },
                        "position_min": {
                            "type": "integer",
                            "description": "Position minimum (1-100). Page 1 = 1-10, Page 2 = 11-20",
                            "default": 1
                        },
                        "position_max": {
                            "type": "integer",
                            "description": "Position maximum (1-100). Page 1 = 1-10, Page 2 = 11-20",
                            "default": 10
                        },
                        "lang": {
                            "type": "string",
                            "description": "Langue de recherche",
                            "default": "fr"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Nombre maximum de résultats à retourner",
                            "default": 20
                        }
                    },
                    "required": ["domain"]
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        domain = arguments["domain"]
        position_min = arguments.get("position_min", 1)
        position_max = arguments.get("position_max", 10)
        lang = arguments.get("lang", "fr")
        limit = arguments.get("limit", 20)
        
        # Utiliser le bon endpoint domains/positions selon la documentation
        positions_data = {
            "input": domain,
            "lineCount": 100,  # Plus de résultats pour filtrer
            "mode": "root",
            "order": "desc",
            "order_by": "traffic",
            "page": 1,
            "position_min": position_min,
            "position_max": position_max
        }
        
        result = await self.client.request("domains/positions", positions_data)
        
        # Traiter la réponse selon la structure documentée de Haloscan
        if isinstance(result, dict):
            # Vérifier les erreurs d'abord
            if 'failure_reason' in result and result['failure_reason']:
                raise Exception(f"Erreur API: {result['failure_reason']}")
            
            # Récupérer les résultats selon la documentation
            if 'results' in result and isinstance(result['results'], list):
                all_results = result['results']
                
                # Les résultats sont déjà filtrés par position grâce aux paramètres API
                # Garder seulement les meilleurs par trafic et limiter
                top_keywords = sorted(all_results, key=lambda x: x.get('traffic', 0), reverse=True)[:limit]
                
                # Simplifier les données pour réduire la taille
                simplified_keywords = []
                for kw in top_keywords:
                    if isinstance(kw, dict):
                        simplified_keywords.append({
                            "keyword": kw.get('keyword', 'N/A'),
                            "position": kw.get('position', 'N/A'),
                            "traffic": kw.get('traffic', 0),
                            "cpc": kw.get('cpc', 0),
                            "volume": kw.get('volume', 0),
                            "competition": kw.get('competition', 'N/A'),
                            "url": kw.get('url', 'N/A')
                        })
                
                return {
                    "domain": domain,
                    "position_range": f"{position_min}-{position_max}",
                    "keywords_found": len(all_results),
                    "total_results": result.get('total_result_count', 0),
                    "top_keywords": simplified_keywords,
                    "api_stats": {
                        "filtered_result_count": result.get('filtered_result_count', 0),
                        "returned_result_count": result.get('returned_result_count', 0)
                    }
                }
            else:
                # Aucun résultat trouvé
                return {
                    "domain": domain,
                    "position_range": f"{position_min}-{position_max}",
                    "keywords_found": 0,
                    "top_keywords": [],
                    "message": "Aucun mot-clé trouvé dans cette plage de positions"
                }
        else:
            raise Exception(f"Réponse API inattendue: {type(result)}")
