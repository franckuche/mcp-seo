"""
Dépendances communes pour l'API Haloscan
"""

import httpx
from .config import Config


class HaloscanClient:
    """Client HTTP optimisé pour l'API Haloscan"""
    
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "haloscan-api-key": Config.HALOSCAN_API_KEY
        }
        self.base_url = Config.HALOSCAN_BASE_URL
    
    async def request(self, endpoint: str, data: dict = None) -> dict:
        """Méthode unifiée pour toutes les requêtes"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/{endpoint}"
            
            if data is None:
                response = await client.get(url, headers=self.headers)
            else:
                response = await client.post(url, headers=self.headers, json=data)
            
            response.raise_for_status()
            return response.json()


    # Méthodes spécifiques pour l'API Haloscan
    async def get_user_credit(self) -> dict:
        """Récupère les crédits utilisateur"""
        return await self.request("user/credit")
    
    async def get_keywords_overview(self, keyword: str, lang: str = "fr") -> dict:
        """Analyse d'un mot-clé"""
        return await self.request("keywords/overview", {"keyword": keyword, "lang": lang})
    
    async def get_keywords_similar(self, keyword: str, lang: str = "fr") -> dict:
        """Mots-clés similaires"""
        return await self.request("keywords/similar", {"keyword": keyword, "lang": lang})
    
    async def get_keywords_questions(self, keyword: str, lang: str = "fr") -> dict:
        """Questions liées au mot-clé"""
        return await self.request("keywords/questions", {"keyword": keyword, "lang": lang})
    
    async def get_domains_overview(self, domain: str, lang: str = "fr") -> dict:
        """Analyse d'un domaine"""
        return await self.request("domains/overview", {"domain": domain, "lang": lang})
    
    async def get_domains_competitors(self, domain: str) -> dict:
        """Concurrents d'un domaine"""
        return await self.request("domains/competitors", {"domain": domain})
    
    async def get_domains_top_pages(self, domain: str) -> dict:
        """Top pages d'un domaine"""
        return await self.request("domains/top-pages", {"domain": domain})


# Instance globale du client Haloscan
haloscan_client = HaloscanClient()


def get_haloscan_client() -> HaloscanClient:
    """Fonction de dépendance pour obtenir le client Haloscan"""
    return haloscan_client
