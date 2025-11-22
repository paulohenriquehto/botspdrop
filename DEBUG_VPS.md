# 🔍 Debug - Resolver Erro "Desculpe, ocorreu um erro"

## 1️⃣ Verificar se todos os containers estão rodando

```bash
cd ~/spdrop
docker-compose -f docker-compose.prod.yml ps
```

**Esperado:** Todos devem estar "Up". Se algum estiver "Exit" ou "Restarting", há problema.

## 2️⃣ Ver logs do BOT (onde ocorre o erro)

```bash
# Ver logs do bot (últimas 100 linhas)
docker-compose -f docker-compose.prod.yml logs --tail=100 bot

# Ou seguir logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f bot
```

**Procure por:**
- ❌ Erros de API Key (OpenAI ou Groq)
- ❌ Erros de conexão com banco de dados
- ❌ Erros de importação de módulos

## 3️⃣ Ver logs do WhatsApp Service

```bash
docker-compose -f docker-compose.prod.yml logs --tail=100 whatsapp
```

## 4️⃣ Ver logs do PostgreSQL

```bash
docker-compose -f docker-compose.prod.yml logs --tail=50 postgres
```

## 5️⃣ Verificar conectividade entre containers

```bash
# Entrar no container do bot
docker exec -it spdrop_bot bash

# Testar conexão com PostgreSQL
apt update && apt install -y postgresql-client
psql -h postgres -U spdrop_user -d spdrop_db

# Se conectar, digitar \q para sair

# Testar conexão com WhatsApp
curl http://whatsapp:3000/status

# Sair do container
exit
```

## 6️⃣ Verificar variáveis de ambiente

```bash
# Ver variáveis do bot
docker exec spdrop_bot env | grep -E "OPENAI|GROQ|DATABASE"

# Ver variáveis do api
docker exec spdrop_api env | grep -E "DB_|JWT"
```

## 🔧 Problemas Comuns e Soluções

### ❌ Erro: "OPENAI_API_KEY not found" ou "Invalid API key"

**Solução:**
```bash
# Editar .env
nano ~/spdrop/.env

# Verificar se OPENAI_API_KEY está correto e SEM espaços
OPENAI_API_KEY=sk-proj-...

# Recriar containers
docker-compose -f docker-compose.prod.yml up -d --force-recreate bot
```

### ❌ Erro: "could not connect to server: Connection refused" (PostgreSQL)

**Solução:**
```bash
# Verificar se postgres está saudável
docker-compose -f docker-compose.prod.yml ps postgres

# Se não estiver, ver logs
docker-compose -f docker-compose.prod.yml logs postgres

# Recriar postgres (CUIDADO: pode perder dados)
docker-compose -f docker-compose.prod.yml up -d --force-recreate postgres
```

### ❌ Erro: "No module named 'openai'" ou "No module named 'groq'"

**Problema:** Imagem não tem as dependências instaladas

**Solução:**
```bash
# Fazer pull da imagem novamente
docker pull paulo003/spdrop-bot:v1.0

# Recriar container
docker-compose -f docker-compose.prod.yml up -d --force-recreate bot
```

### ❌ Erro: "relation 'conversas' does not exist" (Banco de dados não inicializado)

**Solução:**
```bash
# Copiar init.sql para VPS (do seu PC local)
scp init.sql root@SEU_IP_VPS:/root/spdrop/

# Na VPS, executar init.sql
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql

# Verificar se tabelas foram criadas
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "\dt"
```

## 7️⃣ Comando para ver TODOS os logs de uma vez

```bash
docker-compose -f docker-compose.prod.yml logs --tail=200
```

## 8️⃣ Reiniciar tudo do zero (se nada funcionar)

```bash
# Parar tudo
docker-compose -f docker-compose.prod.yml down

# Remover volumes (CUIDADO: apaga dados do banco!)
docker-compose -f docker-compose.prod.yml down -v

# Subir novamente
docker-compose -f docker-compose.prod.yml up -d

# Inicializar banco
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql
```

## 9️⃣ Teste manual da API OpenAI

```bash
# Entrar no container do bot
docker exec -it spdrop_bot python3

# No Python, testar OpenAI
>>> import os
>>> print(os.getenv('OPENAI_API_KEY'))
>>> from openai import OpenAI
>>> client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
>>> response = client.chat.completions.create(
...     model="gpt-4o-mini",
...     messages=[{"role": "user", "content": "teste"}]
... )
>>> print(response.choices[0].message.content)
>>> exit()
```

## 🆘 Se ainda não funcionar

**Me envie a saída destes comandos:**

```bash
# 1. Status dos containers
docker-compose -f docker-compose.prod.yml ps

# 2. Logs do bot
docker-compose -f docker-compose.prod.yml logs --tail=100 bot

# 3. Variáveis de ambiente
docker exec spdrop_bot env | grep -E "OPENAI|GROQ|DATABASE"

# 4. Testar banco de dados
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "\dt"
```
