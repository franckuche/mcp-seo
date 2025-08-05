"""
Application FastAPI principale pour le serveur MCP Haloscan
Architecture modulaire conforme aux standards FastAPI
"""

import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastmcp import FastMCP
from .config import Config
from .logging_config import setup_logging, get_logger
from .routers import health, keywords, domains, user, frontend, advanced

# Initialisation du logging
setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage
    logger.info("🚀 Démarrage du serveur MCP Haloscan...")
    print("🚀 Démarrage du serveur MCP Haloscan...")
    
    try:
        # Validation de la configuration
        logger.info("🔧 Validation de la configuration...")
        Config.validate()
        logger.info("✅ Configuration validée")
        print("✅ Configuration validée")
        
        # Test de connexion Haloscan (optionnel)
        logger.info("🔗 Test de connexion Haloscan...")
        try:
            from .dependencies import haloscan_client
            await haloscan_client.request("user/credit")
            logger.info("✅ Connexion Haloscan OK")
            print("✅ Connexion Haloscan OK")
        except Exception as e:
            logger.error(f"⚠️  Attention: Connexion Haloscan échouée - {e}")
            print(f"⚠️  Attention: Connexion Haloscan échouée - {e}")
        
        logger.info("🎯 Serveur prêt à recevoir des requêtes")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        print(f"❌ Erreur lors de l'initialisation: {e}")
        raise
    
    yield
    print("🛑 Arrêt du serveur")


# Application FastAPI avec cycle de vie
app = FastAPI(
    title="MCP Haloscan Server",
    description="Serveur MCP optimisé pour l'API Haloscan SEO - Architecture modulaire",
    version=Config.MCP_SERVER_VERSION,
    lifespan=lifespan
)

# Inclusion des routers modulaires
app.include_router(frontend.router, tags=["frontend"])  # Interface graphique sur /
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
app.include_router(domains.router, prefix="/domains", tags=["domains"])
app.include_router(advanced.router, prefix="/advanced", tags=["advanced"])

# 🤖 NOUVEAU : Router Chat MCP avec OpenAI + Haloscan
from .routers import chat, chat_chunked
app.include_router(chat.router, prefix="/api", tags=["chat-mcp"])
app.include_router(chat_chunked.router, prefix="/api", tags=["chat-chunked"])

# Génération automatique du serveur MCP depuis FastAPI
mcp = FastMCP.from_fastapi(
    app=app,
    name=Config.MCP_SERVER_NAME
)


def main():
    """Point d'entrée principal avec support dual-mode"""
    import uvicorn
    
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        # Mode MCP pour Claude Desktop
        print("🤖 Mode MCP - Connexion avec Claude Desktop...")
        mcp.run()
    else:
        # Mode web FastAPI par défaut
        print("🌐 Mode Web - Interface de test et debug")
        print(f"📍 Serveur: http://{Config.HOST}:{Config.PORT}")
        print(f"📚 Documentation: http://{Config.HOST}:{Config.PORT}/docs")
        print(f"❤️  Santé: http://{Config.HOST}:{Config.PORT}/health")
        
        uvicorn.run(
            "app.main:app",
            host=Config.HOST,
            port=Config.PORT,
            reload=Config.ENVIRONMENT == "development",
            log_level=Config.LOG_LEVEL.lower()
        )


if __name__ == "__main__":
    main()
