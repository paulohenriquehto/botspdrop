# 00 - Requisitos e Pré-requisitos

## 📋 O Que Você Precisa

### 🖥️ Hardware Mínimo

- **CPU:** 2 cores (4 recomendado)
- **RAM:** 4GB (8GB recomendado)
- **Disco:** 10GB livres
- **Internet:** Conexão estável

### 💻 Sistema Operacional

✅ **Linux** (Ubuntu 20.04+, Debian 11+)
✅ **macOS** (10.15+)
✅ **Windows** (10/11 com WSL2)

---

## 🔧 Software Necessário

### 1. Docker & Docker Compose

**Versões mínimas:**
- Docker: 20.10+
- Docker Compose: 2.0+

**Instalação Ubuntu/Debian:**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalação
docker --version
docker compose version
```

**Instalação macOS:**
```bash
# Instalar via Homebrew
brew install --cask docker

# Ou baixar Docker Desktop:
# https://www.docker.com/products/docker-desktop
```

**Instalação Windows:**
1. Instalar WSL2
2. Baixar Docker Desktop: https://www.docker.com/products/docker-desktop
3. Habilitar integração com WSL2

---

### 2. Git

```bash
# Ubuntu/Debian
sudo apt install -y git

# macOS
brew install git

# Verificar
git --version
```

---

### 3. Editor de Texto (Opcional)

Recomendado:
- **VS Code** - https://code.visualstudio.com/
- **Vim/Nano** - Para edições rápidas
- **Sublime Text**

---

## 🔑 Credenciais Necessárias

### 1. OpenAI API Key

**Como obter:**
1. Acesse: https://platform.openai.com/
2. Faça login ou crie conta
3. Vá em **API Keys**
4. Clique em **Create new secret key**
5. Copie e guarde (não será mostrada novamente!)

**Formato:**
```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Custo estimado:**
- GPT-4.1-mini: ~$0.10 por 1000 mensagens
- Muito econômico para uso comercial

---

### 2. WhatsApp Business (Recomendado)

**Opções:**
- ✅ **WhatsApp Business** - Gratuito, melhor para empresas
- ✅ **WhatsApp Pessoal** - Funciona, mas não recomendado

**Requisitos:**
- Número de telefone válido
- WhatsApp instalado no celular
- **Importante:** Use um número dedicado para o bot

⚠️ **NUNCA use seu número pessoal principal!**

---

### 3. Conta PostgreSQL (Opcional)

- Já incluído no Docker
- Não precisa instalar separadamente
- Configuração automática

---

## 📱 Dispositivos

### Para Configuração Inicial

- **Smartphone** com WhatsApp instalado
- **Câmera** para escanear QR Code
- **Acesso ao celular** durante setup inicial

### Após Configuração

- Sistema roda 24/7 sem necessidade do celular
- WhatsApp Web mantém sessão ativa
- Apenas reinicia se QR Code expirar (raro)

---

## 🌐 Rede

### Portas Necessárias

| Serviço | Porta | Uso |
|---------|-------|-----|
| WhatsApp | 9000 | Acesso ao QR Code |
| Bot API | 5000 | Webhook interno |
| PostgreSQL | 5432 | Banco de dados |

**Firewall:**
```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 9000/tcp  # Apenas se quiser acesso externo ao QR
sudo ufw allow 5000/tcp  # Opcional (interno)
sudo ufw allow 5432/tcp  # Opcional (interno)
```

⚠️ **Atenção:** Para produção, use reverse proxy (Nginx) com HTTPS

---

## 📦 Espaço em Disco

### Estimativa de Uso

- **Imagens Docker:** ~2GB
- **PostgreSQL Data:** ~100MB (inicial)
- **Logs:** ~50MB/mês
- **WhatsApp Session:** ~10MB

**Total recomendado:** 10GB livres

---

## ⚡ Recursos Computacionais

### CPU

- **Idle:** ~5% (aguardando mensagens)
- **Processando:** ~30-50% por mensagem
- **Múltiplas conversas:** ~60-80%

### RAM

- **WhatsApp Service:** ~300MB
- **Bot Service:** ~200MB
- **PostgreSQL:** ~100MB
- **Sistema:** ~500MB
- **Total:** ~1.1GB em uso

Com 4GB RAM, sistema roda confortavelmente.

---

## 🔐 Segurança

### Variáveis de Ambiente

**Criar arquivo `.env` com:**
```env
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxx

# PostgreSQL
DB_HOST=postgres
DB_PORT=5432
DB_NAME=vanlu_db
DB_USER=vanlu_user
DB_PASSWORD=SUA_SENHA_FORTE_AQUI

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=5000
WEBHOOK_URL=http://bot:5000/webhook
```

⚠️ **NUNCA commite .env no Git!**

---

## ✅ Checklist Pré-Instalação

Antes de prosseguir, confirme:

- [ ] Docker instalado e funcionando
- [ ] Docker Compose instalado (versão 2.0+)
- [ ] OpenAI API Key obtida e válida
- [ ] Número de telefone dedicado para WhatsApp
- [ ] WhatsApp instalado no celular
- [ ] Pelo menos 10GB de espaço livre
- [ ] Conexão de internet estável
- [ ] Portas 9000, 5000, 5432 disponíveis
- [ ] Git instalado (para clonar projeto)
- [ ] Editor de texto para editar arquivos

---

## 🧪 Teste de Ambiente

Execute estes comandos para verificar:

```bash
# Docker
docker --version
# Esperado: Docker version 20.10+

# Docker Compose
docker compose version
# Esperado: Docker Compose version v2.0+

# Git
git --version
# Esperado: git version 2.x

# Espaço em disco
df -h .
# Esperado: >10GB disponível

# Portas livres
sudo netstat -tuln | grep -E ':(9000|5000|5432)'
# Esperado: Vazio (portas livres)
```

---

## 🚦 Pronto para Instalar?

Se todos os requisitos estão OK, prossiga para:

**[01-SETUP-INICIAL.md](./01-SETUP-INICIAL.md)** → Instalação do Docker e configuração inicial

---

## 💡 Dicas

### Para Desenvolvedores

- Use VS Code com extensões Docker
- Instale extensão PostgreSQL para gerenciar banco
- Use Docker Desktop para visualizar containers

### Para Produção

- Configure backup automático do PostgreSQL
- Use Docker Swarm ou Kubernetes para escalabilidade
- Implemente monitoramento (Prometheus + Grafana)
- Configure SSL/TLS com Nginx

### Para Testes

- Use conta WhatsApp de teste
- Configure limite de créditos OpenAI
- Faça backup antes de modificações

---

**Próximo:** [01-SETUP-INICIAL.md](./01-SETUP-INICIAL.md)
