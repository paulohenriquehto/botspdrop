# 🏗️ FUNIL DA ESTRUTURA COMPLETA - Frontend + Backend + Banco de Dados

## Visão Geral

Este documento mostra a arquitetura completa do sistema SPDrop, incluindo todos os componentes: Frontend (React), Backend (FastAPI), Banco de Dados (PostgreSQL), Bot (Python) e integração WhatsApp.

---

## 🎯 ARQUITETURA GERAL

```
┌═══════════════════════════════════════════════════════════════┐
│                      👤 USUÁRIO FINAL                          │
│                    (Paulo no WhatsApp)                         │
└═══════════════════════════════════════════════════════════════┘
                             ↕
┌═══════════════════════════════════════════════════════════════┐
│                    📱 WHATSAPP WEB.JS                          │
│                  (Container: spdrop_whatsapp)                  │
│                       Porta: 9000                              │
├───────────────────────────────────────────────────────────────┤
│  • Recebe mensagens do WhatsApp                               │
│  • Envia webhook para BOT                                     │
│  • Envia respostas de volta                                   │
│  • Volume: whatsapp_auth (autenticação persistente)           │
│  • shm_size: 2GB (para Chromium)                              │
└═══════════════════════════════════════════════════════════════┘
                             ↕
┌═══════════════════════════════════════════════════════════════┐
│                      🤖 BOT (main.py)                          │
│                  (Container: spdrop_bot)                       │
│                       Porta: 5000                              │
├───────────────────────────────────────────────────────────────┤
│  RECEBE:                                                       │
│    POST /webhook                                               │
│    {from: "5511...", body: "Olá", timestamp: ...}             │
│                                                                │
│  PROCESSA:                                                     │
│    1. Buffer (13s)                    ← main.py:45            │
│    2. Normalizar telefone             ← customer_manager.py:30│
│    3. Buscar/criar cliente            ↓ SQL                   │
│    4. Recuperar contexto              ↓ SQL                   │
│    5. Criar session_id                ↓ SQL                   │
│    6. Buscar histórico                ↓ SQL                   │
│    7. Chamar Agente                   ← agente_suporte.py     │
│    8. Salvar conversa                 ↓ SQL                   │
│    9. Enviar resposta                 ↑ WhatsApp              │
│                                                                │
│  COMPONENTES:                                                  │
│    • customer_manager.py - Gestão de clientes                 │
│    • agentes/agente_suporte.py - IA (GPT-4.1 mini)            │
│    • tools/memory_tools.py - Ferramentas de memória           │
│    • whatsapp_integration.py - Cliente WhatsApp               │
└═══════════════════════════════════════════════════════════════┘
         ↕ SQL Queries                        ↕ HTTP
┌═══════════════════════════════════════════════════════════════┐
│                  🗄️ POSTGRESQL 16                             │
│                (Container: spdrop_postgres)                    │
│                      Porta: 5432                               │
├───────────────────────────────────────────────────────────────┤
│  BANCO: spdrop_db                                             │
│  USUÁRIO: spdrop_user                                         │
│  VOLUME: postgres_data (persistente)                          │
│                                                                │
│  CONFIGURAÇÕES:                                                │
│    • shared_buffers: 128 MB                                   │
│    • effective_cache_size: 4 GB                               │
│    • work_mem: 4 MB                                           │
│    • max_connections: 100                                     │
│    • autovacuum: ATIVO                                        │
│                                                                │
│  TABELAS (15):                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 👥 CLIENTES E CONTEXTO:                                 │ │
│  │  • customers - Cadastro de clientes                     │ │
│  │  • customer_context - Contexto empreendedor             │ │
│  │  • user_preferences - Preferências                      │ │
│  │  • trial_users - Testes grátis                          │ │
│  │                                                         │ │
│  │ 💬 CONVERSAS E MEMÓRIA:                                 │ │
│  │  • sessions - Sessões de conversa                       │ │
│  │  • conversation_history - Histórico completo            │ │
│  │  • message_logs - Log de mensagens                      │ │
│  │  • conversation_scripts - Scripts pré-definidos         │ │
│  │                                                         │ │
│  │ 📊 ANALYTICS:                                           │ │
│  │  • attendance_metrics - Métricas diárias                │ │
│  │  • audit_log - Log de auditoria                         │ │
│  │                                                         │ │
│  │ 🛒 DROPSHIPPING:                                        │ │
│  │  • products - Catálogo                                  │ │
│  │  • suppliers - Fornecedores                             │ │
│  │  • orders - Pedidos                                     │ │
│  │  • subscription_plans - Planos                          │ │
│  │                                                         │ │
│  │ 👨‍💼 ADMIN:                                              │ │
│  │  • admin_users - Usuários admin                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└═══════════════════════════════════════════════════════════════┘
         ↕ SQL Queries
┌═══════════════════════════════════════════════════════════════┐
│                  🔧 API BACKEND (FastAPI)                      │
│                  (Container: spdrop_api)                       │
│                      Porta: 8000                               │
├───────────────────────────────────────────────────────────────┤
│  ROTAS:                                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 🔐 AUTENTICAÇÃO (api/auth.py):                          │ │
│  │  • POST /api/auth/login - Login admin                   │ │
│  │  • GET  /api/auth/me - Dados do usuário logado          │ │
│  │  • POST /api/auth/logout - Logout                       │ │
│  │                                                         │ │
│  │ 📊 DASHBOARD (api/dashboard.py):                        │ │
│  │  • GET /api/dashboard/stats/summary - Resumo geral      │ │
│  │  • GET /api/dashboard/metrics/today - Métricas de hoje  │ │
│  │  • GET /api/dashboard/metrics/period - Período          │ │
│  │  • GET /api/dashboard/customers/recent - Clientes       │ │
│  │  • POST /api/dashboard/metrics/update - Atualizar       │ │
│  │                                                         │ │
│  │ 💬 CONVERSAS (api/conversations.py):                    │ │
│  │  • GET /api/conversations/history/{id} - Histórico      │ │
│  │  • GET /api/conversations/recent - Recentes             │ │
│  │  • GET /api/conversations/grouped - Agrupadas           │ │
│  │  • GET /api/conversations/trials/active - Trials ativos │ │
│  │  • GET /api/conversations/trials/expired - Expirados    │ │
│  │  • GET /api/conversations/trials/{id} - Detalhes        │ │
│  │  • PATCH /api/conversations/trials/{id}/status - Status │ │
│  │  • POST /api/conversations/trials/{id}/convert - Conver │ │
│  │                                                         │ │
│  │ 📱 QR CODE (api/qrcode.py):                             │ │
│  │  • GET  /api/qrcode/generate - Gerar QR Code            │ │
│  │  • GET  /api/qrcode/status - Status da conexão          │ │
│  │  • POST /api/qrcode/disconnect - Desconectar            │ │
│  │  • POST /api/qrcode/restart - Reiniciar                 │ │
│  │  • GET  /api/qrcode/health - Health check               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
│  SEGURANÇA:                                                    │
│    • JWT Authentication                                        │
│    • CORS habilitado (allow_origins: *)                       │
│    • Token expira em 8 horas                                  │
└═══════════════════════════════════════════════════════════════┘
         ↕ HTTP/REST API
┌═══════════════════════════════════════════════════════════════┐
│                  💻 FRONTEND (React + Vite)                    │
│                   (Vite Dev Server)                            │
│                      Porta: 3002                               │
├───────────────────────────────────────────────────────────────┤
│  TECNOLOGIAS:                                                  │
│    • React 18                                                  │
│    • Vite (dev server)                                         │
│    • Tailwind CSS                                              │
│    • Axios (HTTP client)                                       │
│    • React Router                                              │
│    • date-fns (formatação de datas)                            │
│    • Lucide React (ícones)                                     │
│                                                                │
│  PÁGINAS:                                                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 🏠 / - Dashboard                                        │ │
│  │   • Cards de métricas principais                        │ │
│  │   • Métricas de hoje (5 cards)                          │ │
│  │   • Clientes recentes (tabela)                          │ │
│  │   • Auto-refresh 30s                                    │ │
│  │   • Arquivo: src/pages/Dashboard.jsx                    │ │
│  │                                                         │ │
│  │ 💬 /conversations - Conversas                           │ │
│  │   • Layout WhatsApp-style                               │ │
│  │   • Agrupadas por cliente                               │ │
│  │   • Expandir/Recolher                                   │ │
│  │   • Busca em tempo real                                 │ │
│  │   • Auto-refresh 15s                                    │ │
│  │   • Arquivo: src/pages/Conversations.jsx                │ │
│  │                                                         │ │
│  │ 🧪 /trials - Testes Grátis                             │ │
│  │   • Lista de trials ativos                              │ │
│  │   • Status e dias restantes                             │ │
│  │   • Ações: converter, cancelar                          │ │
│  │   • Arquivo: src/pages/Trials.jsx                       │ │
│  │                                                         │ │
│  │ 📱 /qrcode - QR Code WhatsApp                          │ │
│  │   • Gerar/exibir QR Code                                │ │
│  │   • Status da conexão                                   │ │
│  │   • Reconnect/Restart                                   │ │
│  │   • Arquivo: src/pages/QRCode.jsx                       │ │
│  │                                                         │ │
│  │ 🔐 /login - Login Admin                                │ │
│  │   • Autenticação JWT                                    │ │
│  │   • Formulário de login                                 │ │
│  │   • Arquivo: src/pages/Login.jsx                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
│  SERVIÇOS (src/services/api.js):                              │
│    • authAPI - Autenticação                                    │
│    • dashboardAPI - Dashboard                                  │
│    • conversationsAPI - Conversas e Trials                     │
│    • qrcodeAPI - QR Code                                       │
│                                                                │
│  CONFIGURAÇÃO:                                                 │
│    • API_URL: http://localhost:8000                            │
│    • Proxy: /api → http://localhost:8000                       │
│    • Interceptors: Auto JWT token                              │
└═══════════════════════════════════════════════════════════════┘
                             ↕
┌═══════════════════════════════════════════════════════════════┐
│                   👨‍💼 ADMIN (Navegador)                        │
│              http://localhost:3002                             │
│                                                                │
│  USUÁRIO: admin                                                │
│  SENHA: Admin@123456                                           │
└═══════════════════════════════════════════════════════════════┘
```

