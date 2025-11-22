# 03 - Configuração do WhatsApp Web.js

## 📱 Visão Geral

O serviço WhatsApp usa `whatsapp-web.js` (biblioteca Node.js) para:
- Conectar ao WhatsApp via QR Code
- Receber mensagens de clientes
- Enviar respostas automatizadas
- Manter sessão persistente

---

## 🏗️ Arquitetura

```
┌──────────────┐
│   WhatsApp   │ ← Usuários enviam mensagens
└──────┬───────┘
       │
       ↓
┌──────────────────────┐
│  WhatsApp Web.js     │ ← Container Node.js
│  (porta 9000)        │
│                      │
│  Puppeteer           │ ← Simula navegador
│  Chrome headless     │
│                      │
│  LocalAuth           │ ← Sessão persistente
│  /wwebjs_auth        │
└──────┬───────────────┘
       │ HTTP POST
       ↓
┌──────────────────────┐
│  Bot FastAPI         │ ← Recebe webhook
│  (porta 5000)        │
└──────────────────────┘
```

---

## 📄 Arquivo server.js

Localização: `whatsapp-service/server.js`

### Estrutura Principal

```javascript
const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcodeTerminal = require('qrcode-terminal');
const QRCode = require('qrcode');

const app = express();
const PORT = process.env.PORT || 3000;
const WEBHOOK_URL = process.env.WEBHOOK_URL || 'http://bot:5000/webhook';

let client;
let isReady = false;
let qrCodeData = null;
```

---

### Inicialização do Cliente

```javascript
client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './wwebjs_auth'
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--single-process'
        ]
    }
});
```

**Configurações importantes:**
- `LocalAuth`: Salva sessão no volume Docker
- `headless: true`: Chrome sem interface gráfica
- `--no-sandbox`: Necessário para Docker
- `--disable-dev-shm-usage`: Evita problemas de memória

---

### Eventos do Cliente

#### 1. QR Code

```javascript
client.on('qr', (qr) => {
    console.log('QR Code recebido! Escaneie com WhatsApp:');
    qrcodeTerminal.generate(qr, { small: true });
    qrCodeData = qr;
});
```

**Quando ocorre:** Primeira conexão ou sessão expirada.

---

#### 2. Cliente Pronto

```javascript
client.on('ready', () => {
    console.log('✅ WhatsApp conectado com sucesso!');
    isReady = true;
    qrCodeData = null;
});
```

**Quando ocorre:** WhatsApp conectado e pronto para uso.

---

#### 3. Receber Mensagens

```javascript
client.on('message', async (message) => {
    console.log('📨 Mensagem recebida:', message.from, '-', message.body);

    // Enviar para webhook do bot Python
    try {
        const fetch = (await import('node-fetch')).default;
        await fetch(WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from: message.from,
                body: message.body,
                timestamp: message.timestamp,
                hasMedia: message.hasMedia,
                type: message.type
            })
        });
    } catch (error) {
        console.error('Erro ao enviar para webhook:', error.message);
    }
});
```

**Dados enviados ao bot:**
- `from`: Número do remetente (formato: `5511999999999@c.us` ou `@lid`)
- `body`: Texto da mensagem
- `timestamp`: Timestamp da mensagem
- `hasMedia`: Se tem mídia anexada
- `type`: Tipo da mensagem (chat, image, audio, etc.)

---

## 🌐 Rotas da API

### 1. GET / - Página do QR Code

Renderiza página HTML com QR Code ou status de conexão.

**Estados possíveis:**
- ⏳ Aguardando QR Code
- 📱 QR Code disponível (escaneie)
- ✅ Conectado

```bash
# Acessar no navegador
http://localhost:9000
```

---

### 2. GET /health - Health Check

```bash
curl http://localhost:9000/health
```

**Resposta:**
```json
{
  "status": "ok",
  "whatsapp_ready": true,
  "has_qr": false
}
```

---

### 3. GET /status - Status da Conexão

```bash
curl http://localhost:9000/status
```

**Resposta (conectado):**
```json
{
  "connected": true,
  "state": "CONNECTED",
  "ready": true
}
```

---

### 4. GET /info - Informações do Número Conectado

```bash
curl http://localhost:9000/info
```

