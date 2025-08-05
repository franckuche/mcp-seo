#!/bin/bash
"""
Script d'installation automatique pour MCP Haloscan Server
"""

set -e

echo "🚀 Installation du serveur MCP Haloscan..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Python 3 détecté"

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r config/requirements.txt

# Copier le fichier de configuration
if [ ! -f "config/.env" ]; then
    echo "⚙️ Création du fichier de configuration..."
    cp config/.env.example config/.env
    echo "📝 Éditez config/.env avec votre clé API Haloscan"
else
    echo "✅ Fichier de configuration existant trouvé"
fi

echo ""
echo "🎉 Installation terminée !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Éditez config/.env avec votre clé API Haloscan"
echo "2. Testez avec : python main.py"
echo "3. Pour Claude Desktop : python main.py mcp"
echo ""
