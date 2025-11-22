# 07 - Integração Completa dos Componentes

## 🔗 Visão Geral

Este documento explica como **TODOS os componentes** se conectam e trabalham juntos:

```
WhatsApp ←→ WhatsApp Web.js ←→ Bot FastAPI ←→ Agente Gabi ←→ PostgreSQL
```

---

## 📊 Fluxo Completo de Mensagem

### 1. **Usuário envia mensagem no WhatsApp**

```
Usuário (celular): "Oi, quanto custa?"
```

**WhatsApp →** Servidor WhatsApp (Meta)

---

### 2. **WhatsApp Web.js recebe via Puppeteer**

```javascript
// whatsapp-service/server.js

client.on('message', async (message) => {
    console.log('📨 Mensagem recebida:', message.from, '-', message.body);

    // Payload
    {
        from: "5511999999999@c.us",  // ou @lid
        body: "Oi, quanto custa?",
        timestamp: "1700000000",
        hasMedia: false,
        type: "chat"
    }

    // Enviar para bot via webhook
    await fetch('http://bot:5000/webhook', {
        method: 'POST',
        body: JSON.stringify(payload)
    });
});
```

**WhatsApp Web.js →** POST http://bot:5000/webhook

---

### 3. **Bot FastAPI recebe webhook**

```python
# main.py

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    from_number = payload["from"]     # "5511999999999@c.us"
    message_text = payload["body"]    # "Oi, quanto custa?"

    # Ignorar grupos
    if "@g.us" in from_number:
        return {"status": "ignored_group"}

    # Ignorar vazias
    if not message_text.strip():
        return {"status": "ignored_empty"}

    # Adicionar ao buffer (13 segundos)
    await add_to_buffer_and_schedule(from_number, message_text, payload)

    return {"status": "buffered"}
```

**Bot →** Buffer de 13 segundos

---

### 4. **Buffer aguarda e unifica mensagens**

```python
# main.py

# Buffer acumula mensagens do mesmo usuário
message_buffers[from_number] = {
    "messages": ["Oi", "quanto custa?"],
    "task": <asyncio.Task>,
    "payload": {...}
}

# Após 13 segundos SEM novas mensagens:
async def process_buffered_messages(from_number: str):
    await asyncio.sleep(13)  # Aguarda

    # Unificar
    unified_message = "\n".join(["Oi", "quanto custa?"])
    # "Oi\nquanto custa?"

    # Processar
    await handle_message(payload)
```

**Buffer →** handle_message()

---

### 5. **Bot busca/cria cliente no PostgreSQL**

```python
# main.py → handle_message()

from customer_manager import customer_manager

# Buscar ou criar cliente
customer_id = customer_manager.get_or_create_customer(from_number)

# Se não existe:
#   INSERT INTO customers (phone, name) VALUES ('5511999999999@c.us', 'Cliente')
#   RETURN customer_id

# Se existe:
#   SELECT id FROM customers WHERE phone = '5511999999999@c.us'
#   RETURN customer_id
```

**customer_manager →** PostgreSQL (customers table)

---

### 6. **Bot constrói contexto**

```python
# customer_manager.py

def build_context_message(customer_id, message_text):
    # Buscar histórico recente (últimas 5 mensagens)
    history = self.get_recent_history(customer_id, limit=5)

    # Construir mensagem com contexto
    context_message = f"""
[CONTEXTO INTERNO: customer_id={customer_id}]

Histórico recente:
{history}

Nova mensagem do cliente:
{message_text}
"""

    return context_message
```

**Bot →** Mensagem enriquecida com contexto

---

### 7. **Bot cria session_id**

```python
# main.py

# Normalizar número
normalized_phone = from_number.replace("@c.us", "").replace("@s.whatsapp.net", "")
# "5511999999999@c.us" → "5511999999999"

# Criar session_id
session_id = f"whatsapp_{normalized_phone}"
# "whatsapp_5511999999999"
```

**Bot →** session_id único por cliente

---

### 8. **Bot chama Agente Gabi**

