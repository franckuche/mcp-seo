#!/usr/bin/env python3
"""
Script de test pour l'endpoint chat MCP
"""
import asyncio
import httpx
import json

async def test_chat():
    """Test simple de l'endpoint chat"""
    
    print("🧪 Test de l'endpoint chat MCP...")
    
    # Données de test
    test_data = {
        "message": "Trouve les mots-clés de lafabriquedunet.fr en page 2",
        "conversation_history": []
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("📡 Envoi de la requête...")
            
            response = await client.post(
                "http://localhost:8080/api/chat",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Status code: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Succès !")
                print(f"📝 Réponse: {result.get('response', 'N/A')[:200]}...")
                print(f"🔧 Outils utilisés: {len(result.get('tools_used', []))}")
                
                for tool in result.get('tools_used', []):
                    print(f"  - {tool.get('tool')}: {'✅' if tool.get('success') else '❌'}")
                    if not tool.get('success'):
                        print(f"    Erreur: {tool.get('error')}")
            else:
                print("❌ Erreur !")
                print(f"📄 Contenu: {response.text}")
                
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat())
