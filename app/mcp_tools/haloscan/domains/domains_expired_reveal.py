"""
MCP Tool pour l'endpoint Haloscan domains/expired/reveal
Permet de révéler les domaines expirés en utilisant les clés obtenues depuis l'endpoint domains/expired
"""

from typing import Dict, Any, List, Optional
from ...base import BaseMCPTool
from ....dependencies import HaloscanClient
from ....logging_config import get_logger

logger = get_logger("domains_expired_reveal_tool")

class DomainsExpiredRevealTool(BaseMCPTool):
    """Outil MCP pour révéler les domaines expirés via l'API Haloscan"""
    
    def __init__(self, haloscan_client: HaloscanClient):
        self.haloscan_client = haloscan_client
        self.tool_name = "domainsexpiredreveal"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """Définition OpenAI de l'outil pour révéler les domaines expirés"""
        return {
            "type": "function",
            "function": {
                "name": "domains_expired_reveal",
                "description": "Reveal expired root domains using keys retrieved from the domains/expired endpoint. Consumes expired domain credits to unveil the actual domain names.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "root_domain_keys": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of root_domain_key fields from items in the domains/expired endpoint which you want to reveal. 1 expired domain credit will be consumed for each item in this list that you haven't previously revealed.",
                            "minItems": 1,
                            "maxItems": 100
                        }
                    },
                    "required": ["root_domain_keys"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Exécute la révélation des domaines expirés"""
        try:
            # Validation des paramètres requis
            root_domain_keys = kwargs.get("root_domain_keys", [])
            
            if not root_domain_keys or not isinstance(root_domain_keys, list):
                return {"error": "Le paramètre 'root_domain_keys' est requis et doit être une liste d'entiers"}
            
            if not all(isinstance(key, int) for key in root_domain_keys):
                return {"error": "Toutes les clés doivent être des entiers"}
            
            if len(root_domain_keys) > 100:
                return {"error": "Maximum 100 clés autorisées par requête"}
            
            # Préparation des paramètres
            params = {
                "root_domain_keys": root_domain_keys
            }
            
            logger.info(f"🔍 Révélation de {len(root_domain_keys)} domaine(s) expiré(s) avec les clés: {root_domain_keys[:5]}{'...' if len(root_domain_keys) > 5 else ''}")
            
            # Appel à l'API Haloscan
            response = await self.haloscan_client.post_async("domains/expired/reveal", params)
            
            if not response:
                return {"error": "Aucune réponse de l'API Haloscan"}
            
            # Analyse et synthèse des résultats
            return self._analyze_expired_reveal_results(response, root_domain_keys)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la révélation des domaines expirés: {str(e)}")
            return {"error": f"Erreur lors de la révélation des domaines expirés: {str(e)}"}
    
    def _analyze_expired_reveal_results(self, response: Dict[str, Any], requested_keys: List[int]) -> Dict[str, Any]:
        """Analyse et synthèse des résultats de révélation des domaines expirés"""
        try:
            results = response.get("results", [])
            
            if not results:
                return {
                    "summary": f"Aucun domaine révélé pour les {len(requested_keys)} clés demandées",
                    "requested_keys": requested_keys,
                    "total_keys_requested": len(requested_keys),
                    "domains_revealed": 0,
                    "revealed_domains": []
                }
            
            # Analyse des domaines révélés
            revealed_domains = []
            revealed_keys = []
            
            for result in results:
                root_domain_key = result.get("root_domain_key")
                root_domain = result.get("root_domain", "")
                
                if root_domain_key and root_domain:
                    revealed_keys.append(root_domain_key)
                    
                    domain_analysis = {
                        "key": root_domain_key,
                        "domain": root_domain,
                        "tld": self._extract_tld(root_domain),
                        "domain_length": len(root_domain),
                        "has_hyphens": "-" in root_domain,
                        "has_numbers": any(c.isdigit() for c in root_domain),
                        "potential_value": self._assess_domain_value(root_domain),
                        "category": self._categorize_domain(root_domain)
                    }
                    revealed_domains.append(domain_analysis)
            
            # Clés non révélées
            unrevealed_keys = [key for key in requested_keys if key not in revealed_keys]
            
            # Analyse par TLD
            tld_distribution = {}
            for domain in revealed_domains:
                tld = domain["tld"]
                if tld not in tld_distribution:
                    tld_distribution[tld] = 0
                tld_distribution[tld] += 1
            
            # Analyse par catégorie
            category_distribution = {}
            for domain in revealed_domains:
                category = domain["category"]
                if category not in category_distribution:
                    category_distribution[category] = 0
                category_distribution[category] += 1
            
            # Domaines à fort potentiel
            high_value_domains = [d for d in revealed_domains if d["potential_value"] == "high"]
            premium_domains = [d for d in revealed_domains if d["domain_length"] <= 6 and not d["has_hyphens"] and not d["has_numbers"]]
            
            # Statistiques globales
            stats = {
                "total_keys_requested": len(requested_keys),
                "domains_revealed": len(revealed_domains),
                "success_rate": f"{(len(revealed_domains)/len(requested_keys)*100):.1f}%" if requested_keys else "0%",
                "unrevealed_keys_count": len(unrevealed_keys),
                "tld_distribution": dict(sorted(tld_distribution.items(), key=lambda x: x[1], reverse=True)),
                "category_distribution": category_distribution,
                "quality_metrics": {
                    "high_value_count": len(high_value_domains),
                    "premium_count": len(premium_domains),
                    "average_length": round(sum(d["domain_length"] for d in revealed_domains) / len(revealed_domains), 1) if revealed_domains else 0,
                    "with_hyphens": sum(1 for d in revealed_domains if d["has_hyphens"]),
                    "with_numbers": sum(1 for d in revealed_domains if d["has_numbers"])
                }
            }
            
            return {
                "summary": f"Révélation de {len(revealed_domains)} domaine(s) sur {len(requested_keys)} clé(s) demandée(s)",
                "requested_keys": requested_keys,
                "unrevealed_keys": unrevealed_keys,
                "statistics": stats,
                "revealed_domains": revealed_domains,
                "high_value_domains": high_value_domains,
                "premium_domains": premium_domains,
                "recommendations": self._generate_expired_reveal_recommendations(revealed_domains, stats),
                "response_metadata": {
                    "response_time": response.get("response_time", ""),
                    "total_results": len(results)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des résultats: {str(e)}")
            return {"error": f"Erreur lors de l'analyse des résultats: {str(e)}"}
    
    def _extract_tld(self, domain: str) -> str:
        """Extrait le TLD d'un domaine"""
        parts = domain.split('.')
        return parts[-1] if len(parts) > 1 else ""
    
    def _assess_domain_value(self, domain: str) -> str:
        """Évalue le potentiel de valeur d'un domaine"""
        # Critères de valeur
        length = len(domain.replace('.', '').split('.')[0])  # Longueur sans TLD
        has_hyphens = "-" in domain
        has_numbers = any(c.isdigit() for c in domain)
        tld = self._extract_tld(domain)
        
        # Mots-clés commerciaux courants
        commercial_keywords = [
            "shop", "store", "buy", "sell", "market", "trade", "business", "company",
            "service", "tech", "digital", "online", "web", "app", "mobile", "cloud",
            "finance", "money", "bank", "invest", "crypto", "health", "medical",
            "travel", "hotel", "food", "restaurant", "fashion", "beauty", "sport",
            "game", "music", "video", "photo", "news", "blog", "social", "network"
        ]
        
        domain_lower = domain.lower()
        has_commercial_keyword = any(keyword in domain_lower for keyword in commercial_keywords)
        
        # Calcul du score
        score = 0
        
        # Longueur (plus court = mieux)
        if length <= 4:
            score += 30
        elif length <= 6:
            score += 20
        elif length <= 8:
            score += 10
        
        # TLD premium
        if tld in ["com", "net", "org"]:
            score += 25
        elif tld in ["fr", "de", "uk", "ca"]:
            score += 15
        
        # Pas de tirets ni de chiffres
        if not has_hyphens:
            score += 15
        if not has_numbers:
            score += 10
        
        # Mots-clés commerciaux
        if has_commercial_keyword:
            score += 20
        
        # Classification
        if score >= 70:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
    
    def _categorize_domain(self, domain: str) -> str:
        """Catégorise un domaine selon son contenu"""
        domain_lower = domain.lower()
        
        # Catégories par mots-clés
        categories = {
            "technology": ["tech", "digital", "app", "web", "software", "code", "dev", "ai", "data", "cloud"],
            "business": ["business", "company", "corp", "enterprise", "trade", "market", "shop", "store"],
            "finance": ["finance", "money", "bank", "invest", "crypto", "pay", "wallet", "loan"],
            "health": ["health", "medical", "doctor", "clinic", "pharmacy", "wellness", "fitness"],
            "travel": ["travel", "hotel", "flight", "vacation", "tour", "trip", "booking"],
            "food": ["food", "restaurant", "cafe", "kitchen", "recipe", "cook", "eat"],
            "fashion": ["fashion", "style", "clothes", "dress", "beauty", "cosmetic"],
            "entertainment": ["game", "music", "video", "movie", "tv", "show", "entertainment"],
            "education": ["education", "school", "learn", "course", "study", "university"],
            "news": ["news", "blog", "media", "press", "journal", "magazine"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in domain_lower for keyword in keywords):
                return category
        
        # Vérification des patterns numériques/géographiques
        if any(c.isdigit() for c in domain):
            return "numeric"
        
        # Par défaut
        return "generic"
    
    def _generate_expired_reveal_recommendations(self, revealed_domains: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des domaines expirés révélés"""
        recommendations = []
        
        if not revealed_domains:
            return ["Aucun domaine révélé, vérifiez les clés fournies"]
        
        # Analyse du taux de succès
        success_rate = float(stats.get("success_rate", "0%").replace("%", ""))
        if success_rate < 50:
            recommendations.append(f"⚠️ Taux de révélation faible ({success_rate:.1f}%), certaines clés peuvent être invalides")
        elif success_rate == 100:
            recommendations.append("🎯 Toutes les clés ont été révélées avec succès")
        
        # Analyse de la qualité
        high_value_count = stats.get("quality_metrics", {}).get("high_value_count", 0)
        premium_count = stats.get("quality_metrics", {}).get("premium_count", 0)
        
        if high_value_count > 0:
            recommendations.append(f"💎 {high_value_count} domaine(s) à fort potentiel identifié(s)")
        
        if premium_count > 0:
            recommendations.append(f"🏆 {premium_count} domaine(s) premium (court, sans tiret/chiffre)")
        
        # Analyse des TLD
        tld_dist = stats.get("tld_distribution", {})
        if "com" in tld_dist:
            recommendations.append(f"🌟 {tld_dist['com']} domaine(s) .com trouvé(s) - TLD premium")
        
        # Analyse des catégories
        category_dist = stats.get("category_distribution", {})
        if category_dist:
            top_category = max(category_dist.items(), key=lambda x: x[1])
            recommendations.append(f"📊 Catégorie dominante: {top_category[0]} ({top_category[1]} domaines)")
        
        # Recommandations sur la longueur
        avg_length = stats.get("quality_metrics", {}).get("average_length", 0)
        if avg_length <= 6:
            recommendations.append("✨ Longueur moyenne excellente, domaines faciles à retenir")
        elif avg_length > 12:
            recommendations.append("📏 Domaines longs en moyenne, privilégiez les plus courts")
        
        # Analyse des défauts
        with_hyphens = stats.get("quality_metrics", {}).get("with_hyphens", 0)
        with_numbers = stats.get("quality_metrics", {}).get("with_numbers", 0)
        
        if with_hyphens > len(revealed_domains) * 0.3:
            recommendations.append("⚠️ Beaucoup de domaines avec tirets, impact sur la mémorisation")
        
        if with_numbers > len(revealed_domains) * 0.3:
            recommendations.append("🔢 Beaucoup de domaines avec chiffres, moins premium")
        
        # Recommandation générale
        if len(revealed_domains) > 10:
            recommendations.append("🔍 Analysez en détail les domaines à fort potentiel pour opportunités")
        
        return recommendations if recommendations else ["📊 Révélation terminée, consultez les domaines obtenus"]
