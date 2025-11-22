# 🤖 Vanlu WhatsApp Bot - Guia Completo

Sistema completo de atendimento automatizado via WhatsApp usando WAHA + FastAPI + Agente IA.

## 📋 Pré-requisitos

- Docker e Docker Compose
- Python 3.10+
- WhatsApp instalado no celular

## 🚀 Instalação Rápida

### 1. Clonar e configurar

```bash
cd "/home/paulo/Projeto/Vanlu agente"

# Verificar .env (já configurado)
cat .env
```

### 2. Iniciar sistema

```bash
# Dar permissão ao script
chmod +x start.sh

# Iniciar tudo
./start.sh
```

### 3. Conectar WhatsApp

1. Acesse: http://localhost:3000
2. Vá em "Sessions" → "Start New Session"
3. Nome da sessão: `default`
4. Configure webhook:
   - URL: `http://bot:5000/webhook`
   - Events: `message`
5. Clique em "Start"
6. Escaneie o QR Code com seu WhatsApp

## 🏗️ Arquitetura

```
WhatsApp <--> WAHA <--> FastAPI <--> Agente Luciano <--> PostgreSQL
```

### Componentes

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **WAHA** | 3000 | API WhatsApp |
| **FastAPI Bot** | 5000 | Servidor de webhooks |
| **PostgreSQL** | 5432 | Banco de dados |

## 📝 Como Funciona

### Fluxo de Mensagem

1. **Cliente envia mensagem** via WhatsApp
2. **WAHA recebe** e envia webhook para FastAPI (porta 5000)
3. **FastAPI** processa:
   - Identifica/cria cliente no banco
   - Adiciona `customer_id` ao contexto
   - Envia para Agente Luciano
4. **Agente Luciano** processa com IA (GPT-4.1-mini)
5. **FastAPI** envia resposta de volta via WAHA
6. **Cliente recebe** resposta no WhatsApp

### Sistema de Persistência

- **customer_id automático**: Telefone é mapeado para ID único
- **Veículo salvo**: Agente salva modelo do carro na primeira conversa
- **Contexto mantido**: Conversas futuras lembram do cliente

## 🧪 Testar

### 1. Verificar se está funcionando

```bash
# Status geral
docker ps | grep vanlu

# Logs do bot
docker logs -f vanlu_bot

# Logs do WAHA
docker logs -f vanlu_waha

# Health check
curl http://localhost:5000/health
```

### 2. Teste com WhatsApp

Envie mensagem para o número conectado:

```
Olá, quanto custa lavagem completa?
```

O bot deve responder perguntando o modelo do carro.

### 3. Testar cliente recorrente

Envie outra mensagem depois:

```
Quero fazer polimento
```

O bot deve lembrar do seu carro e dar o preço direto.

## 🛠️ Comandos Úteis

```bash
# Parar tudo
docker compose down

# Reiniciar tudo
docker compose restart

# Rebuild do bot (após mudanças no código)
docker compose up -d --build bot

# Ver logs em tempo real
docker logs -f vanlu_bot

# Acessar banco de dados
docker exec -it vanlu_postgres psql -U vanlu_user -d vanlu_db

# Ver clientes cadastrados
docker exec vanlu_postgres psql -U vanlu_user -d vanlu_db -c "SELECT id, name, phone FROM customers"

# Ver veículos salvos
docker exec vanlu_postgres psql -U vanlu_user -d vanlu_db -c "SELECT customer_id, car_model FROM customer_context"
```

## 🐛 Troubleshooting

### WAHA não conecta

```bash
# Verificar logs
docker logs vanlu_waha

# Reiniciar sessão
curl -X DELETE http://localhost:3000/api/sessions/default
docker compose restart waha
```

### Bot não responde

```bash
# Verificar logs
docker logs -f vanlu_bot

# Verificar webhook configurado
curl http://localhost:3000/api/sessions/default

# Testar endpoint diretamente
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"message","payload":{"from":"5511999999999","body":"teste"}}'
```

### Banco de dados

```bash
# Verificar conexão
docker exec vanlu_postgres pg_isready -U vanlu_user

# Resetar banco (CUIDADO!)
docker compose down -v
docker compose up -d postgres
sleep 5
# Aguardar init.sql rodar
```

## 📊 Monitoramento

### Métricas importantes

```bash
# Número de clientes
docker exec vanlu_postgres psql -U vanlu_user -d vanlu_db -c \
  "SELECT COUNT(*) as total_clientes FROM customers"

# Conversas hoje
docker exec vanlu_postgres psql -U vanlu_user -d vanlu_db -c \
  "SELECT COUNT(*) as conversas_hoje FROM conversation_history
   WHERE DATE(timestamp) = CURRENT_DATE"

# Veículos cadastrados
docker exec vanlu_postgres psql -U vanlu_user -d vanlu_db -c \
  "SELECT COUNT(*) as veiculos FROM customer_context WHERE car_model IS NOT NULL"
```

## 🔧 Desenvolvimento

### Rodar localmente (sem Docker)

```bash
# Terminal 1: FastAPI
python main.py

# Terminal 2: WAHA (Docker)
docker compose up waha

# Terminal 3: PostgreSQL (Docker)
docker compose up postgres
```

### Estrutura de Arquivos

```
.
├── main.py                    # Servidor FastAPI
├── waha_integration.py        # Cliente WAHA
├── customer_manager.py        # Gerenciador de clientes
├── agentes/
│   ├── agente_suporte.py     # Agente Luciano
│   └── agente_processador_pedidos.py
├── tools/
│   ├── database_tools.py
│   ├── memory_tools.py
│   ├── pricing_tools.py
│   └── agent_tools.py
├── docker-compose.yml         # Orquestração
├── Dockerfile                 # Build do bot
└── .env                       # Configurações
```

## 🎯 Próximos Passos

- [x] Integração WAHA + FastAPI
- [x] Sistema de customer_id
- [x] Persistência de veículos
- [ ] Suporte a mídias (imagens, áudios)
- [ ] Dashboard de métricas
- [ ] Deploy em produção

## 📞 Suporte

Para problemas ou dúvidas, verificar logs:

```bash
docker logs vanlu_bot
docker logs vanlu_waha
```