```python
# main.py

from agentes.agente_suporte import support_agent

# Executar agente (síncrono em thread separada)
from functools import partial
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)
loop = asyncio.get_event_loop()

run_with_session = partial(
    support_agent.run,
    message_with_context,
    session_id=session_id
)

run_output = await loop.run_in_executor(executor, run_with_session)
```

**Bot →** Agente Gabi (GPT-4.1-mini)

---

### 9. **Agente Gabi processa**

```python
# agentes/agente_suporte.py

support_agent = Agent(
    name="Gabi",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[SPDropFAQTools(), SPDropMemoryTools(), ConversationScriptsTools()],
    db=postgres_db,
    add_history_to_context=True,
    instructions="""[Prompt de 11.665 caracteres]"""
)

# Gabi recebe:
# - message_with_context (com customer_id)
# - session_id
# - Histórico automático (add_history_to_context=True)

# Gabi processa:
# 1. Extrai customer_id do contexto
# 2. Busca histórico (via tool)
# 3. Identifica intenção
# 4. Usa ferramentas se necessário
# 5. Gera resposta natural

# Saída:
agent_response = "Olá! 😊\n\nEu sou a Gabi da SPDrop...\n\n..."
```

**Agente Gabi →** Resposta completa gerada

---

### 10. **Bot extrai resposta**

```python
# main.py

# Extrair resposta do objeto RunOutput
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
```

**Bot →** Texto da resposta extraído

---

### 11. **Bot salva no PostgreSQL**

```python
# main.py

customer_manager.save_conversation(
    session_id=session_id,
    customer_id=customer_id,
    user_message=message_text,
    agent_response=agent_response
)

# INSERT INTO conversation_history (
#     session_id, customer_id, user_message, agent_response, timestamp
# ) VALUES (
#     'whatsapp_5511999999999', 42, 'Oi, quanto custa?', 'Olá! Eu sou a Gabi...', NOW()
# )
```

**Bot →** PostgreSQL (conversation_history table)

---

### 12. **Bot divide resposta em partes**

```python
# main.py

await send_message_in_parts(from_number, agent_response)

# Dividir por parágrafos
parts = re.split(r'\n\s*\n', agent_response)

# Se não houver quebras duplas, dividir por linhas
if len(parts) == 1:
    parts = agent_response.split('\n')

# Resultado:
final_parts = [
    "Olá! 😊",
    "Eu sou a Gabi da SPDrop.",
    "Temos 3 planos: Mensal (R$99), Semestral (R$499) e Anual (R$999).",
    "Qual se encaixa melhor para você?"
]
```

**Bot →** Lista de micro mensagens

---

### 13. **Bot envia cada parte separadamente**

```python
# main.py

from whatsapp_integration import whatsapp_client

for i, part in enumerate(final_parts):
    # Enviar parte
    await whatsapp_client.send_text(from_number, part)

    # Log
    logger.info(f"📤 Mensagem {i+1}/{len(final_parts)} enviada")

    # Delay entre mensagens (3-6 segundos)
    if i < len(final_parts) - 1:
        delay = min(3 + (len(part) / 100), 6)
        logger.info(f"⏱️ Aguardando {delay:.1f}s...")
        await asyncio.sleep(delay)
```

**Bot →** POST http://whatsapp:3000/send (uma por vez)

---

### 14. **WhatsApp Web.js recebe requisição de envio**

```javascript
// whatsapp-service/server.js

app.post('/send', async (req, res) => {
    const { number, message } = req.body;
    // number: "5511999999999@c.us"
    // message: "Olá! 😊"

    let chatId;

    // Suportar @c.us e @lid
    if (number.includes('@c.us') || number.includes('@lid')) {
        chatId = number;  // Usar diretamente
    } else {
        // Validar número
        const numberId = await client.getNumberId(number);
        chatId = numberId._serialized;
    }

    // Enviar
    await client.sendMessage(chatId, message);

    res.json({status: 'success'});
});
```

**WhatsApp Web.js →** WhatsApp (Meta)

---