**Resposta:**
```json
{
  "wid": "5511999999999@c.us",
  "pushname": "Seu Nome",
  "platform": "android"
}
```

---

### 5. POST /send - Enviar Mensagem

**Endpoint crítico para enviar respostas do bot.**

```bash
curl -X POST http://localhost:9000/send \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999@c.us",
    "message": "Olá! Como posso ajudar?"
  }'
```

#### ⚠️ BUG CRÍTICO CORRIGIDO: Suporte a @lid

**Problema anterior:**
- WhatsApp começou a usar formato `@lid` (Local ID) além de `@c.us`
- Servidor só funcionava com `@c.us`
- Mensagens de números `@lid` eram recebidas mas respostas FALHAVAM

**Solução aplicada (linhas 268-302):**

```javascript
app.post('/send', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({ error: 'WhatsApp não está conectado' });
    }

    const { number, message } = req.body;

    if (!number || !message) {
        return res.status(400).json({ error: 'Número e mensagem são obrigatórios' });
    }

    try {
        let chatId;

        // ✅ CORREÇÃO: Suportar ambos @c.us e @lid
        if (number.includes('@c.us') || number.includes('@lid')) {
            // Usar diretamente se já formatado
            chatId = number;
        } else {
            // Validar número se não formatado
            const numberId = await client.getNumberId(number);

            if (!numberId) {
                return res.status(404).json({
                    error: 'Número não encontrado',
                    details: 'Este número não está registrado no WhatsApp'
                });
            }

            chatId = numberId._serialized;
        }

        // Enviar mensagem
        await client.sendMessage(chatId, message);

        res.json({
            status: 'success',
            message: 'Mensagem enviada com sucesso',
            to: number
        });
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        res.status(500).json({
            error: 'Erro ao enviar mensagem',
            details: error.message
        });
    }
});
```

**O que mudou:**
1. Detecta se número já tem `@c.us` ou `@lid`
2. Se sim, usa diretamente
3. Se não, valida via `getNumberId()`
4. Evita erro "Evaluation failed" ao enviar para `@lid`

---

### 6. POST /logout - Desconectar

```bash
curl -X POST http://localhost:9000/logout
```

**Efeito:**
- Desconecta do WhatsApp
- Apaga sessão salva
- Próximo restart pedirá novo QR Code

---

## 🔄 Fluxo de Mensagens

### Receber Mensagem

```
1. WhatsApp Web → WhatsApp Web.js
   └─ message.from = "5511999999999@c.us" (ou @lid)
   └─ message.body = "Oi, quero agendar"

2. WhatsApp Web.js → POST http://bot:5000/webhook
   └─ Payload JSON: {from, body, timestamp, hasMedia, type}

3. Bot FastAPI → Processa mensagem
   └─ Buffer de 13 segundos
   └─ Processa com agente Gabi
   └─ Gera resposta

4. Bot FastAPI → POST http://whatsapp:3000/send
   └─ {number: "5511999999999@c.us", message: "Resposta..."}

5. WhatsApp Web.js → WhatsApp Web → Cliente
   └─ Mensagem enviada em partes (micro mensagens)
```

---

## 🔐 Autenticação e Sessão

### LocalAuth

```javascript
authStrategy: new LocalAuth({
    dataPath: './wwebjs_auth'
})
```

**Volume Docker:**
```yaml
volumes:
  - whatsapp_auth:/app/wwebjs_auth
```

**Persistência:**
- Sessão salva no volume `whatsapp_auth`
- Sobrevive a reinicializações
- QR Code só necessário na primeira vez ou se expirar

---

### Quando QR Code Expira

**Causas:**
- WhatsApp desconectado manualmente no celular
- Sessão inativa por muito tempo (~14 dias)
- WhatsApp Web desvinculado

**Solução:**
1. Acessar `http://localhost:9000`
2. Escanear novo QR Code
3. Sessão será restaurada automaticamente

---

## 🧪 Testes

### Teste 1: Verificar Conexão

```bash
# Ver se está conectado
curl http://localhost:9000/status

# Esperado: {"connected": true, "ready": true}
```

---

### Teste 2: Enviar Mensagem Teste

```bash
# Substituir 5511999999999 pelo seu número (com @c.us ou @lid)
curl -X POST http://localhost:9000/send \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999@c.us",
    "message": "Teste de mensagem do bot!"
  }'
```

