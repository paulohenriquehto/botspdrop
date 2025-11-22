# 04 - Configuração do Bot Python (FastAPI)

## 🐍 Visão Geral

O bot é o **cérebro** do sistema, responsável por:
- Receber webhooks do WhatsApp
- Buffering de mensagens (13 segundos)
- Processar com agente de IA
- Dividir respostas em micro mensagens
- Enviar de volta para o WhatsApp

**Tecnologias:**
- FastAPI (framework web)
- Uvicorn (servidor ASGI)
- Asyncio (operações assíncronas)
- Python 3.10

---

## 📄 Arquivo main.py

Localização: `/main.py` (raiz do projeto)

### Estrutura Principal

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import asyncio
import re

app = FastAPI(title="Vanlu WhatsApp Bot", version="1.0.0")
```

---

## 🔧 Sistema de Buffer de Mensagens

### Problema que Resolve

Usuários frequentemente enviam mensagens **fracionadas**:

```
Usuário (09:00:00): "Oi"
Usuário (09:00:01): "tudo bem?"
Usuário (09:00:02): "quanto custa lavagem?"
```

**Sem buffer:** Bot responderia 3 vezes (uma para cada mensagem).

**Com buffer:** Bot aguarda 13 segundos, une tudo e responde 1 vez.

---

### Implementação

```python
message_buffers = {}
buffer_lock = asyncio.Lock()
BUFFER_TIMEOUT = 13  # segundos
```

#### Estrutura do Buffer

```python
message_buffers[from_number] = {
    "messages": ["Oi", "tudo bem?", "quanto custa lavagem?"],
    "task": <asyncio.Task>,
    "payload": {...}  # Payload original do WhatsApp
}
```

---

### Função: add_to_buffer_and_schedule()

```python
async def add_to_buffer_and_schedule(from_number: str, message_text: str, payload: dict):
    async with buffer_lock:
        # Criar buffer se não existir
        if from_number not in message_buffers:
            message_buffers[from_number] = {
                "messages": [],
                "task": None,
                "payload": payload.copy()
            }

        # Adicionar mensagem
        message_buffers[from_number]["messages"].append(message_text)

        # Cancelar timer anterior
        if message_buffers[from_number]["task"]:
            message_buffers[from_number]["task"].cancel()

        # Agendar novo processamento (13s)
        task = asyncio.create_task(process_buffered_messages(from_number))
        message_buffers[from_number]["task"] = task
```

**Lógica:**
1. Nova mensagem chega
2. Adiciona ao buffer daquele número
3. Cancela timer anterior (se existir)
4. Inicia novo timer de 13 segundos
5. Se outra mensagem chegar antes de 13s, reinicia o timer

---

### Função: process_buffered_messages()

```python
async def process_buffered_messages(from_number: str):
    try:
        await asyncio.sleep(BUFFER_TIMEOUT)  # Aguarda 13s

        async with buffer_lock:
            if from_number not in message_buffers:
                return

            buffer_data = message_buffers[from_number]
            messages = buffer_data["messages"]
            payload = buffer_data["payload"]

            # Unificar mensagens com quebra de linha
            unified_message = "\n".join(messages)

            logger.info(f"🔄 Processando {len(messages)} mensagens de {from_number}")

            # Limpar buffer
            del message_buffers[from_number]

        # Processar mensagem unificada
        payload["body"] = unified_message
        await handle_message(payload)

    except asyncio.CancelledError:
        logger.info(f"❌ Processamento cancelado (nova mensagem recebida)")
```

**Resultado:**
```
Entrada:
  - "Oi"
  - "tudo bem?"
  - "quanto custa lavagem?"

Saída unificada:
  - "Oi\ntudo bem?\nquanto custa lavagem?"
```

---

## 📥 Endpoint: POST /webhook

**Função:** Receber mensagens do WhatsApp Web.js.

```python
@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()

        from_number = payload.get("from", "")
        message_text = payload.get("body", "")

        # Ignorar grupos
        if "@g.us" in from_number:
            logger.info(f"Mensagem de grupo ignorada: {from_number}")
            return {"status": "ignored_group"}

        # Ignorar mensagens vazias
        if not message_text or not message_text.strip():
            logger.info("Mensagem vazia ignorada")
            return {"status": "ignored_empty"}

        # Adicionar ao buffer
        await add_to_buffer_and_schedule(from_number, message_text, payload)

        return {"status": "buffered"}

    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

**Payload recebido do WhatsApp:**
```json
{
  "from": "5511999999999@c.us",
  "body": "Oi, quero agendar",
  "timestamp": "1234567890",
  "hasMedia": false,
  "type": "chat"
}
```

**Filtros aplicados:**
- ✅ Ignora mensagens de grupos (`@g.us`)
- ✅ Ignora mensagens vazias
- ✅ Aceita qualquer número individual (`@c.us` e `@lid`)

---

## 🧠 Função: handle_message()

**Função:** Processa a mensagem unificada com o agente de IA.

