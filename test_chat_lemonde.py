#!/usr/bin/env python3
"""
Script de test pour l'endpoint chat MCP avec un domaine connu
"""
import asyncio
import httpx
import json

async def test_chat_with_known_domain():
    """Test avec lemonde.fr qui devrait avoir des données SEO"""
    
    print("🧪 Test de l'endpoint chat MCP avec lemonde.fr...")
    
    # Données de test avec un domaine connu
    test_data = {
        "message": "Trouve les mots-clés de lemonde.fr en page 2 (positions 11-20) et analyse leur potentiel business selon le CPC",
        "conversation_history": []
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("📡 Envoi de la requête...")
            
            response = await client.post(
                "http://localhost:8080/api/chat",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Succès !")
                print(f"📝 Réponse: {result.get('response', 'N/A')[:300]}...")
                print(f"🔧 Outils utilisés: {len(result.get('tools_used', []))}")
                
                for tool in result.get('tools_used', []):
                    print(f"  - {tool.get('tool')}: {'✅' if tool.get('success') else '❌'}")
                    if tool.get('success') and 'data' in tool:
                        data = tool['data']
                        if isinstance(data, dict) and 'keywords_found' in data:
                            print(f"    📊 Mots-clés trouvés: {data['keywords_found']}")
                            if data['keywords_found'] > 0:
                                print("    🎯 Premiers mots-clés:")
                                for i, kw in enumerate(data.get('keywords', [])[:3]):
                                    if isinstance(kw, dict):
                                        keyword_name = kw.get('keyword', kw.get('term', 'N/A'))
                                        position = kw.get('position', kw.get('pos', 'N/A'))
                                        print(f"      {i+1}. {keyword_name} (pos: {position})")
                    if not tool.get('success'):
                        print(f"    ❌ Erreur: {tool.get('error')}")
            else:
                print("❌ Erreur !")
                print(f"📄 Contenu: {response.text}")
                
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_with_known_domain())
