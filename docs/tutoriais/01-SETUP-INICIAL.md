# 01 - Setup Inicial e Configuração Docker

## 📁 Estrutura do Projeto

Antes de começar, veja como o projeto está organizado:

```
Vanlu agente/
├── docker-compose.yml          # Orquestração dos containers
├── Dockerfile                  # Dockerfile do bot Python
├── requirements.txt            # Dependências Python
├── main.py                     # Servidor FastAPI (bot principal)
├── .env                        # Variáveis de ambiente (CRIAR)
├── init.sql                    # Script de inicialização do banco
│
├── whatsapp-service/           # Serviço WhatsApp
│   ├── Dockerfile
│   ├── package.json
│   ├── server.js               # Servidor WhatsApp Web.js
│   └── wwebjs_auth/            # (criado automaticamente)
│
├── agentes/                    # Agentes de IA
│   └── agente_suporte.py       # Agente principal (Gabi)
│
├── tools/                      # Ferramentas do agente
│   ├── faq_tool.py
│   ├── memory_tool.py
│   └── conversation_scripts_tool.py
│
├── customer_manager.py         # Gerenciador de clientes
├── whatsapp_integration.py     # Cliente WhatsApp
└── database.py                 # Conexão com PostgreSQL
```

---

## 🐳 Arquivo docker-compose.yml

Crie o arquivo `docker-compose.yml` na raiz do projeto:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: vanlu_postgres
    environment:
      POSTGRES_USER: vanlu_user
      POSTGRES_PASSWORD: vanlu_password
      POSTGRES_DB: vanlu_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vanlu_user -d vanlu_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - vanlu_network

  whatsapp:
    build:
      context: ./whatsapp-service
      dockerfile: Dockerfile
    container_name: vanlu_whatsapp
    ports:
      - "9000:3000"
    environment:
      - PORT=3000
      - WEBHOOK_URL=http://bot:5000/webhook
      - NODE_ENV=production
    volumes:
      - whatsapp_auth:/app/wwebjs_auth
    shm_size: '2gb'
    cap_add:
      - SYS_ADMIN
    security_opt:
      - seccomp:unconfined
    networks:
      - vanlu_network

  bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: vanlu_bot
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db
      - WHATSAPP_API_URL=http://whatsapp:3000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - whatsapp
    restart: unless-stopped
    networks:
      - vanlu_network

volumes:
  postgres_data:
  whatsapp_auth:

networks:
  vanlu_network:
    driver: bridge
```

---

## 🔑 Arquivo .env

Crie o arquivo `.env` na raiz do projeto com suas credenciais:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxx

# PostgreSQL (já configurado no docker-compose)
DATABASE_URL=postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db

# WhatsApp API URL (interno)
WHATSAPP_API_URL=http://whatsapp:3000

# FastAPI (opcional - já tem padrão)
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=5000
```

⚠️ **IMPORTANTE:**
- Substitua `sk-proj-xxx` pela sua chave OpenAI real
- NUNCA commite o `.env` no Git
- Adicione `.env` ao `.gitignore`

---

## 🐍 Dockerfile do Bot (Python)

Crie `Dockerfile` na raiz do projeto:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 5000

# Comando para rodar o servidor
CMD ["python", "main.py"]
```

---

## 📦 requirements.txt

Crie `requirements.txt` na raiz:

```
agno>=1.0.0
openai>=1.0.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.0.0
```

---

## 📱 Dockerfile do WhatsApp Service (Node.js)

Crie `whatsapp-service/Dockerfile`:

```dockerfile
FROM node:18-bullseye

# Instalar dependências do Puppeteer
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

---

## 📦 package.json do WhatsApp Service

Crie `whatsapp-service/package.json`:

```json
{
  "name": "whatsapp-service",
  "version": "1.0.0",
  "description": "WhatsApp Web.js API Service for Vanlu Bot",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "whatsapp-web.js": "^1.23.0",
    "qrcode-terminal": "^0.12.0",
    "qrcode": "^1.5.3",
    "body-parser": "^1.20.2"
  }
}
```

---

## 🚀 Iniciando o Sistema

### 1. Build dos Containers

```bash
cd "/home/paulo/Projeto/Vanlu agente"

# Build de todos os serviços
docker compose build
```

**Tempo estimado:** 5-10 minutos (primeira vez)

---

### 2. Iniciar Todos os Serviços

```bash
# Modo detached (segundo plano)
docker compose up -d

# Ou modo interativo (ver logs)
docker compose up
```

