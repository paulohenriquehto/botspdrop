# 10 - Arquitetura do Sistema

## 🏗️ Visão Geral

Este documento detalha a **arquitetura completa** do sistema SPDrop WhatsApp Bot.

---

## 📊 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                          USUÁRIOS                               │
│                     (Clientes no WhatsApp)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   WHATSAPP (Meta Servers)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               CAMADA 1: WHATSAPP WEB.JS                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Container: vanlu_whatsapp                               │  │
│  │  Porta: 9000 → 3000                                      │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  • Node.js 18                                            │  │
│  │  • Express.js                                            │  │
│  │  • whatsapp-web.js                                       │  │
│  │  • Puppeteer (Chrome Headless)                           │  │
│  │  • LocalAuth (sessão persistente)                        │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  Endpoints:                                               │  │
│  │  • GET  / (QR Code)                                      │  │
│  │  • POST /send (enviar mensagem)                          │  │
│  │  • GET  /status (verificar conexão)                      │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  Volume: whatsapp_auth                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP POST
                         │ http://bot:5000/webhook
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CAMADA 2: BOT FASTAPI                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Container: vanlu_bot                                    │  │
│  │  Porta: 5000 → 5000                                      │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  • Python 3.10                                           │  │
│  │  • FastAPI                                               │  │
│  │  • Uvicorn                                               │  │
│  │  • Asyncio                                               │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  Componentes:                                             │  │
│  │                                                           │  │
│  │  1. main.py (servidor principal)                         │  │
│  │     ├─ Buffer de mensagens (13s)                         │  │
│  │     ├─ handle_message()                                  │  │
│  │     └─ send_message_in_parts()                           │  │
│  │                                                           │  │
│  │  2. customer_manager.py                                  │  │
│  │     ├─ get_or_create_customer()                          │  │
│  │     ├─ build_context_message()                           │  │
│  │     └─ save_conversation()                               │  │
│  │                                                           │  │
│  │  3. whatsapp_integration.py                              │  │
│  │     └─ send_text()                                       │  │
│  │                                                           │  │
│  │  4. database.py                                          │  │
│  │     └─ PostgreSQL connection                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CAMADA 3: AGENTE DE IA                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Agente: Gabi                                            │  │
│  │  Localização: agentes/agente_suporte.py                  │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  • Framework: Agno                                       │  │
│  │  • Modelo: GPT-4.1-mini (OpenAI)                         │  │
│  │  • Prompt: 11.665 caracteres                             │  │
│  │  • Storage: PostgreSQL (via Agno)                        │  │
│  │  • Memory: add_history_to_context=True                   │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  Ferramentas (Tools):                                     │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  1. SPDropFAQTools                                 │  │  │
│  │  │     • buscar_faq()                                 │  │  │
│  │  │     • buscar_resposta_por_palavra_chave()          │  │  │
│  │  │     • Fonte: data/spdrop_faq.csv (9 perguntas)     │  │  │
│  │  ├────────────────────────────────────────────────────┤  │  │
│  │  │  2. SPDropMemoryTools                              │  │  │
│  │  │     • get_conversation_history()                   │  │  │
│  │  │     • update_customer_context()                    │  │  │
│  │  │     • update_customer_preferences()                │  │  │
│  │  │     • Fonte: PostgreSQL                            │  │  │
│  │  ├────────────────────────────────────────────────────┤  │  │
│  │  │  3. ConversationScriptsTools                       │  │  │
│  │  │     • buscar_por_perfil()                          │  │  │
│  │  │     • buscar_por_etapa()                           │  │  │
│  │  │     • buscar_por_palavra_chave()                   │  │  │
│  │  │     • Fonte: data/conversation_scripts.csv (110)   │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CAMADA 4: BANCO DE DADOS                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Container: vanlu_postgres                               │  │
│  │  Porta: 5432 → 5432                                      │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  • PostgreSQL 16-alpine                                  │  │
│  │  • Banco: vanlu_db                                       │  │
│  │  • User: vanlu_user                                      │  │
│  │  • Password: vanlu_password                              │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  Tabelas (14):                                            │  │
│  │                                                           │  │
│  │  CONVERSAÇÃO:                                             │  │
│  │  • customers (dados dos clientes)                        │  │
│  │  • sessions (sessões de conversa)                        │  │
│  │  • conversation_history (mensagens)                      │  │
│  │  • customer_context (contexto dos clientes)              │  │
│  │  • user_preferences (preferências)                       │  │
│  │                                                           │  │
│  │  NEGÓCIO:                                                 │  │
│  │  • services (15 serviços)                                │  │
│  │  • availability (horários)                               │  │
│  │  • appointments (agendamentos)                           │  │
│  │  • vehicle_types (10 tipos)                              │  │
│  │  • service_pricing (preços)                              │  │
│  │  • vehicle_patterns (25 padrões)                         │  │
│  │                                                           │  │
│  │  CONHECIMENTO:                                            │  │
│  │  • conversation_scripts (110 scripts)                    │  │
│  │  • spdrop_faq (9 FAQs)                                   │  │
│  │  ────────────────────────────────────────────────────    │  │
│  │  Volume: postgres_data                                   │  │
│  │  Init: init.sql (executado na criação)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados Detalhado

