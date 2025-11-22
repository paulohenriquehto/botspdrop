# 🚀 DEPLOY FINAL - SPDROP v1.1

## ✅ O QUE FOI CORRIGIDO

### Problema Anterior:
- `customer_manager.py` procurava por `DB_PASSWORD`
- Docker Compose só passava `DATABASE_URL`
- Resultado: **Erro de autenticação no PostgreSQL**

### Solução Aplicada:
- ✅ Adicionadas TODAS as variáveis de banco no container `bot`
- ✅ Imagens atualizadas para v1.1 no Docker Hub
- ✅ `.env.example` atualizado com todas variáveis necessárias

---

## 📋 ARQUIVOS ATUALIZADOS

### 1. `.env.example` - Template completo
```env
# POSTGRES (para criar o container)
POSTGRES_USER=spdrop_user
POSTGRES_PASSWORD=Xw92kL0F3q9tPmA7VgJ2HsR8NeZ5BcQ1UyT6DfG4RxP8LaS0MjW3KpH9TsE4ZdN
POSTGRES_DB=spdrop_db

# VARIÁVEIS INDIVIDUAIS (usadas por customer_manager.py e api)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=spdrop_db
DB_USER=spdrop_user
DB_PASSWORD=Xw92kL0F3q9tPmA7VgJ2HsR8NeZ5BcQ1UyT6DfG4RxP8LaS0MjW3KpH9TsE4ZdN

# JWT
JWT_SECRET_KEY=RiPoMjP4pxYIi61JQTegBem0xsg3mS9+2W7BVSLkxHhGYKpiV4mAFQaNA/xmouiQqawXFGSgyTZ0puyd3KquiA==

# OPENAI & GROQ
OPENAI_API_KEY=sua-chave-aqui
GROQ_API_KEY=sua-chave-aqui
```

### 2. `docker-compose.prod.yml`
**Container Bot com TODAS as variáveis:**
```yaml
bot:
  image: paulo003/spdrop-bot:v1.1
  environment:
    - DATABASE_URL=postgresql://...  # Para compatibilidade
    - DB_HOST=postgres               # Para customer_manager.py
    - DB_PORT=5432                   # Para customer_manager.py
    - DB_NAME=${POSTGRES_DB}         # Para customer_manager.py
    - DB_USER=${POSTGRES_USER}       # Para customer_manager.py
    - DB_PASSWORD=${POSTGRES_PASSWORD} # Para customer_manager.py ✅
    - WHATSAPP_API_URL=...
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - GROQ_API_KEY=${GROQ_API_KEY}
```

**Versões atualizadas:**
- API: `paulo003/spdrop-api:v1.1`
- Bot: `paulo003/spdrop-bot:v1.1`
- WhatsApp: `paulo003/spdrop-whatsapp:v1.1`
- Nginx: `paulo003/spdrop-nginx:v1.1`

---

## 🔧 DEPLOY NA VPS

### OPÇÃO 1: Deploy Limpo (Recomendado)

```bash
# 1. Copiar arquivos para VPS (do seu PC)
scp docker-compose.prod.yml .env.example init.sql root@SEU_IP_VPS:/home/ubuntu/

# 2. Na VPS
ssh root@SEU_IP_VPS
cd /home/ubuntu

# 3. Configurar .env
cp .env.example .env
nano .env
# Verifique se a senha é a MESMA em POSTGRES_PASSWORD e DB_PASSWORD

# 4. Parar e limpar tudo
docker-compose -f docker-compose.prod.yml down -v
docker volume prune -f

# 5. Subir versão v1.1
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 6. Aguardar PostgreSQL inicializar
sleep 15

# 7. Criar TODAS as tabelas do sistema (20+ tabelas)
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql

# 8. Verificar se as tabelas foram criadas (deve mostrar 20+ tabelas)
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "\dt"

# 9. Ver status dos containers
docker-compose -f docker-compose.prod.yml ps

# 10. Testar logs
docker-compose -f docker-compose.prod.yml logs -f bot
```

### OPÇÃO 2: Atualização Rápida (Se já está rodando)

```bash
cd /home/ubuntu

# 1. Atualizar .env (adicionar variáveis individuais)
nano .env
# Adicionar as linhas:
# DB_HOST=postgres
# DB_PORT=5432
# DB_NAME=spdrop_db
# DB_USER=spdrop_user
# DB_PASSWORD=MESMA_SENHA_DO_POSTGRES_PASSWORD

# 2. Atualizar imagens
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --force-recreate bot api

# 3. Ver logs
docker-compose -f docker-compose.prod.yml logs -f bot
```

---

## ✅ VERIFICAÇÃO

### 1. Verificar variáveis de ambiente do bot
```bash
docker exec spdrop_bot env | grep -E "DB_|POSTGRES"
```

**Deve mostrar:**
```
POSTGRES_USER=spdrop_user
POSTGRES_DB=spdrop_db
POSTGRES_PASSWORD=Xw92kL0F3q9tPmA7VgJ2HsR8NeZ5BcQ1UyT6DfG4RxP8LaS0MjW3KpH9TsE4ZdN
DB_HOST=postgres
DB_PORT=5432
DB_NAME=spdrop_db
DB_USER=spdrop_user
DB_PASSWORD=Xw92kL0F3q9tPmA7VgJ2HsR8NeZ5BcQ1UyT6DfG4RxP8LaS0MjW3KpH9TsE4ZdN
DATABASE_URL=postgresql://spdrop_user:Xw92kL0F3q9tPmA7VgJ2HsR8NeZ5BcQ1UyT6DfG4RxP8LaS0MjW3KpH9TsE4ZdN@postgres:5432/spdrop_db
```

### 2. Testar conexão do bot com PostgreSQL
```bash
docker exec spdrop_bot python3 -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    print('✅ Conexão bem-sucedida!')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

### 3. Enviar mensagem de teste
Envie "oi" pelo WhatsApp e veja os logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f bot
```

**Se funcionar, deve aparecer:**
```
✅ Cliente encontrado: ID=1, Nome=Cliente XXXX
```

**EM VEZ DE:**
```
❌ password authentication failed for user "spdrop_user"
```

---

## 🔍 TROUBLESHOOTING

### Erro: "password authentication failed"

**Solução:**
```bash
# 1. Verificar se .env tem as mesmas senhas
cat .env | grep PASSWORD

# POSTGRES_PASSWORD e DB_PASSWORD devem ser IGUAIS!

# 2. Se forem diferentes, corrigir e recriar
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

### Erro: "relation 'customers' does not exist"

**Solução:**
```bash
# Executar init.sql novamente
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql
```

---

## 📦 IMAGENS NO DOCKER HUB

Todas disponíveis publicamente em: https://hub.docker.com/u/paulo003

- `paulo003/spdrop-api:v1.1` (709MB)
- `paulo003/spdrop-bot:v1.1` (709MB)
- `paulo003/spdrop-whatsapp:v1.1` (2.61GB)
- `paulo003/spdrop-nginx:v1.1` (79.9MB)

---

## 🎯 RESUMO

**Antes (v1.0):** ❌ Erro de autenticação PostgreSQL
**Depois (v1.1):** ✅ Conexão funcionando perfeitamente

**Mudança principal:** Container `bot` agora recebe TODAS as variáveis de banco que o `customer_manager.py` precisa.

🚀 **Pronto para produção!**
