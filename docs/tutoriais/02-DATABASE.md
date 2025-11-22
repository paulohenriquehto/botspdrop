# 02 - Configuração do PostgreSQL e Banco de Dados

## 🗄️ Visão Geral

O sistema usa PostgreSQL 16-alpine para armazenar:
- Conversas e histórico
- Clientes e contextos
- Scripts de vendas (110 scripts)
- FAQ (9 perguntas)
- Serviços e agendamentos

---

## 📋 Tabelas do Sistema

### Tabelas Principais

| Tabela | Descrição | Linhas |
|--------|-----------|--------|
| `customers` | Cadastro de clientes | Dinâmico |
| `sessions` | Sessões de conversa | Dinâmico |
| `conversation_history` | Histórico completo de mensagens | Dinâmico |
| `customer_context` | Contexto e notas dos clientes | Dinâmico |
| `services` | Serviços de estética automotiva | 15 fixos |
| `availability` | Horários disponíveis | Dinâmico |
| `appointments` | Agendamentos | Dinâmico |
| `user_preferences` | Preferências dos clientes | Dinâmico |
| `vehicle_types` | Tipos de veículos | 10 fixos |
| `service_pricing` | Preços por tipo de veículo | Dinâmico |
| `vehicle_patterns` | Padrões de identificação de veículos | 25 fixos |
| `conversation_scripts` | Scripts de vendas (SPIN, SNAP, etc.) | 110 fixos |
| `spdrop_faq` | Perguntas frequentes | 9 fixos |

---

## 🔧 Script de Inicialização (init.sql)

O arquivo `init.sql` é executado automaticamente quando o container PostgreSQL é criado pela primeira vez.

### Estrutura das Tabelas

#### 1. customers
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Função:** Armazenar dados básicos dos clientes.

---