---

## 🔄 FLUXO DE DADOS

### 1. Cliente WhatsApp → Bot → Banco

```
Cliente WhatsApp
    ↓ mensagem
WhatsApp Web.js (porta 9000)
    ↓ POST /webhook
Bot (porta 5000)
    ↓ SQL queries
PostgreSQL (porta 5432)
```

### 2. Admin Dashboard → API → Banco

```
Admin (navegador)
    ↓ http://localhost:3002
React Frontend
    ↓ GET /api/...
FastAPI Backend (porta 8000)
    ↓ SQL queries
PostgreSQL (porta 5432)
```

---

## 🐳 CONTAINERS DOCKER

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: spdrop_postgres
    ports: ["5432:5432"]
    volumes:
      - postgres_data:/var/lib/postgresql/data

  whatsapp:
    container_name: spdrop_whatsapp
    ports: ["9000:3000"]
    volumes:
      - whatsapp_auth:/app/wwebjs_auth
    shm_size: '2gb'

  bot:
    container_name: spdrop_bot
    ports: ["5000:5000"]
    depends_on: [postgres, whatsapp]

  api:
    container_name: spdrop_api
    ports: ["8000:8000"]
    depends_on: [postgres]
```

---

## 🔌 PORTAS E ENDPOINTS

| Serviço          | Porta | URL                       | Descrição           |
|------------------|-------|---------------------------|---------------------|
| Frontend (Vite)  | 3002  | http://localhost:3002     | Interface admin     |
| Bot (FastAPI)    | 5000  | http://localhost:5000     | Webhook WhatsApp    |
| API (FastAPI)    | 8000  | http://localhost:8000     | REST API            |
| WhatsApp Web.js  | 9000  | http://localhost:9000     | WhatsApp service    |
| PostgreSQL       | 5432  | postgres://localhost:5432 | Banco de dados      |

---

## 📁 ESTRUTURA DE ARQUIVOS

```
/Spdrop
├── frontend/                    # React + Vite
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # 🏠 Home
│   │   │   ├── Conversations.jsx # 💬 Conversas
│   │   │   ├── Trials.jsx       # 🧪 Testes
│   │   │   ├── QRCode.jsx       # 📱 QR Code
│   │   │   └── Login.jsx        # 🔐 Login
│   │   ├── services/
│   │   │   └── api.js           # Axios + endpoints
│   │   └── components/          # Componentes reutilizáveis
│   └── vite.config.js
│
├── api/                         # FastAPI Backend
│   ├── __init__.py
│   ├── auth.py                  # 🔐 Autenticação
│   ├── dashboard.py             # 📊 Dashboard
│   ├── conversations.py         # 💬 Conversas
│   ├── qrcode.py                # 📱 QR Code
│   └── database.py              # 🗄️ Conexão DB
│
├── agentes/
│   └── agente_suporte.py        # 🤖 Agente IA
│
├── tools/
│   └── memory_tools.py          # 🧠 Memória/Contexto
│
├── main.py                      # 🤖 Bot principal
├── customer_manager.py          # 👥 Gestão clientes
├── whatsapp_integration.py      # 📱 WhatsApp client
├── api_server.py                # 🔧 API server
├── init.sql                     # 🗄️ Schema do banco
└── docker-compose.yml           # 🐳 Orquestração
```

---

## 🔐 SEGURANÇA

### Autenticação

- **JWT Tokens** (8 horas de validade)
- **Bcrypt** para hash de senhas
- **Interceptors** automáticos no frontend

### CORS

- Backend: `allow_origins: ["*"]`
- Frontend Proxy: `/api` → `http://localhost:8000`

