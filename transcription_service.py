import os
import base64
import tempfile
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Serviço de transcrição de áudio usando Groq Whisper Large v3"""

    def __init__(self):
        # Inicializar cliente Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não encontrada no .env")

        self.client = Groq(api_key=api_key)
        logger.info("✅ TranscriptionService inicializado com Groq Whisper")

    def transcribe_audio(self, audio_base64: str, mimetype: str = "audio/ogg") -> str:
        """
        Transcreve áudio base64 para texto usando Groq Whisper Large v3 Turbo

        Args:
            audio_base64: Áudio em formato base64
            mimetype: Tipo do arquivo (audio/ogg, audio/mpeg, etc.)

        Returns:
            Texto transcrito do áudio
        """
        try:
            logger.info(f"🎤 Iniciando transcrição de áudio ({mimetype})...")

            # Converter base64 para bytes
            audio_bytes = base64.b64decode(audio_base64)
            logger.info(f"📊 Áudio decodificado: {len(audio_bytes)} bytes")

            # Determinar extensão do arquivo baseado no mimetype
            extension = self._get_extension_from_mimetype(mimetype)

            # Salvar temporariamente (Groq precisa de arquivo)
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
                logger.info(f"💾 Áudio salvo temporariamente: {temp_file_path}")

            try:
                # Transcrever usando Groq Whisper Large v3 Turbo
                with open(temp_file_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=(f"audio{extension}", audio_file.read()),
                        model="whisper-large-v3-turbo",
                        language="pt",  # Português
                        response_format="text"
                    )

                # Groq retorna texto direto quando response_format="text"
                transcribed_text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()

                logger.info(f"✅ Transcrição concluída: '{transcribed_text[:100]}...'")
                return transcribed_text

            finally:
                # Limpar arquivo temporário
                try:
                    os.unlink(temp_file_path)
                    logger.info(f"🗑️ Arquivo temporário removido: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Aviso: Não foi possível remover arquivo temporário: {e}")

        except Exception as e:
            logger.error(f"❌ Erro ao transcrever áudio: {str(e)}", exc_info=True)
            return "[Não foi possível transcrever o áudio]"

    def _get_extension_from_mimetype(self, mimetype: str) -> str:
        """
        Converte mimetype para extensão de arquivo

        Args:
            mimetype: Tipo MIME (ex: 'audio/ogg', 'audio/mpeg')

        Returns:
            Extensão com ponto (ex: '.ogg', '.mp3')
        """
        mime_to_ext = {
            "audio/ogg": ".ogg",
            "audio/mpeg": ".mp3",
            "audio/mp3": ".mp3",
            "audio/wav": ".wav",
            "audio/webm": ".webm",
            "audio/opus": ".opus"
        }

        return mime_to_ext.get(mimetype.lower(), ".ogg")  # Default: .ogg

# Instância global
transcription_service = TranscriptionService()