**Esperado:** Mensagem chega no WhatsApp.

---

### Teste 3: Simular Webhook

```bash
# Enviar mensagem fake para o bot
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "from": "5511999999999@c.us",
    "body": "Oi, quanto custa a lavagem?",
    "timestamp": "1234567890",
    "hasMedia": false,
    "type": "chat"
  }'
```

**Esperado:** Bot processa e envia resposta.

---

## 📊 Logs Importantes

### Conexão Bem-Sucedida

```
QR Code recebido! Escaneie com WhatsApp:
(QR code no terminal)
✅ Autenticação bem-sucedida!
✅ WhatsApp conectado com sucesso!
```

---

### Mensagem Recebida

```
📨 Mensagem recebida: 5511999999999@c.us - Oi, quero agendar
```

---

### Erro de Conexão

```
❌ Falha na autenticação: Session timed out
⚠️ Cliente desconectado: UNPAIRED
```

**Solução:** Escanear novo QR Code.

---

## ⚠️ Troubleshooting

### Container não inicia

```bash
# Ver logs
docker compose logs whatsapp

# Erro comum: "Navigation timeout"
# Solução: Aumentar shm_size no docker-compose.yml
shm_size: '2gb'
```

---

### QR Code não aparece

```bash
# Verificar logs
docker compose logs whatsapp | grep -i qr

# Verificar se Puppeteer iniciou
docker compose logs whatsapp | grep -i puppeteer

# Solução: Rebuild do container
docker compose build --no-cache whatsapp
docker compose up -d whatsapp
```

---

### Mensagens não chegam no bot

```bash
# Verificar webhook está configurado
docker compose logs whatsapp | grep WEBHOOK_URL

# Deve mostrar: WEBHOOK_URL=http://bot:5000/webhook

# Testar conectividade
docker exec vanlu_whatsapp curl -X GET http://bot:5000/health
```

---

### Erro ao enviar mensagens

**Erro:**
```
Evaluation failed: t
HTTP 500 - Internal server error
```

**Causa:** Tentando enviar para `@lid` sem suporte.

**Solução:** Já corrigido no código (linhas 268-302 de server.js).

---

### Sessão perdida após restart

```bash
# Verificar volume
docker volume ls | grep whatsapp_auth

# Se não existir, criar
docker volume create vanlu-agente_whatsapp_auth

# Reiniciar
docker compose down
docker compose up -d
```

---

## 🔧 Configurações Avançadas

### Alterar Porta

```yaml
# docker-compose.yml
whatsapp:
  ports:
    - "9001:3000"  # Usar porta 9001 no host
```

---

### Webhook Customizado

```yaml
# docker-compose.yml
whatsapp:
  environment:
    - WEBHOOK_URL=http://meu-servidor:8080/webhook
```

---

### Aumentar Timeout

```javascript
// server.js
client = new Client({
    puppeteer: {
        timeout: 60000  // 60 segundos (padrão: 30)
    }
});
```

---

## 📱 Formatos de Número

### @c.us (tradicional)

```
5511999999999@c.us
```

**Uso:** Números normais do WhatsApp.

---

### @lid (Local ID)

```
179839223001153@lid
```

**Uso:** Novo formato do WhatsApp (2024+).

**Importante:** Ambos são suportados pelo sistema.

---

### @g.us (grupos)

```
120363027461784242@g.us
```

**Uso:** Grupos do WhatsApp.

**Importante:** Bot **IGNORA** mensagens de grupos (configurado no main.py).

---

## ✅ Checklist de Funcionamento

- [ ] Container whatsapp está UP
- [ ] QR Code aparece em localhost:9000
- [ ] WhatsApp foi escaneado e conectado
- [ ] Status mostra "connected": true
- [ ] Mensagens de teste chegam no WhatsApp
- [ ] Webhook envia mensagens para o bot
- [ ] Bot consegue enviar respostas
- [ ] Suporte a @c.us e @lid funcionando
- [ ] Sessão persiste após restart

---

## 📚 Próximos Passos

**[04-BOT.md](./04-BOT.md)** → Configuração do bot Python (FastAPI)

---

**Status:** ✅ WhatsApp Web.js configurado e funcional