### Banco de Dados

- **Foreign Keys** garantindo integridade
- **Índices** otimizados (session_id, customer_id, timestamp)
- **Backup** via Docker volumes persistentes

---

## 📊 MÉTRICAS E MONITORAMENTO

### Dashboard Cards

1. **Total de Clientes**: COUNT(customers)
2. **Testes Ativos**: COUNT(trial_users WHERE status='active')
3. **Conversões**: COUNT(trial_users WHERE status='converted')
4. **Mensagens 24h**: COUNT(message_logs WHERE timestamp > NOW() - 24h)

### Métricas de Hoje

1. **Conversas**: COUNT(DISTINCT session_id)
2. **Trials Solicitados**: COUNT(trial_users WHERE created_at::date = TODAY)
3. **Conversões**: COUNT(conversions WHERE date = TODAY)
4. **Msgs Enviadas**: COUNT(message_logs WHERE direction='outbound')
5. **Msgs Recebidas**: COUNT(message_logs WHERE direction='inbound')

---

## 🚀 DEPLOY

### Desenvolvimento

```bash
# Backend API
cd /Spdrop
python api_server.py

# Frontend
cd frontend
npm run dev

# Bot
python main.py

# Docker
docker-compose up -d
```

### Produção

```bash
docker-compose up -d
```

---

## 📝 LOGS

### Bot
```bash
docker logs spdrop_bot -f
```

### API
```bash
docker logs spdrop_api -f
```

### PostgreSQL
```bash
docker logs spdrop_postgres -f
```

---

## 🔄 BACKUP

### Banco de Dados

```bash
docker exec spdrop_postgres pg_dump -U spdrop_user spdrop_db > backup.sql
```

### Restaurar

```bash
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < backup.sql
```

---

## 📞 SUPORTE

- **Documentação Bot**: FUNIL_BOT.md
- **Documentação Conversas**: README_CONVERSATIONS.md
- **Diagnóstico**: DIAGNOSTICO_COMPLETO.md

---

**Data de criação**: 19/11/2025
**Versão**: 1.0
**Arquitetura**: Microserviços (Docker Compose)