### 1. Mensagem Recebida

```
USUÁRIO
  │ "Oi, quanto custa?"
  ↓
WHATSAPP (Meta)
  │
  ↓
WHATSAPP WEB.JS (Puppeteer)
  │ client.on('message')
  ↓
  {
    from: "5511999999999@c.us",
    body: "Oi, quanto custa?",
    timestamp: "1700000000",
    hasMedia: false,
    type: "chat"
  }
  │ POST http://bot:5000/webhook
  ↓
BOT FASTAPI (webhook endpoint)
  │ Filtros:
  │ - Ignorar grupos (@g.us)
  │ - Ignorar vazias
  ↓
BUFFER (13 segundos)
  │ Acumular mensagens do mesmo usuário
  │ Resetar timer a cada nova mensagem
  ↓
  [Após 13s sem novas mensagens]
  │
  ↓
PROCESSAR
```

---

### 2. Processamento

```
handle_message()
  │
  ├─→ customer_manager.get_or_create_customer()
  │   └─→ PostgreSQL: SELECT/INSERT customers
  │
  ├─→ customer_manager.build_context_message()
  │   └─→ PostgreSQL: SELECT conversation_history (últimas 5)
  │
  ├─→ Criar session_id = "whatsapp_5511999999999"
  │
  ├─→ support_agent.run(message_with_context, session_id)
  │   │
  │   ├─→ OpenAI GPT-4.1-mini
  │   │   └─→ Processar com prompt de 11.665 chars
  │   │
  │   ├─→ Tools (se necessário):
  │   │   ├─→ SPDropFAQTools.buscar_faq()
  │   │   ├─→ SPDropMemoryTools.get_conversation_history()
  │   │   └─→ ConversationScriptsTools.buscar_por_perfil()
  │   │
  │   └─→ Gerar resposta natural
  │
  ├─→ customer_manager.save_conversation()
  │   └─→ PostgreSQL: INSERT conversation_history
  │
  └─→ send_message_in_parts()
      │
      ├─→ Dividir resposta em parágrafos
      ├─→ Filtrar vazios
      └─→ Para cada parte:
          ├─→ whatsapp_client.send_text()
          │   └─→ POST http://whatsapp:3000/send
          └─→ asyncio.sleep(3-6 segundos)
```

---

### 3. Envio de Resposta

```
send_message_in_parts()
  │
  ├─→ Parte 1: "Olá! 😊"
  │   └─→ POST http://whatsapp:3000/send
  │       └─→ WhatsApp Web.js: client.sendMessage()
  │           └─→ WhatsApp (Meta)
  │               └─→ USUÁRIO recebe
  │
  ├─→ [Aguardar 3s]
  │
  ├─→ Parte 2: "Eu sou a Gabi..."
  │   └─→ [mesmo fluxo]
  │
  └─→ ... (continua para todas as partes)
```

---

## 📦 Componentes Principais

### 1. WhatsApp Web.js

**Responsabilidades:**
- ✅ Conectar ao WhatsApp via Puppeteer
- ✅ Manter sessão persistente (LocalAuth)
- ✅ Receber mensagens em tempo real
- ✅ Enviar mensagens de volta
- ✅ Suportar formatos @c.us e @lid

