# 🎤 Configuração da Transcrição de Áudio

## O que foi implementado?

A Gabi agora consegue **receber e entender mensagens de áudio do WhatsApp**!

Quando um cliente envia áudio de voz, o sistema:
1. 🎤 Detecta o áudio automaticamente
2. 📥 Baixa o arquivo de áudio (formato .ogg)
3. 🔄 Transcreve para texto usando **Groq Whisper Large v3 Turbo**
4. 💬 Processa o texto com a Gabi normalmente

## Por que Groq Whisper?

- **12x mais barato** que OpenAI Whisper ($0.03/hora vs $0.36/hora)
- **172x mais rápido** (4.5 min de áudio = 3 segundos de transcrição)
- **Gratuito para testar**
- **Suporta português** nativamente (99+ idiomas)
- **Mesma qualidade** (usa o modelo Whisper da OpenAI)

## Configuração (OBRIGATÓRIO)

### 1. Obter chave da API Groq (GRATUITA)

1. Acesse: https://console.groq.com/keys
2. Faça login ou crie conta (gratuito)
3. Clique em **"Create API Key"**
4. Copie a chave gerada (formato: `gsk_...`)

### 2. Adicionar no .env

Edite o arquivo `.env` e substitua:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Por:

```bash
GROQ_API_KEY=gsk_sua_chave_aqui
```

### 3. Reconstruir e reiniciar containers

```bash
# Parar containers
docker compose down

# Reconstruir imagens (instala biblioteca groq)
docker compose build

# Iniciar novamente
docker compose up -d

# Verificar logs
docker compose logs bot -f
```

## Como testar?

1. Envie um **áudio de voz** pelo WhatsApp para o bot
2. Aguarde alguns segundos
3. A Gabi responderá com base no que você disse no áudio! 🎉

## Logs esperados

Quando funcionar corretamente, você verá nos logs:

```
🎤 Áudio detectado! Baixando...
✅ Áudio baixado com sucesso!
🎤 Áudio detectado! Iniciando transcrição...
📊 Áudio decodificado: 45234 bytes
💾 Áudio salvo temporariamente: /tmp/tmpXYZ.ogg
✅ Transcrição concluída: 'Oi Gabi, quero saber sobre os planos'
🗑️ Arquivo temporário removido
```

## Arquivos modificados

1. **whatsapp-service/server.js** - Detecta e baixa áudio
2. **transcription_service.py** (NOVO) - Serviço de transcrição Groq
3. **main.py** - Integra transcrição no fluxo do webhook
4. **requirements.txt** - Adiciona biblioteca `groq`
5. **.env** - Adiciona `GROQ_API_KEY`

## Troubleshooting

### Erro: "GROQ_API_KEY não encontrada"
- Certifique-se de adicionar a chave no `.env`
- Reinicie os containers com `docker compose restart`

### Erro: "Falha ao baixar áudio"
- Verifique se o WhatsApp Web.js está conectado
- Alguns áudios podem ser muito antigos ou deletados do telefone

### Áudio não é transcrito
- Verifique os logs: `docker compose logs bot -f`
- Teste com um áudio curto (5-10 segundos)
- Verifique se o áudio está em português claro

## Custos

- **Groq:** $0.03/hora de áudio transcrito
- **Exemplo:** 1000 áudios de 30 segundos = 500 minutos = 8.3 horas = **$0.25**
- **Tier gratuito:** Groq oferece créditos gratuitos para testar!

## Suporte a idiomas

O sistema está configurado para **português** (`language="pt"`), mas o Groq Whisper suporta 99+ idiomas. Para mudar:

Edite `transcription_service.py`, linha 52:
```python
language="pt",  # Mude para: "en", "es", etc.
```
