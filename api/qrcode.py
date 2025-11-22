"""
Rotas de QR Code - Geração e Status de Conexão WhatsApp
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from api.auth import verify_token
import requests
import io
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# URL do serviço WhatsApp
WHATSAPP_SERVICE_URL = "http://whatsapp:3000"


@router.get("/generate")
def generate_qr_code(token_data: dict = Depends(verify_token)):
    """
    Gera QR Code para autenticação do WhatsApp

    Requer autenticação JWT

    Retorna imagem PNG do QR Code
    """
    try:
        # Fazer requisição ao serviço WhatsApp
        response = requests.get(f"{WHATSAPP_SERVICE_URL}/qr", timeout=10)

        if response.status_code == 200:
            # Retornar imagem diretamente
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type="image/png",
                headers={"Content-Disposition": "inline; filename=whatsapp_qrcode.png"}
            )
        elif response.status_code == 400:
            # WhatsApp já está conectado
            raise HTTPException(
                status_code=400,
                detail="WhatsApp já está conectado. Use /status para verificar."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Erro ao gerar QR Code: {response.text}"
            )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Serviço WhatsApp não disponível. Verifique se o container está rodando."
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Timeout ao conectar com serviço WhatsApp"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar QR Code: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao gerar QR Code: {str(e)}"
        )


@router.get("/status")
def get_whatsapp_status(token_data: dict = Depends(verify_token)):
    """
    Verifica status da conexão WhatsApp

    Requer autenticação JWT

    Retorna:
        - connected: bool
        - ready: bool
        - phone: string (se conectado)
    """
    try:
        response = requests.get(f"{WHATSAPP_SERVICE_URL}/status", timeout=5)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "whatsapp_status": data
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Erro ao verificar status: {response.text}"
            )

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "connected": False,
            "ready": False,
            "error": "Serviço WhatsApp não disponível"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "connected": False,
            "ready": False,
            "error": "Timeout ao conectar com serviço WhatsApp"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )


@router.post("/disconnect")
def disconnect_whatsapp(token_data: dict = Depends(verify_token)):
    """
    Desconecta o WhatsApp (logout)

    Requer autenticação JWT
    """
    try:
        response = requests.post(f"{WHATSAPP_SERVICE_URL}/disconnect", timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": "WhatsApp desconectado com sucesso",
                "data": data
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Erro ao desconectar: {response.text}"
            )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Serviço WhatsApp não disponível"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Timeout ao desconectar WhatsApp"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desconectar: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )


@router.post("/restart")
def restart_whatsapp_service(token_data: dict = Depends(verify_token)):
    """
    Reinicia o serviço WhatsApp

    Requer autenticação JWT
    Útil quando há problemas de conexão
    """
    try:
        response = requests.post(f"{WHATSAPP_SERVICE_URL}/restart", timeout=15)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": "Serviço WhatsApp reiniciado com sucesso",
                "data": data
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Erro ao reiniciar: {response.text}"
            )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Serviço WhatsApp não disponível"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Timeout ao reiniciar serviço"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao reiniciar: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/health")
def whatsapp_health_check(token_data: dict = Depends(verify_token)):
    """
    Health check do serviço WhatsApp

    Verifica se o serviço está respondendo
    """
    try:
        response = requests.get(f"{WHATSAPP_SERVICE_URL}/health", timeout=3)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "Serviço WhatsApp está saudável",
                "status": "healthy"
            }
        else:
            return {
                "success": False,
                "message": "Serviço WhatsApp com problemas",
                "status": "unhealthy",
                "status_code": response.status_code
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Serviço WhatsApp não está respondendo",
            "status": "down"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao verificar saúde: {str(e)}",
            "status": "error"
        }