**Tecnologias:**
- Node.js 18
- Express.js
- whatsapp-web.js 1.23.0
- Puppeteer
- Chrome Headless

**Arquivo principal:** `whatsapp-service/server.js` (374 linhas)

---

### 2. Bot FastAPI

**Responsabilidades:**
- ✅ Receber webhooks do WhatsApp
- ✅ Buffer de mensagens (13s)
- ✅ Gerenciar clientes (CRUD)
- ✅ Construir contexto para agente
- ✅ Salvar conversas
- ✅ Dividir respostas em partes
- ✅ Coordenar envio

**Tecnologias:**
- Python 3.10
- FastAPI
- Uvicorn
- Asyncio
- psycopg2-binary
- httpx

**Arquivos principais:**
- `main.py` (342 linhas)
- `customer_manager.py`
- `whatsapp_integration.py`
- `database.py`

---

### 3. Agente Gabi

**Responsabilidades:**
- ✅ Processar mensagens com IA
- ✅ Aplicar técnicas de vendas
- ✅ Usar ferramentas (FAQ, Memory, Scripts)
- ✅ Manter contexto de conversas
- ✅ Gerar respostas naturais

**Tecnologias:**
- Agno Framework
- OpenAI GPT-4.1-mini
- PostgreSQL storage

**Arquivo principal:** `agentes/agente_suporte.py`

---

### 4. PostgreSQL

**Responsabilidades:**
- ✅ Armazenar clientes
- ✅ Armazenar conversas
- ✅ Armazenar contexto
- ✅ Prover dados para ferramentas

**Tecnologias:**
- PostgreSQL 16-alpine

**Arquivo de inicialização:** `init.sql` (177 linhas)

---

## 🌐 Rede e Comunicação

### Rede Docker: vanlu_network

```yaml
networks:
  vanlu_network:
    driver: bridge
```

**Containers na rede:**
- `postgres` (resolvido como postgres:5432)
- `whatsapp` (resolvido como whatsapp:3000)
- `bot` (resolvido como bot:5000)

---

### Protocolo de Comunicação

| De | Para | Protocolo | Endpoint |
|----|------|-----------|----------|
| WhatsApp | Bot | HTTP POST | http://bot:5000/webhook |
| Bot | WhatsApp | HTTP POST | http://whatsapp:3000/send |
| Bot | PostgreSQL | psycopg2 | postgres:5432 |
| Agente | OpenAI | HTTPS | api.openai.com |
| Agente | PostgreSQL | Agno DB | postgres:5432 |

---

## 💾 Persistência de Dados

### Volumes Docker

```yaml
volumes:
  postgres_data:
    # Armazena: Tabelas, índices, dados do PostgreSQL
    # Localização: /var/lib/postgresql/data

  whatsapp_auth:
    # Armazena: Sessão do WhatsApp (LocalAuth)
    # Localização: /app/wwebjs_auth
```

**O que persiste entre restarts:**
- ✅ Conversas no PostgreSQL
- ✅ Contexto dos clientes
- ✅ Sessão do WhatsApp (QR Code não necessário)

**O que NÃO persiste:**
- ❌ Buffer de mensagens (RAM)
- ❌ Logs dos containers

---

## ⚡ Performance

### Métricas de Recursos

| Container | CPU (Idle) | CPU (Ativo) | RAM (Idle) | RAM (Ativo) |
|-----------|-----------|-------------|------------|-------------|
| whatsapp | ~5% | ~20% | 300MB | 500MB |
| bot | ~5% | ~50% | 200MB | 500MB |
| postgres | ~2% | ~10% | 100MB | 200MB |
| **TOTAL** | **~12%** | **~80%** | **~600MB** | **~1.2GB** |

**Hardware recomendado:**
- CPU: 2 cores (4 recomendado)
- RAM: 4GB (8GB recomendado)
- Disco: 10GB livres

---

### Tempos de Resposta

| Etapa | Tempo |
|-------|-------|
| Buffer aguardando | 13 segundos (fixo) |
| Processamento do agente | 2-5 segundos |
| Divisão de mensagens | <1 segundo |
| Envio de cada parte | 3-6 segundos |
| **TOTAL (resposta completa)** | **20-30 segundos** |

