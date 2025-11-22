# 🤖 SPDrop - WhatsApp Bot com IA

Sistema completo de atendimento via WhatsApp com inteligência artificial integrada, desenvolvido para automatizar vendas e suporte de dropshipping.

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/u/paulo003)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai&logoColor=white)](https://openai.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

---

## 📋 Índice

- [Features](#-features)
- [Arquitetura](#-arquitetura)
- [Stack Tecnológica](#-stack-tecnológica)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação Rápida](#-instalação-rápida)
- [Configuração](#-configuração)
- [Deploy em Produção](#-deploy-em-produção)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [Documentação Completa](#-documentação-completa)
- [Licença](#-licença)

---

## ✨ Features

### 🤖 Inteligência Artificial
- ✅ **GPT-4o-mini** - Conversação natural e contextual
- ✅ **Groq Whisper** - Transcrição de áudios em tempo real
- ✅ **OpenAI Vision** - Análise de imagens enviadas
- ✅ **Sistema de Tools** - FAQ, Trial, Demo Account automatizados
- ✅ **Memória de Conversas** - Contexto persistente por cliente

### 💬 WhatsApp
- ✅ **WhatsApp Web.js** - Integração oficial
- ✅ **QR Code** - Autenticação simplificada
- ✅ **Mensagens em Tempo Real** - Resposta instantânea
- ✅ **Suporte a Mídias** - Áudio, imagem, vídeo, documentos

### 📊 Dashboard Administrativo
- ✅ **Painel React** - Interface moderna e responsiva
- ✅ **Gestão de Clientes** - Visualização completa
- ✅ **Histórico de Conversas** - Todas as interações salvas
- ✅ **Métricas em Tempo Real** - Analytics de atendimento
- ✅ **Gestão de Trials** - Controle de períodos gratuitos

### 🔒 Segurança
- ✅ **Nginx Reverse Proxy** - Gateway único
- ✅ **Rate Limiting** - Proteção DDoS
- ✅ **CORS Restritivo** - Apenas origens autorizadas
- ✅ **JWT Authentication** - API segura
- ✅ **Endpoints Bloqueados** - Proteção de rotas sensíveis

### 🐳 DevOps
- ✅ **Docker Compose** - Deploy com 1 comando
- ✅ **Imagens no Docker Hub** - Versionamento v1.1
- ✅ **Network Isolation** - Microserviços isolados
- ✅ **Health Checks** - Monitoramento automático
- ✅ **Auto Restart** - Alta disponibilidade

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    INTERNET (Port 80)                    │
└────────────────────────┬────────────────────────────────┘
                         │
                    ┌────▼─────┐
                    │  NGINX   │ Rate Limiting + CORS
                    │ Gateway  │ Reverse Proxy
                    └────┬─────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌───▼────┐      ┌───▼────────┐
   │   API   │      │  Bot   │      │  WhatsApp  │
   │ FastAPI │      │ Python │◄─────┤  Node.js   │
   └────┬────┘      └───┬────┘      └────────────┘
        │               │
        │          ┌────▼─────┐
        └─────────►│PostgreSQL│
                   │    DB    │
                   └──────────┘

           Docker Bridge Network (Interno)
```

### Fluxo de Dados

1. **Cliente → WhatsApp** - Envia mensagem
2. **WhatsApp → Bot** - Webhook POST /webhook
3. **Bot → CustomerManager** - Busca/cria cliente no PostgreSQL
4. **Bot → OpenAI** - Processa IA (GPT-4o-mini)
5. **Bot → Tools** - Executa ações (FAQ, Trial, etc.)
6. **Bot → WhatsApp** - Envia resposta
7. **WhatsApp → Cliente** - Entrega mensagem

---

## 🛠️ Stack Tecnológica

### Backend
- **Python 3.10** - Linguagem principal
- **FastAPI** - Framework web assíncrono
- **psycopg2** - Driver PostgreSQL
- **OpenAI SDK** - Integração GPT-4o-mini
- **Groq SDK** - Whisper para transcrição

### Frontend
- **React 18** - Framework UI
- **Vite** - Build tool moderna
- **TailwindCSS** - Estilização
- **React Router** - Navegação SPA

### WhatsApp
- **Node.js 18** - Runtime
- **whatsapp-web.js** - Biblioteca oficial
- **Puppeteer** - Browser automation

### Database
- **PostgreSQL 16** - Banco relacional
- **20+ Tabelas** - Estrutura completa

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração
- **Nginx** - Reverse proxy + rate limiting

---

## 📦 Pré-requisitos

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Conta OpenAI** - [Obter API Key](https://platform.openai.com/api-keys)
- **Conta Groq** - [Obter API Key](https://console.groq.com/keys)

---

## 🚀 Instalação Rápida

### 1. Clone o Repositório

```bash
git clone https://github.com/paulohenriquehto/botspdrop.git
cd botspdrop
```

### 2. Configure Variáveis de Ambiente

```bash
cp .env.example .env
nano .env
```

**Edite as seguintes variáveis:**

```env
# PostgreSQL
POSTGRES_PASSWORD=SuaSenhaSuperSegura123

# API Keys
OPENAI_API_KEY=sk-proj-sua-chave-openai
GROQ_API_KEY=gsk_sua-chave-groq

# JWT Secret (gere uma nova)
JWT_SECRET_KEY=$(openssl rand -base64 64)
```

### 3. Inicie os Containers

```bash
# Subir todos os serviços
docker-compose up -d

# Aguardar PostgreSQL inicializar
sleep 15

# Criar tabelas no banco
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql

# Verificar status
docker-compose ps
```

### 4. Conectar WhatsApp

```bash
# Ver QR Code para autenticação
docker-compose logs -f whatsapp

# Escaneie o QR Code com seu WhatsApp
```

### 5. Acessar Dashboard

```
http://localhost:80
```

**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin123`

> ⚠️ **Altere a senha após primeiro login!**

---

## ⚙️ Configuração

### Estrutura do `.env`

```env
# ===================================
# BANCO DE DADOS POSTGRESQL
# ===================================
POSTGRES_USER=spdrop_user
POSTGRES_PASSWORD=Sua_Senha_Aqui_Trocar
POSTGRES_DB=spdrop_db

# Variáveis individuais (para customer_manager.py e api)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=spdrop_db
DB_USER=spdrop_user
DB_PASSWORD=Mesma_Senha_Do_POSTGRES_PASSWORD

# ===================================
# API ADMINISTRATIVA
# ===================================
JWT_SECRET_KEY=Sua_Chave_JWT_Secreta

# ===================================
# APIs DE IA
# ===================================
OPENAI_API_KEY=sk-proj-sua-chave-openai
GROQ_API_KEY=gsk_sua-chave-groq
```

### Customizar Prompt da IA

Edite o arquivo `docs da minha empresa/prompt.md` com instruções específicas do seu negócio.

### Adicionar FAQs

Edite `docs da minha empresa/movos/Perguntas e respostas normal - ....csv`

---

## 🌐 Deploy em Produção

### Deploy em VPS (Ubuntu)

```bash
# 1. Copiar arquivos para VPS
scp docker-compose.prod.yml .env init.sql root@SEU_IP:/home/ubuntu/

# 2. Na VPS
ssh root@SEU_IP
cd /home/ubuntu

# 3. Subir containers
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 4. Criar tabelas
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql

# 5. Verificar logs
docker-compose -f docker-compose.prod.yml logs -f bot
```

### Configurar Firewall

```bash
# Permitir apenas porta 80 (HTTP)
ufw allow 80/tcp

# Para HTTPS (recomendado)
ufw allow 443/tcp

# Ativar firewall
ufw enable
```

### SSL/HTTPS com Let's Encrypt

```bash
# Instalar Certbot
apt install certbot python3-certbot-nginx

# Obter certificado
certbot --nginx -d seudominio.com

# Renovação automática já configurada!
```

---

## 📁 Estrutura do Projeto

```
spdrop/
├── 📁 api/                      # API FastAPI
│   ├── auth.py                 # Autenticação JWT
│   ├── conversations.py        # Endpoints de conversas
│   ├── dashboard.py            # Métricas
│   └── database.py             # Conexão PostgreSQL
├── 📁 agentes/                  # Agentes de IA
│   └── agente_suporte.py       # Agente principal
├── 📁 tools/                    # Tools customizadas
│   ├── faq_tools.py            # Perguntas frequentes
│   ├── trial_tools.py          # Teste grátis 7 dias
│   └── demo_account_tools.py   # Conta demo
├── 📁 whatsapp-service/         # Serviço WhatsApp
│   ├── server.js               # API Node.js
│   └── Dockerfile
├── 📁 frontend/                 # Dashboard React
│   └── src/
│       ├── pages/              # Páginas
│       └── components/         # Componentes
├── 📁 nginx/                    # Gateway Nginx
│   └── nginx.conf
├── 📁 docs/                     # Documentação
│   └── tutoriais/
├── 📄 main.py                   # Bot principal
├── 📄 customer_manager.py       # Gestão de clientes
├── 📄 transcription_service.py  # Groq Whisper
├── 📄 image_analysis_service.py # OpenAI Vision
├── 📄 docker-compose.yml        # Compose local
├── 📄 docker-compose.prod.yml   # Compose produção
├── 📄 init.sql                  # Schema do banco
└── 📄 requirements.txt          # Dependências Python
```

---

## 🔌 API Endpoints

### Autenticação

```http
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "senha"
}
```

### Conversas

```http
GET /api/conversations
Authorization: Bearer {token}
```

### Dashboard Métricas

```http
GET /api/dashboard/stats
Authorization: Bearer {token}
```

### WhatsApp QR Code

```http
GET /api/qrcode
Authorization: Bearer {token}
```

**Documentação completa:** Ver `README_API.md`

---

## 🐛 Troubleshooting

### Erro: "relation 'customers' does not exist"

**Solução:**
```bash
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql
```

### Erro: "password authentication failed"

**Causa:** `POSTGRES_PASSWORD` diferente de `DB_PASSWORD`

**Solução:**
```bash
# Verificar .env
cat .env | grep PASSWORD

# As duas senhas devem ser IGUAIS!
# Corrigir e recriar containers
docker-compose down -v
docker-compose up -d
```

### WhatsApp desconecta constantemente

**Solução:**
```bash
# Limpar sessão e reconectar
docker-compose down
docker volume rm spdrop_whatsapp_auth
docker-compose up -d
```

### Bot não responde mensagens

**Verificar logs:**
```bash
docker-compose logs -f bot
docker-compose logs -f whatsapp
```

**Mais troubleshooting:** Ver `docs/tutoriais/09-TROUBLESHOOTING.md`

---

## 📚 Documentação Completa

### Guias de Instalação
- [00 - Requisitos](docs/tutoriais/00-REQUISITOS.md)
- [01 - Setup Inicial](docs/tutoriais/01-SETUP-INICIAL.md)
- [02 - Database](docs/tutoriais/02-DATABASE.md)
- [03 - WhatsApp](docs/tutoriais/03-WHATSAPP.md)
- [04 - Bot](docs/tutoriais/04-BOT.md)

### Deploy
- [DEPLOY_FINAL.md](DEPLOY_FINAL.md) - Guia completo de deploy
- [CRIAR_TABELAS.md](CRIAR_TABELAS.md) - Setup do banco de dados
- [CONFIGURAR_FIREWALL.md](CONFIGURAR_FIREWALL.md) - Segurança VPS

### Arquitetura
- [10 - Arquitetura](docs/tutoriais/10-ARQUITETURA.md)
- [README_API.md](README_API.md) - Documentação da API
- [README_WHATSAPP.md](README_WHATSAPP.md) - Serviço WhatsApp

---

## 🐳 Docker Hub

Imagens públicas disponíveis:

- **API:** `paulo003/spdrop-api:v1.1` (709MB)
- **Bot:** `paulo003/spdrop-bot:v1.1` (709MB)
- **WhatsApp:** `paulo003/spdrop-whatsapp:v1.1` (2.61GB)
- **Nginx:** `paulo003/spdrop-nginx:v1.1` (79.9MB)

```bash
# Baixar todas as imagens
docker-compose -f docker-compose.prod.yml pull
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙋 Suporte

- **Issues:** [GitHub Issues](https://github.com/paulohenriquehto/botspdrop/issues)
- **Documentação:** [Wiki do Projeto](https://github.com/paulohenriquehto/botspdrop/wiki)

---

## 🎯 Roadmap

- [ ] Integração com Mercado Pago
- [ ] Suporte a múltiplos idiomas
- [ ] Dashboard analytics avançado
- [ ] Sistema de notificações push
- [ ] Integração com CRM

---

**Desenvolvido com ❤️ usando Claude Code**

[![GitHub stars](https://img.shields.io/github/stars/paulohenriquehto/botspdrop?style=social)](https://github.com/paulohenriquehto/botspdrop)
[![GitHub forks](https://img.shields.io/github/forks/paulohenriquehto/botspdrop?style=social)](https://github.com/paulohenriquehto/botspdrop)