**Ordem de inicialização:**
1. PostgreSQL (primeiro)
2. WhatsApp Service (segundo)
3. Bot Service (terceiro - depende dos outros)

---

### 3. Verificar Containers Rodando

```bash
docker compose ps
```

**Saída esperada:**
```
NAME              STATUS     PORTS
vanlu_postgres    Up         0.0.0.0:5432->5432/tcp
vanlu_whatsapp    Up         0.0.0.0:9000->3000/tcp
vanlu_bot         Up         0.0.0.0:5000->5000/tcp
```

---

### 4. Ver Logs

```bash
# Todos os serviços
docker compose logs -f

# Apenas WhatsApp
docker compose logs -f whatsapp

# Apenas Bot
docker compose logs -f bot

# Apenas PostgreSQL
docker compose logs -f postgres
```

---

## ✅ Verificações de Saúde

### PostgreSQL

```bash
# Conectar ao PostgreSQL
docker exec -it vanlu_postgres psql -U vanlu_user -d vanlu_db

# Listar tabelas
\dt

# Sair
\q
```

**Esperado:** 14 tabelas criadas (services, customers, sessions, etc.)

---

### WhatsApp Service

```bash
# Verificar logs do WhatsApp
docker compose logs whatsapp | grep -E "QR Code|conectado"

# Acessar no navegador
http://localhost:9000
```

**Esperado:**
- Página HTML com QR Code
- Ou mensagem "✅ Conectado!" se já escaneado

---

### Bot Service

```bash
# Health check
curl http://localhost:5000/health

# Endpoint raiz
curl http://localhost:5000/
```

**Esperado:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T..."
}
```

---

## 🔄 Comandos Úteis

### Reiniciar Serviços

```bash
# Reiniciar tudo
docker compose restart

# Reiniciar apenas WhatsApp
docker compose restart whatsapp

# Reiniciar apenas bot
docker compose restart bot
```

---

### Parar Serviços

```bash
# Parar todos
docker compose stop

# Parar apenas bot
docker compose stop bot
```

---

### Derrubar Tudo (e apagar volumes)

```bash
# Parar e remover containers
docker compose down

# Parar e remover containers + volumes (⚠️ APAGA DADOS!)
docker compose down -v
```

⚠️ **Cuidado:** `-v` apaga os dados do PostgreSQL e sessão do WhatsApp!

---

### Rebuild de um Serviço

```bash
# Rebuild do bot (após mudanças no código)
docker compose build bot
docker compose up -d bot

# Rebuild do WhatsApp (após mudanças)
docker compose build whatsapp
docker compose up -d whatsapp
```

---

## 📊 Volumes Criados

```bash
# Listar volumes
docker volume ls | grep vanlu

# Inspecionar volume do PostgreSQL
docker volume inspect vanlu-agente_postgres_data

# Inspecionar volume do WhatsApp
docker volume inspect vanlu-agente_whatsapp_auth
```

---

## 🌐 Rede Docker

```bash
# Listar redes
docker network ls | grep vanlu

# Inspecionar rede
docker network inspect vanlu-agente_vanlu_network
```

**Containers podem se comunicar pelos nomes:**
- `postgres` → PostgreSQL
- `whatsapp` → WhatsApp Service
- `bot` → Bot Service

---

## ⚠️ Troubleshooting Inicial

### Container não inicia

```bash
# Ver logs detalhados
docker compose logs whatsapp

# Ver status de saúde
docker compose ps
```

---

### Porta já em uso

```bash
# Ver quem está usando a porta 5000
sudo lsof -i :5000

# Matar processo
sudo kill -9 <PID>

# Ou mudar porta no docker-compose.yml
ports:
  - "5001:5000"  # Usar 5001 no host
```

---

### Problemas de rede

```bash
# Recriar rede
docker compose down
docker network prune
docker compose up -d
```

---

### Build falha

```bash
# Limpar cache e rebuild
docker compose build --no-cache

# Ou rebuild específico
docker compose build --no-cache bot
```

---

## 🎯 Checklist Pós-Instalação

- [ ] Todos os 3 containers estão UP
- [ ] PostgreSQL responde em localhost:5432
- [ ] WhatsApp mostra QR Code em localhost:9000
- [ ] Bot responde em localhost:5000/health
- [ ] Logs não mostram erros críticos
- [ ] Volumes foram criados
- [ ] Rede docker está ativa

---

## 📝 Próximos Passos

Se tudo estiver funcionando, prossiga para:

**[02-DATABASE.md](./02-DATABASE.md)** → Configuração do PostgreSQL e tabelas

---

**Status:** ✅ Setup Docker completo