### 15. **Mensagem chega no celular do usuário**

```
Gabi (WhatsApp):
├─ 09:00:15 "Olá! 😊"
├─ 09:00:18 "Eu sou a Gabi da SPDrop."
├─ 09:00:22 "Temos 3 planos..."
└─ 09:00:28 "Qual se encaixa melhor para você?"
```

**WhatsApp →** Usuário vê mensagens espaçadas

---

## 🔄 Integrações Entre Componentes

### 1. WhatsApp Web.js ↔ Bot

**Protocolo:** HTTP REST
**Endpoints:**

```
WhatsApp → Bot:
POST http://bot:5000/webhook
Body: {from, body, timestamp, hasMedia, type}

Bot → WhatsApp:
POST http://whatsapp:3000/send
Body: {number, message}
```

**Configuração:**
```yaml
# docker-compose.yml
whatsapp:
  environment:
    - WEBHOOK_URL=http://bot:5000/webhook

bot:
  environment:
    - WHATSAPP_API_URL=http://whatsapp:3000
```

---

### 2. Bot ↔ PostgreSQL

**Protocolo:** psycopg2 (PostgreSQL native)
**Conexão:**

```python
# database.py
DATABASE_URL = os.getenv("DATABASE_URL")
# "postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db"

conn = psycopg2.connect(DATABASE_URL)
```

**Tabelas usadas:**
- `customers` - Cadastro
- `sessions` - Sessões
- `conversation_history` - Histórico
- `customer_context` - Contexto

---

### 3. Bot ↔ Agente Gabi

**Protocolo:** Python direto (import)
**Comunicação:**

```python
# main.py
from agentes.agente_suporte import support_agent

# Chamar agente
run_output = support_agent.run(message_with_context, session_id=session_id)
```

**Dados trocados:**
- **Bot → Gabi:** message_with_context, session_id
- **Gabi → Bot:** RunOutput (com content)

---

### 4. Agente Gabi ↔ PostgreSQL

**Protocolo:** Agno DB (via agno.db.postgres)
**Configuração:**

```python
# agente_suporte.py
postgres_db = PostgresDb(db_url=database_url)

support_agent = Agent(
    db=postgres_db,
    add_history_to_context=True
)
```

**O que é salvo:**
- Histórico de conversas (automático)
- Run logs do agente
- Tool executions

---

### 5. Agente Gabi ↔ Tools

**Protocolo:** Python direto (Agno tools)
**Ferramentas:**

```python
tools=[
    SPDropFAQTools(),        # Acessa FAQ via CSV
    SPDropMemoryTools(),     # Acessa PostgreSQL diretamente
    ConversationScriptsTools()  # Acessa Scripts via CSV
]
```

**Quando são usadas:**
- Gabi decide proativamente quando usar
- Baseado no prompt e contexto
- Tools retornam dados estruturados

---

## 🌐 Rede Docker

### Configuração

```yaml
# docker-compose.yml
networks:
  vanlu_network:
    driver: bridge

services:
  postgres:
    networks:
      - vanlu_network

  whatsapp:
    networks:
      - vanlu_network

  bot:
    networks:
      - vanlu_network
```

### Resolução de Nomes

**Containers podem se comunicar pelos nomes:**

```
bot → postgres:5432
bot → whatsapp:3000
whatsapp → bot:5000
```

**Não funciona:**
```
bot → localhost:3000  ❌
bot → 127.0.0.1:3000  ❌
```

---

## 🗄️ Volumes Docker

### Persistência de Dados

```yaml
# docker-compose.yml
volumes:
  postgres_data:
    # Dados do PostgreSQL
    # /var/lib/postgresql/data

  whatsapp_auth:
    # Sessão do WhatsApp
    # /app/wwebjs_auth
```

**O que sobrevive a reinicializações:**
- ✅ Conversas no PostgreSQL
- ✅ Contexto dos clientes
- ✅ Sessão do WhatsApp (não precisa escanear QR novamente)

**O que é perdido:**
- ❌ Logs dos containers
- ❌ Buffer de mensagens (memória RAM)

