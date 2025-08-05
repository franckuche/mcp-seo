#!/usr/bin/env python3
"""
Tests pour le serveur MCP Haloscan
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au path Python
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import asyncio
import pytest
from config import Config

def test_config_validation():
    """Test de validation de la configuration"""
    try:
        Config.validate()
        print("✅ Configuration valide")
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

async def test_haloscan_connection():
    """Test de connexion à l'API Haloscan"""
    try:
        from main import haloscan
        result = await haloscan.request("user/credit")
        print("✅ Connexion Haloscan OK")
        print(f"📊 Crédits disponibles: {result['totalCredit']['creditKeyword']}")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion Haloscan: {e}")
        return False

def test_server_import():
    """Test d'importation du serveur principal"""
    try:
        from main import app
        print("✅ Serveur importé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur d'importation: {e}")
        return False

async def main():
    """Fonction principale de test"""
    print("🧪 Tests du serveur MCP Haloscan\n")
    
    tests = [
        ("Configuration", test_config_validation),
        ("Importation serveur", test_server_import),
        ("Connexion Haloscan", test_haloscan_connection),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"🔍 Test: {name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur dans {name}: {e}")
            results.append(False)
        print()
    
    # Résumé
    passed = sum(results)
    total = len(results)
    
    print(f"📋 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés !")
        return 0
    else:
        print("⚠️ Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