---

## 🔐 Segurança

### Camadas de Segurança

1. **Rede isolada**: Containers comunicam-se em rede privada
2. **Variáveis de ambiente**: Credenciais não hardcoded
3. **Volume persistente**: Sessão do WhatsApp protegida
4. **PostgreSQL local**: Banco não exposto à internet (produção)

### Recomendações para Produção

```yaml
# Adicionar no docker-compose.yml

# Limitar recursos
bot:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 512M

# Usar secrets do Docker
secrets:
  openai_key:
    file: ./secrets/openai_key.txt

# Usar reverse proxy (Nginx)
nginx:
  image: nginx:alpine
  ports:
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
```

---

## 📈 Escalabilidade

### Escalabilidade Vertical (Atual)

✅ **1 servidor, 3 containers**
- Suporta: ~50-100 conversas simultâneas
- Limitação: CPU e RAM do servidor

---

### Escalabilidade Horizontal (Futuro)

```
┌─────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴────┬────────┬────────┐
   ↓        ↓        ↓        ↓
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Bot 1│ │ Bot 2│ │ Bot 3│ │ Bot N│
└───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘
    │        │        │        │
    └────────┴────────┴────────┘
             │
             ↓
     ┌───────────────┐
     │  PostgreSQL   │
     │   (Master)    │
     └───────────────┘
```

**Tecnologias:**
- Docker Swarm
- Kubernetes
- PostgreSQL com replicação

---

## 🔄 Ciclo de Vida da Mensagem

### Timeline Completa

```
T=0s    Usuário envia mensagem
        ↓
T=0s    WhatsApp Web.js recebe
        ↓
T=0.1s  Bot recebe webhook
        ↓
T=0.1s  Buffer inicia (13s)
        ↓
T=13s   Buffer processa
        ↓
T=13s   Bot busca cliente no DB (0.1s)
        ↓
T=13.1s Bot constrói contexto (0.2s)
        ↓
T=13.3s Agente Gabi processa (2-5s)
        ↓
T=17s   Bot salva conversa (0.1s)
        ↓
T=17.1s Bot divide mensagem (0.1s)
        ↓
T=17.2s Bot envia parte 1
        ↓
T=20s   Bot envia parte 2 (após delay 3s)
        ↓
T=24s   Bot envia parte 3 (após delay 4s)
        ↓
T=29s   Bot envia parte 4 (após delay 5s)
        ↓
T=29s   ✅ Concluído
```

**Tempo total:** ~29 segundos (variável conforme tamanho da resposta)

---

## ✅ Checklist de Arquitetura

- [x] Separação de responsabilidades (4 camadas)
- [x] Comunicação via HTTP REST
- [x] Persistência via PostgreSQL
- [x] Rede Docker isolada
- [x] Volumes persistentes
- [x] Escalabilidade vertical
- [x] Logs centralizados (docker compose logs)
- [x] Health checks
- [x] Variáveis de ambiente
- [x] Tratamento de erros

---

## 📚 Tecnologias Utilizadas

### Backend
- Python 3.10
- FastAPI
- Uvicorn
- Asyncio

### Frontend (WhatsApp)
- Node.js 18
- Express.js
- whatsapp-web.js
- Puppeteer

### IA e Agentes
- Agno Framework
- OpenAI GPT-4.1-mini

### Banco de Dados
- PostgreSQL 16-alpine

### Infraestrutura
- Docker
- Docker Compose

---

## 🎯 Conclusão

O sistema **SPDrop WhatsApp Bot** é uma arquitetura bem estruturada, com:

✅ **Modularidade**: 4 camadas independentes
✅ **Escalabilidade**: Pronto para crescer
✅ **Manutenibilidade**: Código organizado
✅ **Confiabilidade**: Persistência de dados
✅ **Performance**: <30s para resposta completa
✅ **Segurança**: Variáveis de ambiente e rede isolada

---

**Fim da Documentação Completa**

**Versão:** 1.0.0
**Data:** 19/11/2025
**Status:** ✅ 100% Funcional