---

## 🔐 Variáveis de Ambiente

### Compartilhamento

```env
# .env (raiz do projeto)
OPENAI_API_KEY=sk-proj-xxxxxxxxxx
DATABASE_URL=postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db
WHATSAPP_API_URL=http://whatsapp:3000
```

### Como são passadas

```yaml
# docker-compose.yml
bot:
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}  # Do .env
    - DATABASE_URL=postgresql://...     # Hardcoded
    - WHATSAPP_API_URL=http://whatsapp:3000
```

---

## 📊 Dependências entre Containers

```yaml
# docker-compose.yml
bot:
  depends_on:
    - postgres
    - whatsapp
```

**Ordem de inicialização:**
1. postgres (primeiro)
2. whatsapp (segundo)
3. bot (último - depende dos outros)

---

## 🧪 Teste de Integração Completa

### Teste End-to-End

```bash
# 1. Verificar todos os containers
docker compose ps

# 2. Verificar conectividade
docker exec vanlu_bot curl http://whatsapp:3000/health
docker exec vanlu_bot curl http://bot:5000/health
docker exec vanlu_bot pg_isready -h postgres -U vanlu_user

# 3. Simular mensagem completa
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "from": "5511999999999@c.us",
    "body": "Oi, quanto custa a plataforma?",
    "timestamp": "1234567890",
    "hasMedia": false,
    "type": "chat"
  }'

# 4. Ver logs em tempo real
docker compose logs -f bot whatsapp

# 5. Verificar no PostgreSQL
docker exec vanlu_postgres psql -U vanlu_user -d vanlu_db \
  -c "SELECT * FROM conversation_history ORDER BY timestamp DESC LIMIT 1;"
```

**Esperado:**
- ✅ Webhook recebido
- ✅ Buffer aguarda 13s
- ✅ Agente processa
- ✅ Resposta dividida em partes
- ✅ Mensagens enviadas
- ✅ Conversa salva no DB

---

## ⚠️ Troubleshooting de Integração

### Problema: Bot não recebe mensagens do WhatsApp

**Verificar:**
```bash
# Webhook configurado?
docker compose logs whatsapp | grep WEBHOOK_URL

# Bot está acessível?
docker exec vanlu_whatsapp curl http://bot:5000/health

# Rede está OK?
docker network inspect vanlu-agente_vanlu_network
```

---

### Problema: Bot não consegue enviar para WhatsApp

**Verificar:**
```bash
# WhatsApp está conectado?
curl http://localhost:9000/status

# Bot consegue acessar WhatsApp?
docker exec vanlu_bot curl http://whatsapp:3000/health

# Testar envio direto
curl -X POST http://localhost:9000/send \
  -H "Content-Type: application/json" \
  -d '{"number":"5511999999999@c.us","message":"teste"}'
```

---

### Problema: Agente não acessa PostgreSQL

**Verificar:**
```bash
# DATABASE_URL está correto?
docker exec vanlu_bot env | grep DATABASE_URL

# PostgreSQL está acessível?
docker exec vanlu_bot pg_isready -h postgres -U vanlu_user

# Credenciais corretas?
docker exec vanlu_bot psql postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db -c "\dt"
```

---

## ✅ Checklist de Integração

- [ ] Todos os 3 containers UP
- [ ] Rede Docker criada
- [ ] Volumes persistentes criados
- [ ] WhatsApp conectado (QR Code escaneado)
- [ ] PostgreSQL acessível
- [ ] Bot recebe webhooks do WhatsApp
- [ ] Bot envia mensagens para WhatsApp
- [ ] Agente Gabi processa mensagens
- [ ] Ferramentas funcionam
- [ ] Conversas salvas no PostgreSQL
- [ ] Mensagens divididas em partes
- [ ] Suporte a @c.us e @lid

---

## 📚 Próximos Passos

**[08-BUGS-CORRIGIDOS.md](./08-BUGS-CORRIGIDOS.md)** → Histórico de bugs e soluções

---

**Status:** ✅ Integração completa e funcional
