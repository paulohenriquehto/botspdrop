# SPDrop Admin API

API REST completa para gerenciamento e controle do bot SPDrop.

## 🚀 Iniciar a API

### Com Docker (Recomendado)

```bash
docker compose up -d api
```

A API estará disponível em: **http://localhost:8000**

### Localmente

```bash
python3 api_server.py
```

## 📚 Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Autenticação

### 1. Criar primeiro usuário admin

```bash
python3 create_admin.py
```

### 2. Fazer login e obter token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin@123456"
  }'
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@spdrop.com",
    "full_name": "Administrador SPDrop",
    "role": "admin"
  }
}
```

### 3. Usar o token nas requisições

Todas as rotas protegidas requerem o header `Authorization`:

```bash
curl http://localhost:8000/api/dashboard/metrics/today \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 📊 Endpoints Disponíveis

### Autenticação (`/api/auth`)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/login` | Fazer login e obter token JWT |
| POST | `/api/auth/register` | Registrar novo admin |
| GET | `/api/auth/me` | Obter dados do usuário autenticado |
| POST | `/api/auth/logout` | Logout (cliente descarta token) |

### Dashboard (`/api/dashboard`)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/dashboard/metrics/today` | Métricas do dia atual |
| GET | `/api/dashboard/metrics/period` | Métricas de um período (query: start_date, end_date) |
| GET | `/api/dashboard/stats/summary` | Resumo geral de estatísticas |
| GET | `/api/dashboard/customers/recent` | Clientes mais recentes (query: limit) |
| POST | `/api/dashboard/metrics/update` | Atualizar métricas manualmente |

### Conversas e Trials (`/api/conversations`)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/conversations/history/{customer_id}` | Histórico de conversas de um cliente |
| GET | `/api/conversations/recent` | Conversas mais recentes |
| GET | `/api/conversations/trials/active` | Testes de 7 dias ativos |
| GET | `/api/conversations/trials/expired` | Testes expirados (follow-up) |
| GET | `/api/conversations/trials/all` | Todos os testes (query: status, limit) |
| GET | `/api/conversations/trials/{trial_id}` | Detalhes de um teste específico |
| PATCH | `/api/conversations/trials/{trial_id}/status` | Atualizar status de um teste |
| POST | `/api/conversations/trials/{trial_id}/convert` | Marcar teste como convertido |
| GET | `/api/conversations/messages/recent` | Mensagens mais recentes do log |

### QR Code WhatsApp (`/api/qrcode`)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/qrcode/generate` | Gerar QR Code para autenticação |
| GET | `/api/qrcode/status` | Verificar status da conexão WhatsApp |
| POST | `/api/qrcode/disconnect` | Desconectar WhatsApp (logout) |
| POST | `/api/qrcode/restart` | Reiniciar serviço WhatsApp |
| GET | `/api/qrcode/health` | Health check do serviço WhatsApp |

## 📝 Exemplos de Uso

### Obter métricas de hoje

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/dashboard/metrics/today
```

### Buscar testes ativos

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/conversations/trials/active
```

### Converter teste para plano pago

```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_name":"Plano Semestral"}' \
  http://localhost:8000/api/conversations/trials/1/convert
```

### Gerar QR Code WhatsApp

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/qrcode/generate > qrcode.png
```

## 🔧 Configuração

### Variáveis de Ambiente

Arquivo `.env`:

```env
# Banco de Dados
DB_HOST=postgres
DB_PORT=5432
DB_NAME=spdrop_db
DB_USER=spdrop_user
DB_PASSWORD=spdrop_password

# JWT
JWT_SECRET_KEY=sua-chave-secreta-super-segura-aqui

# OpenAI
OPENAI_API_KEY=sk-...
```

## 🗄️ Banco de Dados

### Tabelas da API

- `admin_users`: Usuários administrativos do dashboard
- `audit_log`: Log de auditoria de ações dos admins
- `attendance_metrics`: Métricas diárias de atendimento
- `message_logs`: Log completo de todas as mensagens

### Criar admin via SQL

```sql
-- Gerar hash da senha primeiro com bcrypt
INSERT INTO admin_users (username, password_hash, email, full_name, role, is_active)
VALUES ('admin', '$2b$12$...', 'admin@spdrop.com', 'Admin', 'admin', TRUE);
```

## 🔒 Segurança

- **JWT**: Tokens com expiração de 8 horas
- **Bcrypt**: Senhas hasheadas com salt
- **CORS**: Configurável (padrão: todos os origens)
- **Audit Log**: Todas as ações críticas são registradas

## 📈 Próximos Passos

1. **Frontend React**: Criar dashboard visual com gráficos
2. **WebSocket**: Notificações em tempo real
3. **Rate Limiting**: Limitar requisições por IP
4. **2FA**: Autenticação de dois fatores
5. **Backup**: Sistema de backup automático

## 🐛 Troubleshooting

### API não responde

```bash
# Verificar se container está rodando
docker compose ps api

# Ver logs
docker logs spdrop_api

# Reiniciar
docker compose restart api
```

### Erro de autenticação

- Verifique se o token não expirou (8 horas)
- Confirme que está usando o header correto: `Authorization: Bearer TOKEN`
- Verifique se o usuário existe e está ativo

### Erro de conexão com banco

- Confirme que o container postgres está rodando
- Verifique as credenciais no `.env`
- Teste conexão: `docker exec spdrop_postgres psql -U spdrop_user -d spdrop_db -c "SELECT 1"`

## 📞 Suporte

Para dúvidas ou problemas:
- Email: admin@spdrop.com
- WhatsApp: (11) 93299-4698
