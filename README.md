# 🚀 MCP Haloscan Server avec Chunking Intelligent

Serveur MCP (Model Context Protocol) moderne avec **Chunking Intelligent** pour analyses SEO complètes sans limite de tokens. Interface web professionnelle + intégration Claude Desktop.

## ✨ **NOUVEAUTÉS MAJEURES**

### 🧠 **Chunking Intelligent**
- **Analyses SEO illimitées** : Contourne les limites de tokens OpenAI
- **Traitement séquentiel** : Découpe automatique des données en chunks
- **Synthèse finale** : Combine tous les résultats en une analyse complète
- **Optimisation tokens** : Prompts optimisés pour maximiser les données utiles

### 🎯 **Interface Plein Écran Professionnelle**
- **Design moderne** : Interface chat occupant 100% de l'écran
- **Progression en temps réel** : Barre de progression + timer + étapes détaillées
- **Textarea extensible** : Auto-resize pour prompts longs (Ctrl+Entrée)
- **Exemples pré-configurés** : Prompts chunked prêts à l'emploi

### 📊 **Récupération de Données Étendue**
- **Positions 1-50** : Analyse complète pages 1-5 (au lieu de 1-20)
- **Limite augmentée** : 200 résultats par appel API (au lieu de 50)
- **3 tranches d'analyse** : Pages 1, 2, et 3+ pour couverture maximale

## 📋 Table des Matières

