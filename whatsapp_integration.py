import httpx
import os
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class WhatsAppClient:
    """Cliente para interagir com WhatsApp Web.js API"""

    def __init__(self):
        self.base_url = os.getenv("WHATSAPP_API_URL", "http://localhost:3000")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def send_text(self, to: str, text: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto via WhatsApp

        Args:
            to: Número do destinatário (formato: 5511999999999)
            text: Texto da mensagem

        Returns:
            Resposta da API
        """
        try:
            # Garantir formato correto do número
            phone = to.replace("@c.us", "").replace("@s.whatsapp.net", "")

            url = f"{self.base_url}/send"
            payload = {
                "number": phone,
                "message": text
            }

            logger.info(f"Enviando mensagem para {phone}: {text[:50]}...")

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Mensagem enviada com sucesso!")

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar mensagem: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}", exc_info=True)
            raise

    async def get_status(self) -> Dict[str, Any]:
        """
        Verifica status da conexão WhatsApp

        Returns:
            Status da conexão
        """
        try:
            url = f"{self.base_url}/status"
            response = await self.client.get(url)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            return {"connected": False, "error": str(e)}

    async def get_qr_code(self) -> Dict[str, Any]:
        """
        Obtém QR Code para conectar WhatsApp

        Returns:
            Dados com QR Code
        """
        try:
            url = f"{self.base_url}/qr"
            response = await self.client.get(url)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Erro ao obter QR Code: {str(e)}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde do serviço

        Returns:
            Status do serviço
        """
        try:
            url = f"{self.base_url}/health"
            response = await self.client.get(url)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Erro no health check: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def logout(self) -> Dict[str, Any]:
        """
        Faz logout do WhatsApp

        Returns:
            Resultado do logout
        """
        try:
            url = f"{self.base_url}/logout"
            response = await self.client.post(url)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Erro ao fazer logout: {str(e)}")
            raise

    async def close(self):
        """Fecha o client HTTP"""
        await self.client.aclose()

# Instância global
whatsapp_client = WhatsAppClient()
