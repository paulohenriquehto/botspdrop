"""
API Package para Dashboard Administrativo SPDrop
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    """Cria e configura a aplicação FastAPI"""

    app = FastAPI(
        title="SPDrop Admin API",
        description="API para gerenciamento e controle do bot SPDrop",
        version="1.0.0"
    )

    # Configurar CORS - RESTRITO PARA SEGURANÇA
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:80",
            "http://127.0.0.1",
            "http://127.0.0.1:80",
            # Adicionar domínio de produção quando houver:
            # "https://seudominio.com"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Registrar rotas
    from api.auth import router as auth_router
    from api.dashboard import router as dashboard_router
    from api.conversations import router as conversations_router
    from api.qrcode import router as qrcode_router

    app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])
    app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
    app.include_router(conversations_router, prefix="/api/conversations", tags=["Conversas"])
    app.include_router(qrcode_router, prefix="/api/qrcode", tags=["QR Code"])

    @app.get("/")
    def root():
        return {"message": "SPDrop Admin API - Funcionando!"}

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    return app
