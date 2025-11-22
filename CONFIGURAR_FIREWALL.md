# 🔥 Configurar Firewall na VPS

## Portas que precisam estar abertas:

- **Porta 80** (HTTP) - **OBRIGATÓRIA**
- **Porta 443** (HTTPS) - **RECOMENDADA** (para SSL/TLS)
- **Porta 22** (SSH) - Já deve estar aberta para você acessar a VPS

## 🛡️ Ubuntu/Debian (UFW - Uncomplicated Firewall)

### 1. Verificar status do UFW
```bash
sudo ufw status
```

### 2. Se estiver inativo, ativar (CUIDADO: configure SSH primeiro!)
```bash
# Permitir SSH primeiro (para não perder acesso)
sudo ufw allow 22/tcp

# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir HTTPS (opcional mas recomendado)
sudo ufw allow 443/tcp

# Ativar firewall
sudo ufw enable

# Verificar regras
sudo ufw status numbered
```

### 3. Se UFW já estiver ativo, apenas adicionar as portas
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
sudo ufw status
```

## 🔴 CentOS/RHEL/Rocky Linux (FirewallD)

### 1. Verificar status do firewalld
```bash
sudo firewall-cmd --state
```

### 2. Abrir portas
```bash
# Permitir HTTP
sudo firewall-cmd --permanent --add-service=http

# Permitir HTTPS
sudo firewall-cmd --permanent --add-service=https

# Ou usar números de porta diretamente
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp

# Recarregar firewall
sudo firewall-cmd --reload

# Verificar regras
sudo firewall-cmd --list-all
```

## ☁️ Provedores de VPS (AWS, DigitalOcean, Vultr, etc.)

Além do firewall do sistema operacional, você também precisa configurar o **Security Group** ou **Firewall** no painel do provedor:

### AWS (EC2 Security Groups)
1. Acesse EC2 Console → Security Groups
2. Selecione o Security Group da sua instância
3. Adicione Inbound Rules:
   - Type: HTTP, Protocol: TCP, Port: 80, Source: 0.0.0.0/0
   - Type: HTTPS, Protocol: TCP, Port: 443, Source: 0.0.0.0/0

### DigitalOcean (Cloud Firewall)
1. Acesse Networking → Firewalls
2. Crie ou edite firewall
3. Adicione Inbound Rules:
   - HTTP: TCP, Port 80, All IPv4, All IPv6
   - HTTPS: TCP, Port 443, All IPv4, All IPv6

### Vultr / Linode / Hetzner
Similar: adicione regras permitindo tráfego nas portas 80 e 443 de qualquer origem (0.0.0.0/0)

## ✅ Verificar se as portas estão abertas

### Dentro da VPS
```bash
# Verificar se o nginx está rodando e escutando na porta 80
sudo netstat -tulpn | grep :80

# Ou usando ss
sudo ss -tulpn | grep :80
```

### De fora da VPS (do seu computador local)
```bash
# Testar conectividade na porta 80
nc -zv SEU_IP_VPS 80

# Ou usar telnet
telnet SEU_IP_VPS 80

# Ou usar curl
curl -I http://SEU_IP_VPS
```

### Ferramenta online
Acesse: https://www.yougetsignal.com/tools/open-ports/
- Digite seu IP da VPS
- Digite a porta 80
- Click "Check"

## 🔍 Troubleshooting

### Problema: Não consigo acessar http://SEU_IP

**1. Verificar se o nginx está rodando:**
```bash
docker ps | grep nginx
```

**2. Verificar se a porta está sendo escutada:**
```bash
sudo netstat -tulpn | grep :80
```

**3. Verificar firewall local (UFW):**
```bash
sudo ufw status
```

**4. Verificar firewall do provedor:**
- Acesse o painel da VPS
- Verifique Security Groups/Firewall
- Certifique-se que porta 80 está liberada para 0.0.0.0/0

**5. Testar diretamente:**
```bash
# Dentro da VPS
curl http://localhost

# De fora
curl http://SEU_IP_VPS
```

## 📋 Checklist Rápido

- [ ] Porta 22 (SSH) aberta no firewall do SO
- [ ] Porta 80 (HTTP) aberta no firewall do SO
- [ ] Porta 443 (HTTPS) aberta no firewall do SO (opcional)
- [ ] Porta 80 liberada no Security Group do provedor
- [ ] Porta 443 liberada no Security Group do provedor (opcional)
- [ ] Docker containers rodando (`docker ps`)
- [ ] Nginx respondendo na porta 80 (`curl localhost`)
- [ ] Acesso externo funcionando (`curl http://SEU_IP_VPS`)

## ⚠️ IMPORTANTE - Segurança

**NÃO abra portas desnecessárias!**

❌ **NUNCA abra estas portas publicamente:**
- 5432 (PostgreSQL)
- 3000 (WhatsApp Service)
- 5000 (Bot Service)
- 8000 (API interna)

✅ **Apenas estas portas devem estar públicas:**
- 22 (SSH - restringir por IP se possível)
- 80 (HTTP)
- 443 (HTTPS)

Todos os outros serviços devem estar na rede interna do Docker (já configurado no docker-compose.prod.yml).

## 🔐 Segurança Extra (Opcional mas Recomendado)

### Restringir SSH apenas ao seu IP
```bash
# Remover regra atual de SSH
sudo ufw delete allow 22/tcp

# Permitir SSH apenas do seu IP
sudo ufw allow from SEU_IP_FIXO to any port 22
```

### Usar fail2ban para proteção contra brute force
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```
