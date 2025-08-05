#!/usr/bin/env python3
"""
Point d'entrée principal pour le serveur MCP Haloscan
Délègue l'exécution au serveur dans app/ (structure FastAPI standard)
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path Python pour importer app
root_path = Path(__file__).parent
sys.path.insert(0, str(root_path))

# Importer et lancer le serveur principal
from app.main import main as server_main

if __name__ == "__main__":
    server_main()