```python
async def handle_message(payload: dict):
    try:
        from whatsapp_integration import whatsapp_client
        from customer_manager import customer_manager
        from agentes.agente_suporte import support_agent

        from_number = payload.get("from", "")
        message_text = payload.get("body", "")

        # 1. Buscar ou criar cliente
        customer_id = customer_manager.get_or_create_customer(from_number)

        # 2. Construir mensagem com contexto
        message_with_context = customer_manager.build_context_message(
            customer_id,
            message_text
        )

        # 3. Criar session_id (normalizado)
        normalized_phone = from_number.replace("@c.us", "").replace("@s.whatsapp.net", "")
        session_id = f"whatsapp_{normalized_phone}"

        # 4. Processar com agente (síncrono rodando em executor)
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()

        run_with_session = partial(support_agent.run, message_with_context, session_id=session_id)

        run_output = await loop.run_in_executor(
            executor,
            run_with_session
        )

        # Extrair resposta do agente
        agent_response = extract_response(run_output)

        # 5. Salvar conversa no histórico
        customer_manager.save_conversation(
            session_id=session_id,
            customer_id=customer_id,
            user_message=message_text,
            agent_response=agent_response
        )

        # 6. Dividir e enviar resposta em partes
        await send_message_in_parts(from_number, agent_response)

        logger.info("✓ Mensagem enviada com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
```

---

## ✂️ Sistema de Divisão de Mensagens (Micro Mensagens)

### Problema que Resolve

Respostas longas parecem **não humanas**. Usuário prefere mensagens **curtas e espaçadas**.

**Antes:**
```
Bot (09:00:00): "Olá, João! Eu sou a Gabi da SPDrop. Vi que você está interessado em nossos serviços. Temos lavagem completa por R$80 e polimento por R$150. Qual serviço você procura?"
```

**Depois:**
```
Bot (09:00:00): "Olá, João! 😊"
Bot (09:00:03): "Eu sou a Gabi da SPDrop."
Bot (09:00:07): "Vi que você está interessado em nossos serviços."
Bot (09:00:12): "Temos lavagem completa por R$80 e polimento por R$150."
Bot (09:00:17): "Qual serviço você procura?"
```

---

### Implementação: send_message_in_parts()

```python
async def send_message_in_parts(to_number: str, message: str):
    from whatsapp_integration import whatsapp_client

    # Dividir por quebras de linha duplas (parágrafos)
    parts = re.split(r'\n\s*\n', message.strip())

    # Se não houver quebras duplas, dividir por linha simples
    if len(parts) == 1:
        parts = message.split('\n')

    # Filtrar partes vazias
    final_parts = []
    for part in parts:
        part = part.strip()
        if part:
            # Se parte for muito longa (>200 chars), dividir por frases
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

        # Delay entre mensagens (3-6 segundos)
        if i < len(final_parts) - 1:
            delay = min(3 + (len(part) / 100), 6)
            logger.info(f"  ⏱️ Aguardando {delay:.1f}s antes da próxima...")
            await asyncio.sleep(delay)
```

**Lógica de divisão:**
1. Dividir por quebras duplas (`\n\n`) → parágrafos
2. Se não houver, dividir por linhas simples (`\n`)
3. Se parte >200 chars, dividir por frases (`.`, `!`, `?`)
4. Enviar cada parte com delay de 3-6 segundos

**Cálculo do delay:**
```python
delay = min(3 + (len(part) / 100), 6)
# Mínimo: 3 segundos
# Máximo: 6 segundos
# Proporcional ao tamanho (mais longo = mais delay)
```

---

## 🌐 Endpoints da API

### GET / - Informações Básicas

```bash
curl http://localhost:5000/
```

**Resposta:**
```json
{
  "service": "Vanlu WhatsApp Bot",
  "status": "online",
  "version": "1.0.0",
  "timestamp": "2025-11-19T12:34:56"
}
```

---

### GET /health - Health Check

```bash
curl http://localhost:5000/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T12:34:56"
}
```

---

### POST /webhook - Receber Mensagens

**Uso:** WhatsApp Web.js envia mensagens para este endpoint.

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "from": "5511999999999@c.us",
    "body": "Oi, quanto custa?",
    "timestamp": "1234567890",
    "hasMedia": false,
    "type": "chat"
  }'
```

**Respostas possíveis:**
- `{"status": "buffered"}` - Mensagem adicionada ao buffer
- `{"status": "ignored_group"}` - Mensagem de grupo ignorada
- `{"status": "ignored_empty"}` - Mensagem vazia ignorada

---

## 📊 Logs do Sistema

### Mensagem Recebida

```
2025-11-19 12:34:56 - INFO - Webhook recebido: {...}
2025-11-19 12:34:56 - INFO - 📝 Mensagem adicionada ao buffer de 5511999999999@c.us. Total: 1 mensagens
2025-11-19 12:34:56 - INFO - ⏳ Novo timer de 13s iniciado para 5511999999999@c.us
```

---

### Processamento

```
2025-11-19 12:35:09 - INFO - 🔄 Processando 3 mensagens de 5511999999999@c.us
2025-11-19 12:35:09 - INFO - 📨 Mensagem unificada: Oi\ntudo bem?\nquanto custa...
2025-11-19 12:35:09 - INFO - ═══════════════════════════════════════
                              NOVA MENSAGEM RECEBIDA
                              ═══════════════════════════════════════
                              De: 5511999999999@c.us
                              Texto: Oi\ntudo bem?\nquanto custa lavagem?
                              ID: 1234567890
                              ═══════════════════════════════════════
