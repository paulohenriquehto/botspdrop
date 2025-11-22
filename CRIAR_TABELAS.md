# 🗄️ CRIAR TABELAS NO POSTGRESQL

## ❌ PROBLEMA
```
ERROR: relation "customers" does not exist
ERROR: relation "conversas" does not exist
```

**Causa:** O PostgreSQL subiu sem as tabelas. Precisa executar o `init.sql` que tem TODAS as tabelas do sistema.

---

## ✅ SOLUÇÃO

### PASSO 1: Copiar init.sql para VPS

```bash
# Do seu PC, copiar o arquivo
scp init.sql root@SEU_IP_VPS:/home/ubuntu/
```

### PASSO 2: Executar init.sql no PostgreSQL

```bash
# Na VPS
cd /home/ubuntu

# Executar todas as tabelas de uma vez
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql

# Verificar se as tabelas foram criadas (deve mostrar 20+ tabelas)
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "\dt"
```

**Deve mostrar todas as tabelas:**
```
 admin_users
 attendance_metrics
 audit_log
 conversation_history
 conversation_scripts
 conversas              ← ESSENCIAL para o bot
 customer_context
 customers              ← ESSENCIAL para o bot
 message_logs
 orders
 products
 session
 subscription_plans
 suppliers
 trial_users
 user_preferences
 usuarios               ← ESSENCIAL para API
```

### Método 2: Criar manualmente via Docker (Se não tiver o init.sql)

```bash
# Criar as 3 tabelas essenciais de uma vez
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db << 'EOF'
-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Conversas
CREATE TABLE IF NOT EXISTS conversas (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_id VARCHAR(100)
);

-- Tabela de Usuários Admin
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_conversas_customer ON conversas(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversas_timestamp ON conversas(timestamp);

-- Mostrar tabelas criadas
\dt
EOF
```

## 📊 VERIFICAÇÃO

### Ver todas as tabelas
```bash
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "\dt"
```

**Deve mostrar 20+ tabelas incluindo:**
```
 Schema |         Name          | Type  |    Owner
--------+-----------------------+-------+--------------
 public | admin_users           | table | spdrop_user
 public | conversas             | table | spdrop_user
 public | customers             | table | spdrop_user
 public | subscription_plans    | table | spdrop_user
 public | usuarios              | table | spdrop_user
 ... (total de 20+ tabelas)
```

### Ver estrutura completa de customers
```bash
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "\d customers"
```

### Testar inserção
```bash
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "
INSERT INTO customers (phone, name) VALUES ('557999861603', 'Paulo Teste');
SELECT * FROM customers;
"
```

## 🧪 TESTE FINAL

Após criar as tabelas, envie "oi" pelo WhatsApp e veja os logs:

```bash
docker-compose -f docker-compose.prod.yml logs -f bot
```

**Deve aparecer:**
```
✅ Cliente encontrado: ID=1, Nome=Paulo Teste
```

**EM VEZ DE:**
```
❌ ERROR: relation "customers" does not exist
```

## 🔍 TROUBLESHOOTING

### Erro: "permission denied for schema public"
```bash
# Dar permissões ao usuário
docker exec -it spdrop_postgres psql -U postgres -d spdrop_db -c "
GRANT ALL ON SCHEMA public TO spdrop_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO spdrop_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO spdrop_user;
"
```

### Erro: "database does not exist"
```bash
# Criar o banco
docker exec -it spdrop_postgres psql -U spdrop_user -d postgres -c "CREATE DATABASE spdrop_db;"
```

### Resetar TUDO (cuidado!)
```bash
# Apagar banco e recriar do zero
docker-compose -f docker-compose.prod.yml down -v
docker volume prune -f
docker-compose -f docker-compose.prod.yml up -d
sleep 15
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql
```