#### 2. sessions
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);
```

**Função:** Gerenciar sessões de conversa (formato: `whatsapp_5511999999999`).

**Índices:**
```sql
CREATE INDEX idx_sessions_customer_id ON sessions(customer_id);
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
```

---

#### 3. conversation_history
```sql
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    customer_id INTEGER,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR(50)
);
```

**Função:** Armazenar todas as mensagens trocadas entre cliente e agente.

**Índices:**
```sql
CREATE INDEX idx_conversation_session_id ON conversation_history(session_id);
CREATE INDEX idx_conversation_customer_id ON conversation_history(customer_id);
```

---

#### 4. customer_context
```sql
CREATE TABLE customer_context (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    car_model VARCHAR(255),
    car_color VARCHAR(50),
    car_condition VARCHAR(100),
    services_purchased TEXT,
    last_service_date DATE,
    total_spent DECIMAL(10, 2) DEFAULT 0.00,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Função:** Armazenar contexto específico de cada cliente (carro, compras, notas).

---

#### 5. services
```sql
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Serviços incluídos (15):**
1. Lavagem Completa - R$ 80
2. Polimento - R$ 150
3. Higienização - R$ 120
4. Vitrificação - R$ 100
5. Cristalização - R$ 200
6. Wax Aplicação - R$ 90
7. Limpeza de Motor - R$ 85
8. Proteção de Pneus - R$ 55
9. Blindagem Cerâmica - R$ 350
10. Estética de Rodão - R$ 95
11. Couro Tratado - R$ 140
12. Odorizante Premium - R$ 65
13. Espelhamento de Pintura - R$ 180
14. Selagem de Vidros - R$ 110
15. Pacote Completo VIP - R$ 750

---

#### 6. vehicle_types
```sql
CREATE TABLE vehicle_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    multiplier DECIMAL(3, 2) NOT NULL DEFAULT 1.00,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tipos de veículos (10):**
- Sedan (1.0x)
- Hatch (1.0x)
- SUV Compacta (1.3x)
- SUV Média (1.4x)
- SUV Grande (1.5x)
- Camionete Pequena (1.35x)
- Camionete Média (1.45x)
- Camionete Grande (1.6x)
- Conversível (1.25x)
- Coupe (1.2x)

---

#### 7. vehicle_patterns
```sql
CREATE TABLE vehicle_patterns (
    id SERIAL PRIMARY KEY,
    pattern VARCHAR(255) NOT NULL,
    vehicle_type_id INTEGER REFERENCES vehicle_types(id),
    examples TEXT
);
```

**Função:** Identificar tipo de veículo por padrões (ex: "civic" → Sedan).

---

## 📥 Inserção de Dados Iniciais

O `init.sql` já inclui:

✅ **15 serviços** com preços e durações
✅ **10 tipos de veículos** com multiplicadores
✅ **25 padrões de veículos** (Civic, Corolla, HR-V, etc.)
✅ **8 horários de disponibilidade** (exemplo)

---

## 🔌 Conexão com o Banco

### Via Docker (dentro do container bot)

```python
# database.py
DATABASE_URL = os.getenv("DATABASE_URL")
# postgresql://vanlu_user:vanlu_password@postgres:5432/vanlu_db
```

**Importante:** Use `postgres` como host (nome do container).

---

### Via Host (seu computador)

```bash
# CLI do PostgreSQL
psql -h localhost -p 5432 -U vanlu_user -d vanlu_db

# Senha: vanlu_password
```

---

## 🧪 Comandos SQL Úteis

### Conectar ao Banco

```bash
docker exec -it vanlu_postgres psql -U vanlu_user -d vanlu_db
```

---

### Verificar Tabelas

```sql
-- Listar todas as tabelas
\dt

-- Descrever estrutura de uma tabela
\d customers

-- Contar registros
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM conversation_history;
SELECT COUNT(*) FROM sessions;
```

---

### Consultar Conversas

```sql
-- Ver últimas 10 conversas
SELECT
    customer_id,
    session_id,
    user_message,
    agent_response,
    timestamp
FROM conversation_history
ORDER BY timestamp DESC
LIMIT 10;
```

---

### Consultar Clientes

```sql
-- Ver todos os clientes
SELECT * FROM customers ORDER BY created_at DESC;

-- Ver cliente com contexto
SELECT
    c.id,
    c.name,
    c.phone,
    cc.car_model,
    cc.total_spent,
    cc.notes
FROM customers c
LEFT JOIN customer_context cc ON c.id = cc.customer_id
ORDER BY c.created_at DESC;
```

---

### Consultar Sessões Ativas

```sql
-- Sessões ativas
SELECT * FROM sessions WHERE status = 'active' ORDER BY started_at DESC;

-- Total de mensagens por sessão
SELECT
    session_id,
    COUNT(*) as total_messages
FROM conversation_history
GROUP BY session_id
ORDER BY total_messages DESC;
```

---

### Consultar Serviços

```sql
-- Todos os serviços com preços
SELECT name, price, duration_minutes FROM services ORDER BY price;

-- Serviços mais caros
SELECT name, price FROM services ORDER BY price DESC LIMIT 5;
```

---

## 🗑️ Limpar Dados de Teste

```sql
-- Limpar histórico de conversas (mas manter estrutura)
TRUNCATE TABLE conversation_history CASCADE;
TRUNCATE TABLE sessions CASCADE;
TRUNCATE TABLE customer_context CASCADE;
TRUNCATE TABLE customers CASCADE;

-- Verificar limpeza
SELECT COUNT(*) FROM conversation_history; -- Deve retornar 0
SELECT COUNT(*) FROM sessions; -- Deve retornar 0
```

⚠️ **Cuidado:** Isso apaga TODOS os dados de clientes e conversas!

---

## 🔐 Segurança

### Senhas

**Padrão (desenvolvimento):**
- User: `vanlu_user`
- Password: `vanlu_password`
- Database: `vanlu_db`

**Produção (recomendado):**
```yaml
environment:
  POSTGRES_USER: vanlu_prod
  POSTGRES_PASSWORD: SuaSenhaForte123!@#
  POSTGRES_DB: vanlu_production
```

---

### Backup

```bash
# Backup completo
docker exec vanlu_postgres pg_dump -U vanlu_user vanlu_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker exec -i vanlu_postgres psql -U vanlu_user -d vanlu_db < backup_20251119.sql
```

---

## 📊 Monitoramento

### Tamanho do Banco

```sql
-- Tamanho do banco de dados
SELECT pg_size_pretty(pg_database_size('vanlu_db'));

-- Tamanho de cada tabela
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

### Performance de Índices

```sql
-- Ver índices existentes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Estatísticas de uso dos índices
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## 🔧 Manutenção

### Vacuum (Limpeza)

```sql
-- Limpar tabelas (recomendado mensalmente)
VACUUM ANALYZE conversation_history;
VACUUM ANALYZE sessions;
VACUUM ANALYZE customers;
```

---

### Reindexação

```sql
-- Reindexar todas as tabelas
REINDEX DATABASE vanlu_db;
```

---

## ⚠️ Troubleshooting

### Container não inicia

```bash
# Ver logs
docker compose logs postgres

# Verificar healthcheck
docker inspect vanlu_postgres | grep -A 10 Health
```

---

### Não consegue conectar

```bash
# Verificar se porta está disponível
sudo lsof -i :5432

# Testar conexão
docker exec vanlu_postgres pg_isready -U vanlu_user -d vanlu_db
```

**Esperado:** `vanlu_db accepting connections`

---

### Erro "database does not exist"

```bash
# Recriar banco
docker compose down -v
docker compose up -d postgres

# Aguardar 10 segundos
docker compose logs postgres | grep "database system is ready"
```

---

### Dados perdidos após restart

**Causa:** Volume não foi criado corretamente.

**Solução:**
```bash
# Verificar volumes
docker volume ls | grep postgres_data

# Se não existir, criar manualmente
docker volume create vanlu-agente_postgres_data
```

---

## 📝 Scripts SQL Customizados

### Adicionar Scripts de Conversação

Os scripts de vendas estão em um CSV separado. Para importar:

```sql
-- Via COPY (dentro do container)
COPY conversation_scripts(category, script_name, script_text, tags, usage_context)
FROM '/app/data/conversation_scripts.csv'
DELIMITER ','
CSV HEADER;
```

---

### Adicionar FAQ

```sql
-- Via COPY
COPY spdrop_faq(pergunta, resposta, categoria, palavras_chave)
FROM '/app/data/faq.csv'
DELIMITER ','
CSV HEADER;
```

---

## ✅ Checklist de Verificação

- [ ] PostgreSQL container está rodando
- [ ] Banco `vanlu_db` foi criado
- [ ] 14 tabelas foram criadas
- [ ] 15 serviços foram inseridos
- [ ] 10 tipos de veículos foram inseridos
- [ ] 25 padrões de veículos foram inseridos
- [ ] Índices foram criados corretamente
- [ ] Consegue conectar via psql
- [ ] Healthcheck está OK

---

## 📚 Próximos Passos

**[03-WHATSAPP.md](./03-WHATSAPP.md)** → Configuração do WhatsApp Web.js

---

**Status:** ✅ Banco de dados configurado e pronto
