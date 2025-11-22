# 📚 Documentação Completa - SPDrop WhatsApp Bot

Sistema completo de atendimento automatizado via WhatsApp usando IA (GPT-4.1-mini) com integração ao PostgreSQL.

## 🎯 Visão Geral

**SPDrop WhatsApp Bot** é um sistema de vendas automatizado que:
- ✅ Recebe mensagens do WhatsApp
- ✅ Processa com agente IA (Gabi - Especialista em Vendas)
- ✅ Armazena conversas e contexto no PostgreSQL
- ✅ Responde automaticamente com técnicas de vendas
- ✅ Suporta múltiplos clientes simultaneamente
- ✅ Buffer de mensagens (13s) para juntar mensagens fracionadas
- ✅ Envio de respostas em partes (micro mensagens) com delays

---

## 📋 Índice da Documentação

1. **[00-REQUISITOS.md](./00-REQUISITOS.md)** - Requisitos e pré-requisitos
2. **[01-SETUP-INICIAL.md](./01-SETUP-INICIAL.md)** - Instalação do Docker e configuração inicial
3. **[02-DATABASE.md](./02-DATABASE.md)** - Configuração do PostgreSQL e criação de tabelas
4. **[03-WHATSAPP.md](./03-WHATSAPP.md)** - Configuração do WhatsApp Web.js
5. **[04-BOT.md](./04-BOT.md)** - Configuração do bot Python (FastAPI)
6. **[05-AGENTE.md](./05-AGENTE.md)** - Configuração do agente de IA (Gabi)
7. **[06-TOOLS.md](./06-TOOLS.md)** - Ferramentas (FAQ, Memory, Scripts)
8. **[07-INTEGRACAO.md](./07-INTEGRACAO.md)** - Integração completa dos componentes
9. **[08-BUGS-CORRIGIDOS.md](./08-BUGS-CORRIGIDOS.md)** - Histórico de bugs e soluções
10. **[09-TROUBLESHOOTING.md](./09-TROUBLESHOOTING.md)** - Solução de problemas comuns
11. **[10-ARQUITETURA.md](./10-ARQUITETURA.md)** - Arquitetura do sistema

---

## 🚀 Quick Start

```bash
# 1. Clone ou acesse o projeto
cd "/home/paulo/Projeto/Vanlu agente"

# 2. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 3. Inicie todos os serviços
docker compose up -d

# 4. Acesse o QR Code do WhatsApp
http://localhost:9000

# 5. Escaneie com WhatsApp
# Aguarde "✅ WhatsApp conectado com sucesso!"

# 6. Teste enviando mensagem para o número conectado
```

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐
│   WhatsApp      │ ← Usuários enviam mensagens
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ WhatsApp Web.js │ ← Container Node.js (porta 9000)
│  (whatsapp)     │
└────────┬────────┘
         │ HTTP POST (webhook)
         ↓
┌─────────────────┐
│   FastAPI Bot   │ ← Container Python (porta 5000)
│     (bot)       │   - Recebe mensagens
└────────┬────────┘   - Buffer de 13s
         │            - Processa com agente
         ↓            - Divide respostas
┌─────────────────┐
│  Agente Gabi    │ ← GPT-4.1-mini + Tools
│   (support)     │   - FAQ Tool
└────────┬────────┘   - Memory Tool
         │            - Scripts Tool
         ↓
┌─────────────────┐
│  PostgreSQL     │ ← Container Postgres (porta 5432)
│   (postgres)    │   - Conversas
└─────────────────┘   - Clientes
                      - Scripts (110)
                      - FAQ (9)
```

---

## 📦 Componentes

### 1. **WhatsApp Service** (Node.js)
- Biblioteca: `whatsapp-web.js`
- Função: Conectar ao WhatsApp e receber/enviar mensagens
- Porta: 9000
- QR Code: `http://localhost:9000`

### 2. **Bot Service** (Python/FastAPI)
- Framework: FastAPI + Uvicorn
- Função: Processar mensagens e coordenar agente
- Porta: 5000
- Webhook: `http://localhost:5000/webhook`

### 3. **PostgreSQL Database**
- Versão: 14-alpine
- Função: Armazenar conversas, clientes, scripts, FAQ
- Porta: 5432
- Banco: `vanlu_db`

### 4. **Agente Gabi** (Agno + OpenAI)
- Modelo: GPT-4.1-mini
- Framework: Agno
- Tools: FAQ, Memory, Conversation Scripts
- Prompt: 11.665 caracteres com técnicas de vendas

---

## 🔧 Tecnologias

- **Docker & Docker Compose** - Orquestração de containers
- **Python 3.10** - Linguagem principal do bot
- **FastAPI** - Framework web para webhooks
- **Node.js 18** - Runtime para WhatsApp Web.js
- **PostgreSQL 14** - Banco de dados
- **Agno** - Framework de agentes IA
- **OpenAI GPT-4.1-mini** - Modelo de linguagem
- **WhatsApp Web.js** - Biblioteca para WhatsApp

---

## 📊 Dados do Sistema

### Tabelas do Banco:
- `customers` - Cadastro de clientes
- `sessions` - Sessões de conversa
- `conversation_history` - Histórico completo
- `customer_context` - Contexto e notas dos clientes
- `conversation_scripts` - 110 scripts de vendas
- `spdrop_faq` - 9 perguntas frequentes (CSV)

### Volumes Docker:
- `postgres_data` - Dados persistentes do PostgreSQL
- `wwebjs_auth` - Sessão do WhatsApp Web

---

## 🎓 Como Usar Esta Documentação

1. **Iniciantes:** Siga os documentos na ordem (00 → 10)
2. **Experientes:** Vá direto para o componente desejado
3. **Problemas:** Consulte [09-TROUBLESHOOTING.md](./09-TROUBLESHOOTING.md)
4. **Bugs:** Veja [08-BUGS-CORRIGIDOS.md](./08-BUGS-CORRIGIDOS.md)

---

## 📝 Convenções

- 📌 **Importante** - Informação crítica
- ⚠️ **Atenção** - Cuidado especial
- ✅ **Sucesso** - Confirmação de etapa
- ❌ **Erro** - Problema identificado
- 🔧 **Correção** - Solução aplicada
- 💡 **Dica** - Sugestão útil

---

## 🤝 Contribuindo

Esta documentação foi criada baseada no desenvolvimento real do projeto e inclui todos os bugs encontrados e soluções aplicadas. Mantenha atualizada conforme novas features ou correções forem implementadas.

---

**Versão:** 1.0.0
**Última Atualização:** 19/11/2025
**Status:** ✅ 100% Funcional