2025-11-19 12:35:09 - INFO - Customer ID: 42
2025-11-19 12:35:09 - INFO - Session ID: whatsapp_5511999999999
2025-11-19 12:35:09 - INFO - Processando com Agente Luciano...
```

---

### Resposta do Agente

```
2025-11-19 12:35:12 - INFO - Resposta do agente: Olá! Eu sou a Gabi da SPDrop...
2025-11-19 12:35:12 - INFO -   📤 Mensagem 1/5 enviada (15 chars)
2025-11-19 12:35:12 - INFO -   ⏱️ Aguardando 3.2s antes da próxima...
2025-11-19 12:35:15 - INFO -   📤 Mensagem 2/5 enviada (42 chars)
2025-11-19 12:35:15 - INFO -   ⏱️ Aguardando 3.4s antes da próxima...
...
2025-11-19 12:35:30 - INFO - ✓ Mensagem enviada com sucesso!
```

---

## 🔧 Variáveis de Ambiente

```env
# PostgreSQL
DATABASE_URL=postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db

# WhatsApp API
WHATSAPP_API_URL=http://whatsapp:3000

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxx

# FastAPI (opcional)
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=5000
```

---

## 🔄 Fluxo Completo de Mensagem

```
1. WhatsApp → WhatsApp Web.js
   └─ Mensagem recebida

2. WhatsApp Web.js → POST /webhook (FastAPI)
   └─ Payload JSON enviado

3. FastAPI → Buffer (13s)
   └─ Acumula mensagens do mesmo usuário

4. FastAPI → handle_message()
   ├─ Busca/cria cliente no DB
   ├─ Constrói contexto
   ├─ Cria session_id
   ├─ Processa com agente IA
   ├─ Extrai resposta
   └─ Salva histórico

5. FastAPI → send_message_in_parts()
   ├─ Divide resposta em partes
   ├─ Envia cada parte individualmente
   └─ Aguarda 3-6s entre partes

6. FastAPI → POST /send (WhatsApp Web.js)
   └─ Cada parte enviada separadamente

7. WhatsApp Web.js → WhatsApp → Cliente
   └─ Mensagens chegam espaçadas
```

---

## ⚠️ Troubleshooting

### Container não inicia

```bash
# Ver logs
docker compose logs bot

# Erros comuns:
# - ImportError: Módulo não encontrado → Rebuild
# - Connection refused: postgres → Aguardar postgres iniciar
```

**Solução:**
```bash
docker compose build bot
docker compose up -d bot
```

---

### Webhook não recebe mensagens

```bash
# Verificar se bot está rodando
curl http://localhost:5000/health

# Verificar se WhatsApp está enviando para URL correta
docker compose logs whatsapp | grep WEBHOOK_URL

# Testar webhook manualmente
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"from":"5511999999999@c.us","body":"teste","timestamp":"123","hasMedia":false,"type":"chat"}'
```

---

### Agente não processa

```bash
# Verificar OpenAI API Key
docker exec vanlu_bot env | grep OPENAI_API_KEY

# Verificar logs do agente
docker compose logs bot | grep -i "processando com agente"
```

---

### Mensagens não são enviadas

```bash
# Verificar se WhatsApp está conectado
curl http://localhost:9000/status

# Verificar logs de envio
docker compose logs bot | grep "📤 Mensagem"

# Testar envio direto
curl -X POST http://localhost:9000/send \
  -H "Content-Type: application/json" \
  -d '{"number":"5511999999999@c.us","message":"Teste"}'
```

---

## 📈 Performance

### Recursos Utilizados

- **CPU:** ~30-50% durante processamento
- **RAM:** ~200MB em idle, ~500MB durante IA
- **Latência:**
  - Buffer: 13 segundos fixos
  - Processamento IA: 2-5 segundos
  - Envio de mensagens: 3-6 segundos por parte

**Total:** ~20-30 segundos para resposta completa.

---

### Otimizações Implementadas

✅ **Buffer de mensagens** - Evita processamentos duplicados
✅ **Async/await** - Múltiplas conversas simultâneas
✅ **ThreadPoolExecutor** - Agente síncrono em thread separada
✅ **Micro mensagens** - Parecem mais humanas
✅ **Índices no DB** - Queries rápidas

---

## ✅ Checklist de Funcionamento

- [ ] Container bot está UP
- [ ] Health check retorna "healthy"
- [ ] Webhook recebe mensagens
- [ ] Buffer acumula mensagens em 13s
- [ ] Agente processa e gera resposta
- [ ] Mensagens são divididas em partes
- [ ] Delays entre mensagens funcionam
- [ ] Conversas são salvas no DB
- [ ] Sistema aceita @c.us e @lid

---

## 📚 Próximos Passos

**[05-AGENTE.md](./05-AGENTE.md)** → Configuração do agente de IA (Gabi)

---

**Status:** ✅ Bot FastAPI configurado e funcional
