"""
Configuration centralisée du logging pour le serveur MCP Haloscan
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Configure le système de logging avec fichier et console"""
    
    # Créer le dossier logs s'il n'existe pas
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Nom du fichier de log avec timestamp
    log_filename = logs_dir / f"haloscan_server_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configuration du logger principal
    logger = logging.getLogger("haloscan")
    logger.setLevel(logging.DEBUG)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour fichier (avec rotation)
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Logger pour FastAPI/Uvicorn
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = [file_handler, console_handler]
    
    # Logger pour les requêtes HTTP
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers = [file_handler, console_handler]
    
    # Logger pour le chat MCP
    chat_logger = logging.getLogger("chat")
    chat_logger.setLevel(logging.INFO)
    chat_logger.handlers = [file_handler, console_handler]
    chat_logger.propagate = False
    
    logger.info("🚀 Système de logging initialisé")
    logger.info(f"📁 Fichier de log: {log_filename}")
    
    return logger

def get_logger(name: str = "haloscan"):
    """Récupère un logger configuré"""
    return logging.getLogger(name)

# Logger global
logger = get_logger()
