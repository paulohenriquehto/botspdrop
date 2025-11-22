# 🚀 INSTRUÇÕES COMPLETAS - DEPLOY NA VPS

## 📦 Arquivos necessários na VPS

Você precisa copiar estes arquivos para a VPS:

1. `docker-compose.prod.yml` - Configuração dos containers
2. `.env` - Variáveis de ambiente (com suas credenciais)
3. `reset.sh` - Script de reset completo
4. `init-db.sh` - Script de inicialização do banco

---

## 🔧 PASSO A PASSO

### 1️⃣ Copiar arquivos do seu PC para VPS

```bash
# Do seu computador local
scp docker-compose.prod.yml root@SEU_IP_VPS:/home/ubuntu/
scp .env root@SEU_IP_VPS:/home/ubuntu/
scp reset.sh root@SEU_IP_VPS:/home/ubuntu/
scp init-db.sh root@SEU_IP_VPS:/home/ubuntu/
```

### 2️⃣ Conectar na VPS

```bash
ssh root@SEU_IP_VPS
cd /home/ubuntu
```

### 3️⃣ Dar permissão de execução aos scripts

```bash
chmod +x reset.sh
chmod +x init-db.sh
```

### 4️⃣ Executar reset completo

```bash
bash reset.sh
```

**O que este script faz:**
- Para todos os containers
- Remove volumes completamente
- Limpa cache do Docker
- Recria tudo com as variáveis corretas do `.env`

### 5️⃣ Inicializar banco de dados

```bash
bash init-db.sh
```

**O que este script faz:**
- Cria o arquivo `init.sql` se não existir
- Executa SQL para criar tabelas
- Verifica se tabelas foram criadas
- Testa conexão do bot com PostgreSQL

### 6️⃣ Verificar logs

```bash
docker-compose -f docker-compose.prod.yml logs -f bot
```

Pressione `Ctrl+C` para sair.

### 7️⃣ Testar

Envie uma mensagem pelo WhatsApp para o número conectado!

---

## ✅ CHECKLIST DE VERIFICAÇÃO

- [ ] Porta 80 aberta no firewall da VPS
- [ ] Porta 80 aberta no Security Group do provedor
- [ ] Arquivo `.env` com credenciais corretas
- [ ] Scripts com permissão de execução (`chmod +x`)
- [ ] Todos containers rodando (`docker-compose ps`)
- [ ] Tabelas criadas no banco (`\dt` no psql)
- [ ] Bot conecta no PostgreSQL sem erros
- [ ] WhatsApp autenticado (QR Code escaneado)

---

## 🔍 TROUBLESHOOTING

### ❌ Erro: "password authentication failed"

**Solução:**
```bash
# Execute o reset completo
bash reset.sh
bash init-db.sh
```

### ❌ Containers reiniciando constantemente

**Ver qual container:**
```bash
docker-compose -f docker-compose.prod.yml ps
```

**Ver logs:**
```bash
docker-compose -f docker-compose.prod.yml logs NOME_DO_CONTAINER
```

### ❌ Não consigo acessar http://SEU_IP

**Verificar:**
1. Porta 80 aberta no firewall: `sudo ufw status`
2. Nginx rodando: `docker ps | grep nginx`
3. Security Group do provedor liberado

### ❌ WhatsApp não conecta (QR Code não aparece)

**Ver logs:**
```bash
docker-compose -f docker-compose.prod.yml logs -f whatsapp
```

**Resetar autenticação:**
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
# Aguardar e acessar: http://SEU_IP/whatsapp/
```

---

## 🔄 COMANDOS ÚTEIS

### Ver status de todos os containers
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Ver logs de um container específico
```bash
docker-compose -f docker-compose.prod.yml logs -f bot
docker-compose -f docker-compose.prod.yml logs -f whatsapp
docker-compose -f docker-compose.prod.yml logs -f postgres
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Reiniciar um container específico
```bash
docker-compose -f docker-compose.prod.yml restart bot
```

### Parar tudo
```bash
docker-compose -f docker-compose.prod.yml down
```

### Subir tudo novamente
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Acessar PostgreSQL diretamente
```bash
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db
```

Comandos úteis no psql:
- `\dt` - Listar tabelas
- `\d customers` - Descrever tabela customers
- `SELECT * FROM customers;` - Ver dados
- `\q` - Sair

### Ver variáveis de ambiente de um container
```bash
docker exec spdrop_bot env | grep -E "OPENAI|GROQ|DATABASE"
```

---

## 📊 ARQUITETURA

```
Internet
    ↓
[Porta 80] ← Firewall VPS + Security Group
    ↓
[NGINX] ← Gateway público
    ↓
Rede Interna Docker (spdrop_network)
    ├── [API] (8000) ← Dashboard Admin
    ├── [BOT] (5000) ← Processamento IA
    ├── [WhatsApp] (3000) ← QR Code + Mensagens
    └── [PostgreSQL] (5432) ← Banco de Dados
```

**Segurança:**
- ✅ Apenas porta 80 exposta publicamente
- ✅ Todos serviços em rede interna isolada
- ✅ PostgreSQL inacessível de fora
- ✅ Rate limiting no Nginx
- ✅ CORS restrito

---

## 🆘 SUPORTE

Se ainda tiver problemas, envie:

```bash
# 1. Status
docker-compose -f docker-compose.prod.yml ps

# 2. Logs do bot
docker-compose -f docker-compose.prod.yml logs --tail=50 bot

# 3. Logs do postgres
docker-compose -f docker-compose.prod.yml logs --tail=30 postgres

# 4. Verificar .env
cat .env | grep -v "KEY=" | grep -v "PASSWORD="
```
