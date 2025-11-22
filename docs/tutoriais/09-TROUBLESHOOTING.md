# 09 - Solução de Problemas Comuns

## 🔧 Guia de Troubleshooting

Este documento cobre os problemas mais comuns e suas soluções.

---

## 📋 Índice de Problemas

1. [Docker e Containers](#docker-e-containers)
2. [WhatsApp Web.js](#whatsapp-webjs)
3. [Bot FastAPI](#bot-fastapi)
4. [Agente de IA](#agente-de-ia)
5. [PostgreSQL](#postgresql)
6. [Rede e Comunicação](#rede-e-comunicação)
7. [Performance](#performance)

---

## Docker e Containers

### ❌ Container não inicia

**Sintomas:**
```bash
docker compose ps
# STATUS: Exited (1)
```

**Diagnóstico:**
```bash
# Ver logs do container
docker compose logs <service_name>

# Ver últimas 50 linhas
docker compose logs --tail=50 whatsapp
```

**Soluções:**

#### 1. Porta já em uso
```bash
# Verificar quem está usando
sudo lsof -i :5000  # Bot
sudo lsof -i :9000  # WhatsApp
sudo lsof -i :5432  # PostgreSQL

# Matar processo
sudo kill -9 <PID>

# Ou mudar porta no docker-compose.yml
ports:
  - "5001:5000"  # Usar 5001 no host
```

#### 2. Erro de build
```bash
# Rebuild sem cache
docker compose build --no-cache

# Rebuild específico
docker compose build --no-cache bot
```

#### 3. Volume corrompido
```bash
# Remover volumes
docker compose down -v

# Recriar
docker compose up -d
```

---

### ❌ Container reinicia constantemente

**Sintomas:**
```bash
docker compose ps
# STATUS: Restarting
```

**Diagnóstico:**
```bash
# Ver logs em tempo real
docker compose logs -f <service_name>

# Parar restart temporário para debug
docker compose stop <service_name>
docker compose start <service_name> --no-deps
```

**Soluções:**

#### 1. Erro no código
```bash
# Ver stack trace
docker compose logs bot | grep -i error

# Corrigir código
# Rebuild
docker compose build bot
docker compose up -d bot
```

#### 2. Dependência não disponível
```bash
# Bot esperando PostgreSQL
# Verificar healthcheck
docker inspect vanlu_postgres | grep -A 10 Health

# Aguardar PostgreSQL estar pronto
docker compose logs postgres | grep "ready to accept"
```

---

## WhatsApp Web.js

### ❌ QR Code não aparece

**Sintomas:**
- Página http://localhost:9000 mostra "Aguardando QR Code..."
- Nunca mostra o QR Code

**Diagnóstico:**
```bash
# Ver logs do WhatsApp
docker compose logs whatsapp | grep -i qr

# Ver erros do Puppeteer
docker compose logs whatsapp | grep -i error
```

**Soluções:**

#### 1. Puppeteer não inicializa
```bash
# Aumentar shm_size (memória compartilhada)
# docker-compose.yml
whatsapp:
  shm_size: '2gb'  # Adicionar esta linha

# Restart
docker compose down
docker compose up -d
```

#### 2. Chromium travado
```bash
# Remover volume de auth
docker volume rm vanlu-agente_whatsapp_auth

# Restart
docker compose up -d whatsapp
```

#### 3. Timeout do Puppeteer
```javascript
// whatsapp-service/server.js
client = new Client({
    puppeteer: {
        timeout: 60000  // Aumentar para 60 segundos
    }
});
```

---

### ❌ WhatsApp desconecta frequentemente

**Sintomas:**
- QR Code expira rapidamente
- Desconexões frequentes
- Precisa escanear QR toda hora

**Diagnóstico:**
```bash
# Ver eventos de desconexão
docker compose logs whatsapp | grep -i "disconnected\|auth_failure"
```

**Soluções:**

#### 1. Volume não está persistindo
```bash
# Verificar volume
docker volume ls | grep whatsapp_auth

# Se não existir, criar
docker volume create vanlu-agente_whatsapp_auth

# Verificar montagem
docker inspect vanlu_whatsapp | grep -A 5 Mounts
```

#### 2. WhatsApp Web desvinculado no celular
```
Solução: Re-escanear QR Code
1. Acessar http://localhost:9000
2. Escanear novo QR Code
3. Sessão será salva
```

#### 3. Sessão corrompida
```bash
# Fazer logout e reconectar
curl -X POST http://localhost:9000/logout

# Aguardar novo QR Code
# Escanear novamente
```

---

### ❌ Mensagens não chegam no bot

**Sintomas:**
- WhatsApp recebe mensagem
- Bot não processa

**Diagnóstico:**
```bash
# Ver se WhatsApp está enviando webhook
docker compose logs whatsapp | grep "📨 Mensagem recebida"

# Ver se bot está recebendo
docker compose logs bot | grep "Webhook recebido"
```

**Soluções:**

#### 1. Webhook URL errado
```bash
# Verificar configuração
docker compose logs whatsapp | grep WEBHOOK_URL
# Deve mostrar: http://bot:5000/webhook

# Corrigir no docker-compose.yml
whatsapp:
  environment:
    - WEBHOOK_URL=http://bot:5000/webhook

# Restart
docker compose restart whatsapp
```

#### 2. Bot não está acessível
```bash
# Testar conectividade
docker exec vanlu_whatsapp curl http://bot:5000/health

# Se falhar, verificar rede
docker network inspect vanlu-agente_vanlu_network
```

---

## Bot FastAPI

### ❌ Bot não inicia

**Sintomas:**
```bash
docker compose logs bot
# Error: ModuleNotFoundError
```

**Diagnóstico:**
```bash
# Ver erro completo
docker compose logs bot | grep -i error
```

**Soluções:**

#### 1. Dependências faltando
```bash
# Rebuild com requirements.txt atualizado
docker compose build --no-cache bot
docker compose up -d bot
```

#### 2. Erro no código Python
```bash
# Ver stack trace
docker compose logs bot

# Corrigir código
# Restart
docker compose restart bot
```

#### 3. Variável de ambiente faltando
```bash
# Verificar .env
cat .env

# Verificar se bot recebeu
docker exec vanlu_bot env | grep OPENAI_API_KEY
docker exec vanlu_bot env | grep DATABASE_URL
```

---

### ❌ Bot processa mas não responde

**Sintomas:**
- Webhook recebido
- Agente processa
- MAS não envia resposta

**Diagnóstico:**
```bash
# Ver se está processando
docker compose logs bot | grep "Processando com Agente"

# Ver se está tentando enviar
docker compose logs bot | grep "📤 Mensagem"

# Ver erros de envio
docker compose logs bot | grep -i "erro ao enviar"
```

**Soluções:**

#### 1. WhatsApp não está conectado
```bash
# Verificar status
curl http://localhost:9000/status

# Se não conectado, escanear QR
http://localhost:9000
```

#### 2. Formato de número não suportado
```bash
# Verificar logs para números @lid
docker compose logs bot | grep "@lid"

# Solução: Já corrigido no Bug #1 (ver 08-BUGS-CORRIGIDOS.md)
# Rebuild whatsapp se necessário
docker compose build whatsapp
docker compose up -d whatsapp
```

---

## Agente de IA

### ❌ Agente não responde

**Sintomas:**
- Bot processa
- Agente demora infinitamente
- Timeout

**Diagnóstico:**
```bash
# Ver logs do agente
docker compose logs bot | grep -i "processando com agente"

# Ver erros da OpenAI
docker compose logs bot | grep -i "openai\|api"
```

**Soluções:**

#### 1. OpenAI API Key inválida
```bash
# Verificar key
docker exec vanlu_bot env | grep OPENAI_API_KEY

# Testar key
docker exec vanlu_bot python3 -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('API Key válida!')
"
```

#### 2. Sem créditos na OpenAI
```
Solução:
1. Acessar https://platform.openai.com/account/billing
2. Verificar saldo
3. Adicionar créditos se necessário
```

#### 3. Rate limit excedido
```bash
# Ver erro de rate limit
docker compose logs bot | grep "rate_limit"

# Solução: Aguardar alguns minutos
# Ou aumentar tier na OpenAI
```

---

### ❌ Ferramentas não são usadas

**Sintomas:**
- Agente responde
- MAS não usa FAQ/Memory/Scripts

**Diagnóstico:**
```bash
# Ver se tools estão carregadas
docker compose logs bot | grep -i "tool"

# Ver prompt sendo enviado
docker exec vanlu_bot python3 -c "
from agentes.agente_suporte import support_agent
print(support_agent.tools)
"
```

**Soluções:**

#### 1. Tools não registradas
```python
# Verificar agente_suporte.py
tools=[
    SPDropFAQTools(),
    SPDropMemoryTools(),
    ConversationScriptsTools()
]

# Rebuild bot
docker compose build bot
docker compose up -d bot
```

#### 2. CSV não encontrado
```bash
# Verificar arquivos
docker exec vanlu_bot ls -la data/

# Deve ter:
# - spdrop_faq.csv
# - conversation_scripts.csv

# Se faltando, copiar para container
docker cp data/ vanlu_bot:/app/data/
```

---

## PostgreSQL

### ❌ Bot não conecta ao PostgreSQL

**Sintomas:**
```
Error: could not connect to server
Connection refused
```

**Diagnóstico:**
```bash
# Verificar se PostgreSQL está rodando
docker compose ps postgres

# Testar conexão
docker exec vanlu_bot pg_isready -h postgres -U vanlu_user
```

**Soluções:**

#### 1. PostgreSQL não iniciou
```bash
# Ver logs
docker compose logs postgres

# Aguardar "ready to accept connections"
docker compose logs postgres | grep "ready"

# Se não iniciar, rebuild
docker compose down
docker compose up -d postgres
```

#### 2. Credenciais erradas
```bash
# Verificar DATABASE_URL
docker exec vanlu_bot env | grep DATABASE_URL

# Deve ser:
# postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db

# Corrigir no docker-compose.yml
bot:
  environment:
    - DATABASE_URL=postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db
```

---

### ❌ Tabelas não foram criadas

**Sintomas:**
```
Error: relation "customers" does not exist
```

**Diagnóstico:**
```bash
# Conectar ao banco
docker exec -it vanlu_postgres psql -U vanlu_user -d vanlu_db

# Listar tabelas
\dt

# Sair
\q
```

**Soluções:**

#### 1. init.sql não foi executado
```bash
# Verificar se arquivo existe
ls -la init.sql

# Recriar banco (apaga dados!)
docker compose down -v
docker compose up -d postgres

# Aguardar
sleep 10

# Verificar novamente
docker exec vanlu_postgres psql -U vanlu_user -d vanlu_db -c "\dt"
```

#### 2. Criar tabelas manualmente
```bash
# Executar init.sql manualmente
docker exec -i vanlu_postgres psql -U vanlu_user -d vanlu_db < init.sql
```

---

## Rede e Comunicação

### ❌ Containers não se comunicam

**Sintomas:**
```
Error: Connection refused
Could not connect to host
```

**Diagnóstico:**
```bash
# Verificar rede
docker network ls | grep vanlu

# Inspecionar rede
docker network inspect vanlu-agente_vanlu_network

# Verificar conectividade
docker exec vanlu_bot ping -c 3 postgres
docker exec vanlu_bot curl http://whatsapp:3000/health
```

**Soluções:**

#### 1. Containers não estão na mesma rede
```bash
# Recriar rede
docker compose down
docker network prune
docker compose up -d
```

#### 2. Usando localhost ao invés de nome do container
```python
# ❌ ERRADO
DATABASE_URL = "postgresql://user:pass@localhost:5432/db"

# ✅ CORRETO
DATABASE_URL = "postgresql://user:pass@postgres:5432/db"
```

---

## Performance

### ❌ Respostas muito lentas

**Sintomas:**
- Mensagens demoram >30 segundos
- Timeout frequente

**Diagnóstico:**
```bash
# Verificar uso de CPU/RAM
docker stats

# Ver logs de tempo
docker compose logs bot | grep "Aguardando\|Timer"
```

**Soluções:**

#### 1. Buffer muito longo
```python
# main.py
BUFFER_TIMEOUT = 13  # Reduzir para 8-10 segundos se necessário
```

#### 2. Delay entre mensagens muito grande
```python
# main.py → send_message_in_parts()
delay = min(3 + (len(part) / 100), 6)  # Reduzir valores se necessário
# Exemplo: min(2 + (len(part) / 150), 4)
```

#### 3. Modelo da OpenAI lento
```python
# agente_suporte.py
# Usar gpt-4.1-mini (já é o mais rápido)
model=OpenAIChat(id="gpt-4.1-mini")
```

---

### ❌ Sistema consumindo muita RAM

**Sintomas:**
```bash
docker stats
# Bot usando >1GB RAM
```

**Soluções:**

#### 1. Limpar histórico antigo
```sql
-- Apagar conversas >30 dias
DELETE FROM conversation_history
WHERE timestamp < NOW() - INTERVAL '30 days';
```

#### 2. Limitar memória do container
```yaml
# docker-compose.yml
bot:
  deploy:
    resources:
      limits:
        memory: 512M
```

---

## 🔍 Comandos Úteis de Debug

### Ver todos os logs
```bash
docker compose logs -f
```

### Ver logs específicos
```bash
docker compose logs -f bot
docker compose logs -f whatsapp
docker compose logs -f postgres
```

### Ver últimas N linhas
```bash
docker compose logs --tail=100 bot
```

### Buscar erro nos logs
```bash
docker compose logs bot | grep -i error
docker compose logs bot | grep -i exception
```

### Entrar no container
```bash
docker exec -it vanlu_bot bash
docker exec -it vanlu_whatsapp sh
docker exec -it vanlu_postgres bash
```

### Ver variáveis de ambiente
```bash
docker exec vanlu_bot env
docker exec vanlu_whatsapp env
```

### Restart específico
```bash
docker compose restart bot
docker compose restart whatsapp
```

### Rebuild e restart
```bash
docker compose build bot && docker compose up -d bot
```

---

## ✅ Checklist de Verificação

Quando algo não funciona, siga esta ordem:

- [ ] Todos os containers estão UP? (`docker compose ps`)
- [ ] Logs não mostram erros? (`docker compose logs`)
- [ ] Rede está OK? (`docker network inspect`)
- [ ] Volumes existem? (`docker volume ls`)
- [ ] Variáveis de ambiente corretas? (`docker exec ... env`)
- [ ] PostgreSQL conectado? (`pg_isready`)
- [ ] WhatsApp conectado? (`curl localhost:9000/status`)
- [ ] Bot respondendo? (`curl localhost:5000/health`)

---

## 📚 Próximos Passos

**[10-ARQUITETURA.md](./10-ARQUITETURA.md)** → Arquitetura detalhada do sistema

---

**Status:** ✅ Guia de troubleshooting completo
