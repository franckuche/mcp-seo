import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Chargement automatique du fichier .env depuis config/
config_dir = Path(__file__).parent.parent / "config"
env_path = config_dir / ".env"
load_dotenv(env_path)

class Config:
    """Configuration centralisée et sécurisée pour le serveur MCP Haloscan"""
    
    # === HALOSCAN API ===
    HALOSCAN_API_KEY: str = os.getenv("HALOSCAN_API_KEY", "")
    HALOSCAN_BASE_URL: str = os.getenv("HALOSCAN_BASE_URL", "https://api.haloscan.com/api")
    
    # === OPENAI API ===
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # === SERVEUR ===
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "localhost")
    
    # === SÉCURITÉ ===
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    
    # === LOGS ===
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # === MCP ===
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "Haloscan SEO Tools")
    MCP_SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    
    @classmethod
    def validate(cls) -> None:
        """Valide la configuration et lève des erreurs explicites si invalide"""
        errors = []
        
        # Validation de la clé API Haloscan
        if not cls.HALOSCAN_API_KEY or cls.HALOSCAN_API_KEY == "your_haloscan_api_key_here":
            errors.append(
                "❌ HALOSCAN_API_KEY manquante ou invalide.\n"
                "   → Configurez votre vraie clé API dans le fichier .env\n"
                "   → Obtenez votre clé sur: https://haloscan.com/api"
            )
        
        # Validation du port
        if not (1 <= cls.PORT <= 65535):
            errors.append(f"❌ PORT invalide: {cls.PORT}. Doit être entre 1 et 65535.")
        
        # Validation de l'environnement
        if cls.ENVIRONMENT not in ["development", "production"]:
            errors.append(f"❌ ENVIRONMENT invalide: {cls.ENVIRONMENT}. Doit être 'development' ou 'production'.")
        
        # Validation de la clé secrète en production
        if cls.ENVIRONMENT == "production" and cls.SECRET_KEY == "dev-secret-key-change-me":
            errors.append(
                "❌ SECRET_KEY par défaut détectée en production.\n"
                "   → Générez une clé secrète unique pour la production"
            )
        
        # Validation du niveau de log
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if cls.LOG_LEVEL not in valid_log_levels:
            errors.append(f"❌ LOG_LEVEL invalide: {cls.LOG_LEVEL}. Doit être l'un de: {valid_log_levels}")
        
        if errors:
            error_message = "\n🔧 Erreurs de configuration:\n\n" + "\n\n".join(errors)
            error_message += f"\n\n💡 Vérifiez votre fichier .env dans: {Path.cwd() / '.env'}"
            raise ValueError(error_message)
    
    @classmethod
    def is_development(cls) -> bool:
        """Retourne True si on est en mode développement"""
        return cls.ENVIRONMENT == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Retourne True si on est en mode production"""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def get_haloscan_headers(cls) -> dict:
        """Retourne les headers pour les requêtes Haloscan de manière sécurisée"""
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "haloscan-api-key": cls.HALOSCAN_API_KEY
        }
    
    @classmethod
    def print_config_summary(cls) -> None:
        """Affiche un résumé sécurisé de la configuration (sans clés sensibles)"""
        print("🔧 Configuration du serveur MCP Haloscan:")
        print(f"   📍 Serveur: {cls.HOST}:{cls.PORT}")
        print(f"   🌍 Environnement: {cls.ENVIRONMENT}")
        print(f"   📊 Logs: {cls.LOG_LEVEL}")
        print(f"   🤖 MCP: {cls.MCP_SERVER_NAME} v{cls.MCP_SERVER_VERSION}")
        print(f"   🔑 API Haloscan: {'✅ Configurée' if cls.HALOSCAN_API_KEY and cls.HALOSCAN_API_KEY != 'your_haloscan_api_key_here' else '❌ Non configurée'}")
        if cls.is_development():
            print("   ⚠️  Mode développement actif")