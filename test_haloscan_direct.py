#!/usr/bin/env python3
"""
Test direct de l'API Haloscan pour diagnostiquer le problème
"""
import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv("config/.env")

async def test_haloscan_api():
    """Test direct de l'API Haloscan"""
    
    api_key = os.getenv("HALOSCAN_API_KEY")
    base_url = os.getenv("HALOSCAN_BASE_URL", "https://api.haloscan.com/api")
    
    print("🧪 Test direct de l'API Haloscan...")
    print(f"🔑 Clé API: {'✅ Configurée' if api_key else '❌ Manquante'}")
    print(f"🌐 Base URL: {base_url}")
    
    if not api_key:
        print("❌ Clé API manquante dans config/.env")
        return
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "haloscan-api-key": api_key
    }
    
    # Tests des différents endpoints
    test_cases = [
        {
            "name": "User Credit",
            "endpoint": "user/credit",
            "method": "GET",
            "data": None
        },
        {
            "name": "Domain Overview - lemonde.fr",
            "endpoint": "domains/overview",
            "method": "POST",
            "data": {"domain": "lemonde.fr", "lang": "fr"}
        },
        {
            "name": "Domain Overview - example.com",
            "endpoint": "domains/overview", 
            "method": "POST",
            "data": {"domain": "example.com", "lang": "fr"}
        },
        {
            "name": "Keyword Overview - marketing",
            "endpoint": "keywords/overview",
            "method": "POST", 
            "data": {"keyword": "marketing", "lang": "fr"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🔍 Test: {test['name']}")
            print(f"📡 {test['method']} {base_url}/{test['endpoint']}")
            
            try:
                if test['method'] == 'GET':
                    response = await client.get(
                        f"{base_url}/{test['endpoint']}", 
                        headers=headers
                    )
                else:
                    response = await client.post(
                        f"{base_url}/{test['endpoint']}", 
                        headers=headers,
                        json=test['data']
                    )
                
                print(f"📊 Status: {response.status_code}")
                print(f"📋 Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        print(f"✅ Succès - Taille: {len(str(result))} caractères")
                        print(f"📄 Structure: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                        
                        # Afficher un aperçu du contenu
                        if isinstance(result, dict):
                            if 'errors' in result and result['errors']:
                                print(f"⚠️ Erreurs: {result['errors']}")
                            elif 'data' in result:
                                print(f"📊 Données disponibles: {type(result['data'])}")
                            elif len(result) > 0:
                                print(f"📋 Aperçu: {str(result)[:200]}...")
                        
                    except json.JSONDecodeError:
                        print(f"❌ Réponse non-JSON: {response.text[:200]}...")
                else:
                    print(f"❌ Erreur HTTP {response.status_code}")
                    print(f"📄 Contenu: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"💥 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_haloscan_api())
