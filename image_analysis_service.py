import os
import base64
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ImageAnalysisService:
    """Serviço de análise de imagem usando OpenAI Vision (GPT-4 Vision)"""

    def __init__(self):
        # Inicializar cliente OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no .env")

        self.client = OpenAI(api_key=api_key)
        logger.info("✅ ImageAnalysisService inicializado com OpenAI Vision")

    def analyze_image(self, image_base64: str, mimetype: str = "image/jpeg", caption: str = None) -> str:
        """
        Analisa imagem base64 e retorna descrição detalhada em texto usando GPT-4 Vision

        Args:
            image_base64: Imagem em formato base64
            mimetype: Tipo do arquivo (image/jpeg, image/png, etc.)
            caption: Legenda enviada com a imagem (opcional)

        Returns:
            Descrição textual da imagem
        """
        try:
            logger.info(f"🖼️ Iniciando análise de imagem ({mimetype})...")

            # Preparar prompt para análise
            prompt = """Analise esta imagem detalhadamente e descreva o que você vê.

Seja específico e objetivo. Inclua:
- O que está sendo mostrado na imagem
- Contexto e ambiente
- Detalhes relevantes
- Se houver texto na imagem, transcreva-o

Responda em português de forma clara e direta."""

            # Se houver legenda, adicionar ao prompt
            if caption and caption != '[Imagem recebida]':
                prompt = f"""O usuário enviou uma imagem com a seguinte mensagem: "{caption}"

Analise a imagem detalhadamente e responda considerando a mensagem do usuário.

Seja específico e objetivo. Inclua:
- O que está sendo mostrado na imagem
- Contexto e ambiente
- Detalhes relevantes
- Se houver texto na imagem, transcreva-o

Responda em português de forma clara e direta."""

            # Construir data URI para a imagem
            data_uri = f"data:{mimetype};base64,{image_base64}"

            # Chamar GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Usando gpt-4o-mini que suporta visão e é mais barato
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_uri,
                                    "detail": "auto"  # auto, low, ou high
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )

            # Extrair descrição
            description = response.choices[0].message.content.strip()

            logger.info(f"✅ Análise concluída: '{description[:100]}...'")
            return description

        except Exception as e:
            logger.error(f"❌ Erro ao analisar imagem: {str(e)}", exc_info=True)
            return "[Não foi possível analisar a imagem]"

# Instância global
image_analysis_service = ImageAnalysisService()
