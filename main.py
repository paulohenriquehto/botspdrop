from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import asyncio
import re

load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vanlu WhatsApp Bot", version="1.0.0")

# Sistema de buffer de mensagens para juntar mensagens fracionadas
message_buffers = {}
buffer_lock = asyncio.Lock()
BUFFER_TIMEOUT = 13  # segundos para aguardar novas mensagens

@app.get("/")
async def root():
    """Endpoint raiz - informações básicas"""
    return {
        "service": "Vanlu WhatsApp Bot",
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

async def add_to_buffer_and_schedule(from_number: str, message_text: str, payload: dict):
    """
    Adiciona mensagem ao buffer e agenda processamento após BUFFER_TIMEOUT segundos

    Args:
        from_number: Número do remetente
        message_text: Texto da mensagem
        payload: Payload completo do WhatsApp
    """
    async with buffer_lock:
        # Criar buffer se não existir
        if from_number not in message_buffers:
            message_buffers[from_number] = {
                "messages": [],
                "task": None,
                "payload": payload.copy()
            }

        # Adicionar mensagem ao buffer
        message_buffers[from_number]["messages"].append(message_text)
        logger.info(f"📝 Mensagem adicionada ao buffer de {from_number}. Total: {len(message_buffers[from_number]['messages'])} mensagens")

        # Cancelar timer anterior se existir
        if message_buffers[from_number]["task"]:
            message_buffers[from_number]["task"].cancel()
            logger.info(f"⏱️ Timer anterior cancelado para {from_number}")

        # Agendar novo processamento
        task = asyncio.create_task(process_buffered_messages(from_number))
        message_buffers[from_number]["task"] = task
        logger.info(f"⏳ Novo timer de {BUFFER_TIMEOUT}s iniciado para {from_number}")

async def process_buffered_messages(from_number: str):
    """
    Aguarda BUFFER_TIMEOUT segundos e processa todas mensagens acumuladas

    Args:
        from_number: Número do remetente
    """
    try:
        await asyncio.sleep(BUFFER_TIMEOUT)

        async with buffer_lock:
            if from_number not in message_buffers:
                return

            buffer_data = message_buffers[from_number]
            messages = buffer_data["messages"]
            payload = buffer_data["payload"]

            # Unificar todas as mensagens com quebra de linha
            unified_message = "\n".join(messages)

            logger.info(f"🔄 Processando {len(messages)} mensagens de {from_number}")
            logger.info(f"📨 Mensagem unificada: {unified_message[:100]}...")

            # Limpar buffer
            del message_buffers[from_number]

        # Processar mensagem unificada (fora do lock)
        payload["body"] = unified_message
        await handle_message(payload)

    except asyncio.CancelledError:
        logger.info(f"❌ Processamento cancelado para {from_number} (nova mensagem recebida)")
    except Exception as e:
        logger.error(f"Erro ao processar buffer de {from_number}: {str(e)}", exc_info=True)

@app.post("/webhook")
async def webhook(request: Request):
    """
    Endpoint para receber webhooks do WhatsApp Web.js

    WhatsApp Web.js envia mensagens recebidas do WhatsApp para este endpoint
    Usa sistema de buffer para juntar mensagens fracionadas do mesmo usuário
    """
    try:
        # Receber payload do WhatsApp Web.js
        payload = await request.json()

        logger.info(f"Webhook recebido: {payload}")

        # Extrair dados
        from_number = payload.get("from", "")
        message_text = payload.get("body", "")

        # Determinar se é grupo
        is_group = "@g.us" in from_number

        # Ignorar mensagens de grupos
        if is_group:
            logger.info(f"Mensagem de grupo ignorada: {from_number}")
            return {"status": "ignored_group"}

        # Ignorar mensagens vazias
        if not message_text or not message_text.strip():
            logger.info("Mensagem vazia ignorada")
            return {"status": "ignored_empty"}

        # Adicionar ao buffer ao invés de processar imediatamente
        await add_to_buffer_and_schedule(from_number, message_text, payload)

        return {"status": "buffered"}

    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def send_message_in_parts(to_number: str, message: str):
    """
    Divide mensagem em partes MICRO (cada parágrafo separado) e envia com delays

    Args:
        to_number: Número do destinatário
        message: Mensagem completa do agente
    """
    from whatsapp_integration import whatsapp_client

    # Dividir por quebras de linha duplas (parágrafos) - cada um vira mensagem separada
    parts = re.split(r'\n\s*\n', message.strip())

    # Se não houver quebras duplas, dividir por linha simples
    if len(parts) == 1:
        parts = message.split('\n')

    # Filtrar partes vazias e preparar para envio
    final_parts = []
    for part in parts:
        part = part.strip()
        if part:
            # Se uma parte for muito longa (>200 chars), dividir por frases
            if len(part) > 200:
                sentences = re.split(r'([.!?])\s+', part)
                current = ""
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    punct = sentences[i+1] if i+1 < len(sentences) else ""

                    if len(current) + len(sentence) > 200 and current:
                        final_parts.append(current.strip())
                        current = sentence + punct + " "
                    else:
                        current += sentence + punct + " "

                if current.strip():
                    final_parts.append(current.strip())
            else:
                final_parts.append(part)

    # Enviar cada parte INDIVIDUALMENTE com delay
    for i, part in enumerate(final_parts):
        await whatsapp_client.send_text(to_number, part)
        logger.info(f"  📤 Mensagem {i+1}/{len(final_parts)} enviada ({len(part)} chars)")

        # Delay entre mensagens (3-6 segundos para parecer humano)
        if i < len(final_parts) - 1:
            delay = min(3 + (len(part) / 100), 6)
            logger.info(f"  ⏱️ Aguardando {delay:.1f}s antes da próxima...")
            await asyncio.sleep(delay)

async def handle_message(payload: dict):
    """
    Processa mensagem recebida do WhatsApp

    Args:
        payload: Dados da mensagem do WhatsApp Web.js
    """
    try:
        from whatsapp_integration import whatsapp_client
        from customer_manager import customer_manager
        from agentes.agente_suporte import support_agent
        from transcription_service import transcription_service
        from image_analysis_service import image_analysis_service

        # Extrair dados da mensagem (whatsapp-web.js format)
        from_number = payload.get("from", "")
        message_text = payload.get("body", "")
        message_id = payload.get("timestamp", "")
        has_media = payload.get("hasMedia", False)
        message_type = payload.get("type", "")

        # 🎤 TRANSCRIÇÃO DE ÁUDIO: Se houver áudio, transcrever para texto
        if message_type in ['ptt', 'audio'] and 'audioData' in payload:
            logger.info("🎤 Áudio detectado! Iniciando transcrição...")

            audio_base64 = payload.get("audioData")
            audio_mimetype = payload.get("audioMimetype", "audio/ogg")

            # Transcrever áudio
            transcribed_text = transcription_service.transcribe_audio(
                audio_base64=audio_base64,
                mimetype=audio_mimetype
            )

            # Substituir message_text pelo texto transcrito
            message_text = transcribed_text
            logger.info(f"✅ Áudio transcrito: '{transcribed_text[:100]}...'")
        elif message_type in ['ptt', 'audio']:
            logger.warning("⚠️ Áudio detectado mas sem audioData no payload")
            message_text = "[Áudio não pôde ser processado]"

        # 🖼️ ANÁLISE DE IMAGEM: Se houver imagem, analisar e descrever
        if message_type == 'image' and 'imageData' in payload:
            logger.info("🖼️ Imagem detectada! Iniciando análise...")

            image_base64 = payload.get("imageData")
            image_mimetype = payload.get("imageMimetype", "image/jpeg")
            image_caption = payload.get("body", None)

            # Analisar imagem
            image_description = image_analysis_service.analyze_image(
                image_base64=image_base64,
                mimetype=image_mimetype,
                caption=image_caption
            )

            # Criar mensagem combinando legenda (se houver) e descrição da imagem
            if image_caption and image_caption != '[Imagem recebida]':
                message_text = f"[Imagem enviada com legenda: '{image_caption}']\n\nAnálise da imagem: {image_description}"
            else:
                message_text = f"[Imagem enviada]\n\nAnálise da imagem: {image_description}"

            logger.info(f"✅ Imagem analisada: '{image_description[:100]}...'")
        elif message_type == 'image':
            logger.warning("⚠️ Imagem detectada mas sem imageData no payload")
            message_text = "[Imagem não pôde ser processada]"

        # Determinar se é grupo (grupos têm @g.us no final)
        is_group = "@g.us" in from_number

        # Ignorar mensagens de grupos
        if is_group:
            logger.info(f"Mensagem de grupo ignorada: {from_number}")
            return

        # Ignorar mensagens vazias
        if not message_text or not message_text.strip():
            logger.info("Mensagem vazia ignorada")
            return

        logger.info(f"""
        ═══════════════════════════════════════
        NOVA MENSAGEM RECEBIDA
        ═══════════════════════════════════════
        De: {from_number}
        Texto: {message_text}
        ID: {message_id}
        ═══════════════════════════════════════
        """)

        # 1. Buscar ou criar cliente
        customer_id = customer_manager.get_or_create_customer(from_number)

        if not customer_id:
            logger.error("Falha ao obter customer_id")
            await whatsapp_client.send_text(
                from_number,
                "Desculpe, ocorreu um erro. Tente novamente."
            )
            return

        # 2. Construir mensagem com contexto
        message_with_context = customer_manager.build_context_message(
            customer_id,
            message_text
        )

        logger.info(f"Customer ID: {customer_id}")

        # 3. Criar session_id baseado no número do WhatsApp (normalizado)
        # Remove caracteres especiais e usa só números para session_id
        normalized_phone = from_number.replace("@c.us", "").replace("@s.whatsapp.net", "")
        session_id = f"whatsapp_{normalized_phone}"

        logger.info(f"Session ID: {session_id}")

        # 4. Processar com Agente Luciano
        logger.info("Processando com Agente Luciano...")

        # Usar .run() que é síncrono, passando session_id para contexto
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()

        # Criar função parcial para passar session_id
        from functools import partial
        run_with_session = partial(support_agent.run, message_with_context, session_id=session_id)

        run_output = await loop.run_in_executor(
            executor,
            run_with_session
        )

        # Extrair resposta
        if hasattr(run_output, 'content'):
            agent_response = run_output.content
        elif hasattr(run_output, 'message'):
            if hasattr(run_output.message, 'content'):
                agent_response = run_output.message.content
            else:
                agent_response = str(run_output.message)
        else:
            agent_response = str(run_output)

        logger.info(f"Resposta do agente: {agent_response[:100]}...")

        # 5. Salvar conversa no histórico
        customer_manager.save_conversation(
            session_id=session_id,
            customer_id=customer_id,
            user_message=message_text,
            agent_response=agent_response
        )

        # 6. Dividir e enviar resposta em partes (como humano)
        await send_message_in_parts(from_number, agent_response)

        logger.info("✓ Mensagem enviada com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)

        # Tentar enviar mensagem de erro ao cliente
        try:
            await whatsapp_client.send_text(
                from_number,
                "Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?"
            )
        except:
            pass

if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 5000))

    logger.info(f"Iniciando servidor FastAPI em {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
