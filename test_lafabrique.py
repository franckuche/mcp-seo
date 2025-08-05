#!/usr/bin/env python3
"""
Test final avec lafabriquedunet.fr pour votre cas d'usage business
"""
import asyncio
import httpx
import json

async def test_lafabrique_business():
    """Test avec lafabriquedunet.fr pour l'analyse business"""
    
    print("🎯 Test final : Analyse business pour lafabriquedunet.fr...")
    
    # Votre demande originale
    test_data = {
        "message": "Je travaille pour lafabriquedunet.fr, j'aimerais augmenter le business via le SEO donc j'aimerais que tu me trouves parmi les keywords où le site est en page 2 les meilleurs keywords business selon toi, tu peux te baser sur le CPC",
        "conversation_history": []
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("📡 Envoi de la requête business...")
            
            response = await client.post(
                "http://localhost:8080/api/chat",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Succès !")
                print(f"📝 Réponse complète:")
                print(f"{result.get('response', 'N/A')}")
                print(f"\n🔧 Outils utilisés: {len(result.get('tools_used', []))}")
                
                for tool in result.get('tools_used', []):
                    print(f"  - {tool.get('tool')}: {'✅' if tool.get('success') else '❌'}")
                    if tool.get('success') and 'data' in tool:
                        data = tool['data']
                        if isinstance(data, dict) and 'keywords_found' in data:
                            print(f"    📊 Mots-clés trouvés: {data['keywords_found']}")
                            if data.get('top_keywords'):
                                print("    💰 Top mots-clés business (par CPC):")
                                # Trier par CPC pour l'analyse business
                                business_keywords = sorted(
                                    data.get('top_keywords', []), 
                                    key=lambda x: float(x.get('cpc', 0)) if x.get('cpc') != 'N/A' else 0, 
                                    reverse=True
                                )
                                for i, kw in enumerate(business_keywords[:5]):
                                    if isinstance(kw, dict):
                                        keyword_name = kw.get('keyword', 'N/A')
                                        position = kw.get('position', 'N/A')
                                        traffic = kw.get('traffic', 0)
                                        cpc = kw.get('cpc', 0)
                                        volume = kw.get('volume', 0)
                                        print(f"      {i+1}. '{keyword_name}' - Pos: {position}, CPC: {cpc}€, Trafic: {traffic}, Volume: {volume}")
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
    asyncio.run(test_lafabrique_business())