- [🚀 Installation Rapide](#-installation-rapide)
- [⚙️ Configuration](#️-configuration)
- [🎯 Utilisation](#-utilisation)
- [🧠 Chunking Intelligent](#-chunking-intelligent)
- [🛠️ Outils Disponibles](#️-outils-disponibles)
- [📁 Structure du Projet](#-structure-du-projet)
- [🔒 Sécurité](#-sécurité)
- [🐛 Dépannage](#-dépannage)

## 🚀 Installation Rapide

### Prérequis
- Python 3.8+
- Clé API Haloscan valide ([Obtenir une clé](https://haloscan.com/api))
- Claude Desktop (pour l'utilisation MCP)

### Installation Automatique
```bash
# 1. Naviguer vers le projet
cd votre-projet-mcp-haloscan

# 2. Lancer le script d'installation
./scripts/setup.sh

# 3. Éditer la configuration
nano config/.env
# Remplacer HALOSCAN_API_KEY=your_key par votre vraie clé
```

### Installation Manuelle
```bash
# 1. Naviguer vers le projet
cd votre-projet-mcp-haloscan

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate.bat  # Windows

# 3. Installer les dépendances
pip install -r config/requirements.txt

# 4. Configuration
cp config/.env.example config/.env
# Éditer config/.env avec votre clé API Haloscan
```

### Test de Fonctionnement
```bash
# Test de la configuration
python -c "from config import Config; Config.validate(); print('✅ Configuration OK')"

# Test du serveur (mode web)
python main.py

# Test du serveur (mode MCP)
python main.py mcp
```

## ⚙️ Configuration

### Variables d'Environnement (config/.env)
```bash
# === HALOSCAN API ===
HALOSCAN_API_KEY=votre_cle_api_ici
HALOSCAN_BASE_URL=https://api.haloscan.com/api

# === SERVEUR ===
HOST=localhost
PORT=8000
ENVIRONMENT=development  # ou production

# === LOGS ===
LOG_LEVEL=INFO

# === MCP ===
MCP_SERVER_NAME=Haloscan SEO Tools
MCP_SERVER_VERSION=1.0.0
```

### Configuration Claude Desktop

Copier le fichier de configuration :
```bash
cp config/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json  # macOS
# ou
cp config/claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json  # Windows
```

Ou ajouter manuellement dans `claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "haloscan": {
      "command": "python",
      "args": ["/chemin/vers/votre/projet/main.py", "mcp"],
      "env": {
        "HALOSCAN_API_KEY": "votre_cle_api_ici"
      }
    }
  }
}
```

**Emplacements du fichier :**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## 🎯 Utilisation

### 🧠 Interface Chunked (Recommandée)
```bash
# Lancer l'interface web
python main.py

# Accès à l'interface chunked :
# 🧠 Chat Chunked: http://localhost:8080/chat-chunked
# 🌐 Interface normale: http://localhost:8080/
# 📚 Documentation API: http://localhost:8080/docs
# ❤️ Santé du serveur: http://localhost:8080/health
```

### Mode MCP (Claude Desktop)
```bash
# Lancer le serveur MCP
python main.py mcp

# Le serveur se connecte automatiquement à Claude Desktop
# Utilisez les outils directement dans vos conversations Claude
```

## 🧠 Chunking Intelligent

### 🎯 Qu'est-ce que le Chunking Intelligent ?

Le **Chunking Intelligent** résout le problème des **limites de tokens OpenAI** pour les analyses SEO complètes :

- **Problème** : OpenAI limite à ~4000 tokens par réponse
- **Conséquence** : Analyses tronquées, données incomplètes
- **Solution** : Découpage intelligent + synthèse finale

### 📊 Comment ça fonctionne ?

```
1. 📊 Analyse du domaine (3s)
2. 🏢 Identification des concurrents (4s)
3. 🔍 Analyse mots-clés page 2 (11-20) (8s)
4. 📈 Analyse mots-clés page 1 (1-10) (6s)
5. 📊 Analyse mots-clés page 3+ (21-50) (10s)
6. 🧠 Synthèse finale (max 8000 tokens) (15s)
```

**Total : ~46 secondes pour une analyse complète**

### 🚀 Avantages du Chunking

- **✨ Analyses illimitées** : Plus de limite de tokens
- **📊 Données maximisées** : 200 résultats par appel (vs 50)
- **🎯 Couverture étendue** : Positions 1-50 (vs 1-20)
- **📈 Progression visuelle** : Timer + barre + étapes
- **📝 Format optimisé** : Tableaux Markdown sans blabla

### 📋 Exemples de Prompts Chunked

#### 🧠 Analyse des Gaps SEO
```
ANALYSE SEO CHUNKED: https://ads-up.fr/
MISSION: Identifier les mots-clés où ads-up.fr NE SE POSITIONNE PAS 
mais où la plupart de ses concurrents sont bien positionnés (pages 1-3).

FORMAT OBLIGATOIRE - RÉPONSE DIRECTE SANS BLABLA:
| keyword | volume | difficulty | competition | cpc | trend | thematic_cluster | sous_thematique | intention_type |

INSTRUCTIONS CRITIQUES:
- FOCUS: mots-clés où ads-up.fr est ABSENT (pas de position)
- CONDITION: concurrents positionnés pages 1-3 sur ces mots-clés
- INCLURE: TOUS les gaps SEO trouvés (pas de limite)
- PRIORITÉ: mots-clés à fort potentiel commercial
```

#### 📊 Analyse Concurrentielle Complète
```
ANALYSE SEO CHUNKED: https://lemonde.fr/
MISSION: Rapport détaillé avec analyse exhaustive des mots-clés et concurrents.

FORMAT: Tableau avec TOUS les mots-clés trouvés
FOCUS: Positions 11-50 où les concurrents sont mieux classés
```

### 📈 Résultats Attendus

Avec le chunking, vous obtenez :

```markdown
| keyword | volume | difficulty | competition | cpc | trend | thematic_cluster | sous_thematique | intention_type |
|---------|--------|------------|-------------|-----|-------|------------------|-----------------|-------------------|
| agence sea | 1200 | 0.65 | 0.78 | 3.45 | Croissant | Marketing Digital | SEA | Commerciale |
| consultant adwords | 890 | 0.58 | 0.72 | 4.20 | Stable | Marketing Digital | Google Ads | Commerciale |
| formation google ads | 3200 | 0.45 | 0.62 | 2.90 | Croissant | Formation | SEA | Informationnelle |
... (TOUS les autres mots-clés - potentiellement 100-200+)
```

**Au lieu de seulement 20 mots-clés tronqués ! 🎉**

### Exemples d'Utilisation dans Claude

```
Analyse le mot-clé "SEO" avec toutes les métriques disponibles

Trouve les concurrents organiques de "example.com"

Récupère les questions fréquentes liées au mot-clé "marketing digital"

Analyse en bulk les mots-clés : "SEO, référencement, marketing"
```

## 🛠️ Outils Disponibles

### 🔑 Outils Utilisateur
- **`get_user_credit`** - Vérification des crédits Haloscan disponibles

### 📊 Outils Mots-clés (5 outils)
- **`analyze_keyword`** - Analyse complète d'un mot-clé (volume, concurrence, SERP, mots-clés associés)
- **`search_keywords`** - Recherche de mots-clés par correspondance exacte
- **`get_similar_keywords`** - Mots-clés sémantiquement similaires
- **`get_keyword_questions`** - Questions fréquentes liées au mot-clé
- **`analyze_keywords_bulk`** - Analyse groupée de plusieurs mots-clés

### 🌐 Outils Domaines (4 outils)
- **`analyze_domain`** - Analyse SEO complète d'un domaine (trafic, visibilité, pages performantes)
- **`get_domain_competitors`** - Identification des concurrents organiques
- **`get_domain_top_pages`** - Pages les plus performantes du domaine
- **`analyze_domains_bulk`** - Analyse groupée de plusieurs domaines

### 🎯 Fonctionnalités Techniques
- **Architecture unifiée** : FastAPI + MCP automatique avec FastMCP
- **Validation Pydantic** : Validation automatique des paramètres d'entrée
- **Gestion d'erreurs robuste** : Messages d'erreur clairs et informatifs
- **Monitoring intégré** : Endpoint de santé et métriques de performance
- **Support bulk** : Analyse de masse optimisée pour économiser les crédits API
- **Timeout configuré** : 30 secondes par requête pour éviter les blocages

## 📁 Structure du Projet

```
mcp-haloscan-server/
├── 📄 main.py                    # Point d'entrée principal (délègue à app/)
├── 📖 README.md                  # Cette documentation
├── 🚫 .gitignore                 # Fichiers à ignorer par Git
│
├── 📁 app/                       # Package principal (standard FastAPI)
│   ├── 📄 __init__.py            # Package Python
│   ├── 📄 main.py                # Application FastAPI principale
│   ├── 🔧 config.py              # Configuration centralisée
│   ├── 🔗 dependencies.py        # Dépendances communes (client Haloscan)
│   ├── 📋 models.py              # Modèles Pydantic
│   └── 📁 routers/               # Routes modulaires
│       ├── 📄 __init__.py        # Package routers
│       ├── ❤️ health.py          # Routes de santé/monitoring
│       ├── 👤 user.py            # Routes utilisateur
│       ├── 🔤 keywords.py        # Routes mots-clés
│       └── 🌐 domains.py         # Routes domaines
│
├── 📁 config/                    # Configuration et dépendances
│   ├── 🔐 .env                   # Variables d'environnement (non versionné)
│   ├── 📝 .env.example           # Template de configuration
│   ├── ⚙️ claude_desktop_config.json # Configuration Claude Desktop
│   ├── 📦 requirements.txt       # Dépendances Python
│   ├── 📦 package.json           # Métadonnées Node.js (optionnel)
│   └── 📦 pyproject.toml         # Configuration Python moderne
│
├── 📁 tests/                     # Tests automatisés
│   └── 🧪 test_server.py         # Tests du serveur
│
├── 📁 scripts/                   # Scripts utilitaires
│   └── 🚀 setup.sh               # Script d'installation automatique
│
├── 📁 docs/                      # Documentation supplémentaire (vide)
└── 📁 venv/                      # Environnement virtuel Python
```

### Fichiers Principaux
- **`main.py`** : Point d'entrée principal (délègue à app/main.py)
- **`app/main.py`** : Application FastAPI principale avec cycle de vie
- **`app/config.py`** : Gestion centralisée de la configuration avec validation
- **`app/models.py`** : Modèles Pydantic pour validation des données
- **`app/dependencies.py`** : Client Haloscan et dépendances communes
- **`app/routers/`** : Routes modulaires par fonctionnalité
- **`config/requirements.txt`** : Dépendances avec versions compatibles
- **`config/.env`** : Variables d'environnement (clé API, etc.)
- **`scripts/setup.sh`** : Script d'installation automatique
- **`tests/test_server.py`** : Tests automatisés du serveur

### Architecture Technique

**Point d'entrée (`main.py`)** :
- Délègue l'exécution au serveur dans `app/main.py`
- Gère le path Python pour importer le package `app`
- Interface simple et claire

**Application FastAPI (`app/main.py`)** :
- **Architecture modulaire** conforme aux standards FastAPI
- **Cycle de vie** avec validation de configuration au démarrage
- **Inclusion des routers** modulaires (health, user, keywords, domains)
- **FastMCP** pour génération automatique du serveur MCP
- **Dual-mode** : Web (test/debug) et MCP (production)

**Modèles (`app/models.py`)** :
- **Modèles Pydantic** pour validation automatique des données
- `KeywordRequest`, `DomainRequest`, `BulkRequest`
- `HealthResponse` pour les réponses de santé
- Types stricts et validation d'entrée

**Dépendances (`app/dependencies.py`)** :
- **Client Haloscan optimisé** avec timeout et gestion d'erreurs
- Instance globale réutilisable
- Méthode unifiée pour toutes les requêtes API

**Routes modulaires (`app/routers/`)** :
- **`health.py`** : Monitoring et vérification de santé
- **`user.py`** : Gestion des crédits utilisateur
- **`keywords.py`** : Toutes les fonctionnalités mots-clés
- **`domains.py`** : Toutes les fonctionnalités domaines
- Séparation claire des responsabilités

**Configuration (`app/config.py`)** :
- Chargement automatique des variables d'environnement depuis `config/.env`
- Validation stricte au démarrage
- Messages d'erreur explicites
- Support développement/production

**Installation (`scripts/setup.sh`)** :
- Installation automatique de l'environnement virtuel
- Installation des dépendances
- Copie du template de configuration
- Instructions post-installation

**Tests (`tests/test_server.py`)** :
- Validation de la configuration
- Test de connexion Haloscan
- Test d'importation du serveur
- Rapport de résultats détaillé

## 🔒 Sécurité

### Protection de la Clé API
```bash
# ✅ Bonnes pratiques
export HALOSCAN_API_KEY="votre_cle"  # Variable d'environnement
# ou dans .env (non versionné)

# ❌ À éviter
# Jamais de clé API directement dans le code
# Jamais de commit de fichiers .env
```

### Validation de Configuration
- **Vérification au démarrage** : Clé API présente et valide
- **Test de connectivité** : Vérification de l'accès à l'API Haloscan
- **Validation des paramètres** : Pydantic valide tous les inputs
- **Gestion des erreurs** : Messages sécurisés sans fuite d'informations

### Bonnes Pratiques
- Utilisation d'un environnement virtuel isolé
- Timeout configuré pour éviter les blocages
- Logs structurés sans informations sensibles
- Variables d'environnement pour la configuration

## 🐛 Dépannage

### Problèmes Courants

#### ❌ "ModuleNotFoundError: No module named 'fastmcp'"
```bash
# Solution : Activer l'environnement virtuel
source venv/bin/activate
pip install -r requirements.txt
```

#### ❌ "HALOSCAN_API_KEY manquante ou invalide"
```bash
# Solution : Vérifier le fichier de configuration
cat config/.env | grep HALOSCAN_API_KEY
# Ou définir la variable d'environnement
export HALOSCAN_API_KEY="votre_cle_ici"
```

#### ❌ Claude Desktop ne voit pas le serveur
```bash
# 1. Vérifier le chemin dans claude_desktop_config.json
# 2. Tester le serveur manuellement
python main.py mcp

# 3. Vérifier les logs Claude Desktop
# macOS: ~/Library/Logs/Claude/
```

#### ❌ Erreur de connexion Haloscan
```bash
# Test de connectivité
curl -H "haloscan-api-key: VOTRE_CLE" https://api.haloscan.com/api/user/credit

# Vérifier l'endpoint de santé
curl http://localhost:8000/health
```

### Tests et Debug

#### Mode Développement
```bash
# Activer les logs détaillés
export LOG_LEVEL=DEBUG
export ENVIRONMENT=development
python main.py
```

#### Test de Santé Complet
```bash
# Vérification complète du serveur
curl http://localhost:8000/health

# Réponse attendue :
{
  "status": "healthy",
  "haloscan_connected": true,
  "credits": {
    "keywords": 1000,
    "sites": 500,
    "exports": 100
  },
  "server_version": "1.0.0"
}
```

#### Test des Outils MCP
```bash
# Test de configuration
python -c "from config import Config; Config.validate()"

# Test de connectivité Haloscan
python -c "import asyncio; from main import haloscan; print(asyncio.run(haloscan.request('user/credit')))"
```

### Commandes Utiles

```bash
# Démarrage rapide
python main.py                    # Mode web (développement)
python main.py mcp                # Mode MCP (production)

# Tests
python tests/test_server.py       # Test complet du serveur
python -m py_compile app/main.py  # Vérification syntaxe

# Debug
export LOG_LEVEL=DEBUG && python main.py  # Logs détaillés
curl http://localhost:8000/docs            # Documentation API
curl http://localhost:8000/health          # Santé du serveur

# Installation
./scripts/setup.sh                # Installation automatique
```

## 📚 Ressources

- **Documentation Haloscan** : [https://haloscan.com/api](https://haloscan.com/api)
- **MCP Specification** : [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- **FastMCP Documentation** : [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **Claude Desktop** : [https://claude.ai/desktop](https://claude.ai/desktop)

---

**🎉 Votre serveur MCP Haloscan est maintenant prêt !**

Pour toute question, consultez la section dépannage ou testez les commandes de debug ci-dessus.
