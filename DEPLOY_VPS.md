# 🚀 Deploy SPDrop na VPS

Guia completo para subir o projeto SPDrop na sua VPS usando Docker Hub.

## 📋 Pré-requisitos na VPS

1. **Docker instalado**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

2. **Docker Compose instalado**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🔧 Passo a Passo

### 1. Criar diretório do projeto na VPS
```bash
mkdir -p ~/spdrop
cd ~/spdrop
```

### 2. Criar arquivo docker-compose.prod.yml
```bash
nano docker-compose.prod.yml
```

Cole o conteúdo do arquivo `docker-compose.prod.yml` deste repositório.

### 3. Criar arquivo .env com suas credenciais
```bash
nano .env
```

Cole e edite com seus dados reais:
```env
# BANCO DE DADOS
POSTGRES_USER=spdrop_user
POSTGRES_PASSWORD=SuaSenhaSuperSeguraAqui123!
POSTGRES_DB=spdrop_db

# JWT
JWT_SECRET_KEY=ChaveJWTSuperSeguraComMaisde32Caracteres!

# APIs DE IA
OPENAI_API_KEY=sk-sua-chave-openai-aqui
GROQ_API_KEY=sua-chave-groq-aqui
```

### 4. Fazer pull das imagens do Docker Hub
```bash
docker pull paulo003/spdrop-api:v1.0
docker pull paulo003/spdrop-bot:v1.0
docker pull paulo003/spdrop-whatsapp:v1.0
docker pull paulo003/spdrop-nginx:v1.0
docker pull postgres:16-alpine
```

### 5. Subir os containers
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 6. Verificar status dos containers
```bash
docker-compose -f docker-compose.prod.yml ps
```

Todos devem estar com status "Up".

### 7. Ver logs (se necessário)
```bash
# Todos os containers
docker-compose -f docker-compose.prod.yml logs -f

# Container específico
docker-compose -f docker-compose.prod.yml logs -f whatsapp
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f bot
docker-compose -f docker-compose.prod.yml logs -f nginx
```

## 🌐 Acessar o Sistema

Após subir, acesse:
- **Landing Page:** `http://SEU_IP_VPS/`
- **QR Code WhatsApp:** `http://SEU_IP_VPS/whatsapp/`
- **API Docs:** `http://SEU_IP_VPS/api/docs`
- **Health Check:** `http://SEU_IP_VPS/health`

## 🔒 Configurar HTTPS (Opcional mas Recomendado)

### Usando Certbot + Let's Encrypt

1. Instalar Certbot:
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

2. Obter certificado SSL:
```bash
sudo certbot --nginx -d seudominio.com
```

3. Editar `docker-compose.prod.yml` e descomentar porta 443:
```yaml
nginx:
  ports:
    - "80:80"
    - "443:443"  # Descomente esta linha
```

4. Reiniciar nginx:
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

## 🛠️ Comandos Úteis

### Parar containers
```bash
docker-compose -f docker-compose.prod.yml down
```

### Parar e remover volumes (CUIDADO: apaga dados)
```bash
docker-compose -f docker-compose.prod.yml down -v
```

### Reiniciar um serviço específico
```bash
docker-compose -f docker-compose.prod.yml restart whatsapp
```

### Atualizar imagens
```bash
# Pull novas versões
docker pull paulo003/spdrop-api:latest
docker pull paulo003/spdrop-bot:latest
docker pull paulo003/spdrop-whatsapp:latest
docker pull paulo003/spdrop-nginx:latest

# Recriar containers com novas imagens
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### Ver uso de recursos
```bash
docker stats
```

## 📊 Arquitetura de Segurança

✅ **Apenas porta 80 (e 443 para HTTPS) exposta**
✅ **Todos os serviços em rede interna isolada**
✅ **Rate limiting configurado**
✅ **CORS restrito**
✅ **Endpoints internos bloqueados**

## ⚠️ Segurança Importante

1. **Nunca exponha o arquivo .env**
2. **Use senhas fortes para PostgreSQL**
3. **Troque a JWT_SECRET_KEY**
4. **Configure HTTPS em produção**
5. **Mantenha as imagens atualizadas**
6. **Faça backup regular do volume postgres_data**

## 🗄️ Backup do Banco de Dados

### Fazer backup
```bash
docker exec spdrop_postgres pg_dump -U spdrop_user spdrop_db > backup_$(date +%Y%m%d).sql
```

### Restaurar backup
```bash
cat backup_20250122.sql | docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db
```

## 🔄 Inicializar Banco de Dados

Se precisar rodar o script de inicialização:
```bash
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql
```

## 📞 Suporte

- GitHub Issues: https://github.com/seu-usuario/spdrop/issues
- Docker Hub: https://hub.docker.com/u/paulo003
