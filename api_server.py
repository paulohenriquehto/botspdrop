"""
Servidor API FastAPI para Dashboard Administrativo SPDrop

Iniciar com:
    uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

Documentação:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

import uvicorn
import logging
from api import create_app

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Criar aplicação
app = create_app()

if __name__ == "__main__":
    logger.info("🚀 Iniciando SPDrop Admin API...")
    logger.info("📚 Documentação disponível em: http://localhost:8000/docs")

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
