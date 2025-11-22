# 08 - Histórico de Bugs e Correções

## 🐛 Visão Geral

Este documento registra **TODOS os bugs** encontrados durante o desenvolvimento e suas soluções definitivas.

---

## 🔴 BUG #1: Formato @lid Não Suportado

### Data
19/11/2025

### Severidade
**CRÍTICA** 🔴

### Descrição

WhatsApp começou a usar novo formato de ID: `@lid` (Local ID) além do tradicional `@c.us`.

**Sintomas:**
- Bot recebia mensagens de números `@lid`
- Processava normalmente
- **MAS falhava ao enviar resposta**

**Erro:**
```
HTTP 500 - Internal Server Error
Error: Evaluation failed: t
```

**Números afetados:**
```
179839223001153@lid
245908352561231@lid
263539226865688@lid
81780958842940@lid
```

---

### Causa Raiz

```javascript
// whatsapp-service/server.js (ANTES)

app.post('/send', async (req, res) => {
    const { number, message } = req.body;

    // Tentava validar TODOS os números
    const numberId = await client.getNumberId(number);

    if (!numberId) {
        return res.status(404).json({error: 'Número não encontrado'});
    }

    // Usava _serialized
    await client.sendMessage(numberId._serialized, message);
});
```

**Problema:**
- `getNumberId()` **não funciona** com números `@lid`
- Retorna `null` para `@lid`
- Causa falha 404 ou erro de validação

---

### Solução

```javascript
// whatsapp-service/server.js (DEPOIS)

app.post('/send', async (req, res) => {
    const { number, message } = req.body;

    let chatId;

    // ✅ CORREÇÃO: Detectar formato
    if (number.includes('@c.us') || number.includes('@lid')) {
        // Usar diretamente se já formatado
        chatId = number;
    } else {
        // Validar apenas se não formatado
        const numberId = await client.getNumberId(number);

        if (!numberId) {
            return res.status(404).json({
                error: 'Número não encontrado',
                details: 'Este número não está registrado no WhatsApp'
            });
        }

        chatId = numberId._serialized;
    }

    // Enviar usando chatId apropriado
    await client.sendMessage(chatId, message);

    res.json({
        status: 'success',
        message: 'Mensagem enviada com sucesso',
        to: number
    });
});
```

---

### Teste da Correção

```bash
# Testar com @c.us (tradicional)
curl -X POST http://localhost:9000/send \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999@c.us",
    "message": "Teste @c.us"
  }'

# Testar com @lid (novo)
curl -X POST http://localhost:9000/send \
  -H "Content-Type: application/json" \
  -d '{
    "number": "179839223001153@lid",
    "message": "Teste @lid"
  }'

# Testar sem sufixo (validação)
curl -X POST http://localhost:9000/send \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "message": "Teste sem sufixo"
  }'
```

**Resultado:** ✅ Todos funcionam

---

### Arquivo Modificado

- `whatsapp-service/server.js` (linhas 268-302)

### Rebuild Necessário

```bash
docker compose build whatsapp
docker compose up -d whatsapp
```

---

### Impacto

**Antes:** ~40% dos números não recebiam respostas (todos com @lid)
**Depois:** 100% dos números funcionam

---

## 🟡 BUG #2: Mensagens Agrupadas Demais

### Data
19/11/2025

### Severidade
**MÉDIA** 🟡

### Descrição

Sistema enviava mensagens **agrupadas** ao invés de **micro mensagens** separadas.

**Sintomas:**
- Bot enviava parágrafos juntos
- Parecia robótico
- Usuário via mensagem grande de uma vez

**Exemplo do problema:**
```
Bot (09:00:00): "Olá, João! Eu sou a Gabi da SPDrop.
Vi que você está interessado.
Temos lavagem por R$80 e polimento por R$150.
Qual serviço você procura?"
```

**Desejado:**
```
Bot (09:00:00): "Olá, João! 😊"
Bot (09:00:03): "Eu sou a Gabi da SPDrop."
Bot (09:00:07): "Vi que você está interessado."
Bot (09:00:11): "Temos lavagem por R$80 e polimento por R$150."
Bot (09:00:15): "Qual serviço você procura?"
```

---

### Causa Raiz

```python
# main.py (ANTES)

async def send_message_in_parts(to_number: str, message: str):
    parts = message.split('\n')

    # Agrupava até 3 linhas ou 200 chars
    grouped_parts = []
    current_group = []
    current_length = 0

    for part in parts:
        if len(current_group) < 3 and current_length + len(part) < 200:
            current_group.append(part)
            current_length += len(part)
        else:
            grouped_parts.append('\n'.join(current_group))
            current_group = [part]
            current_length = len(part)

    # Enviar grupos
    for group in grouped_parts:
        await whatsapp_client.send_text(to_number, group)
        await asyncio.sleep(3)
```

**Problema:** Lógica de agrupamento muito agressiva.

---

### Solução

```python
# main.py (DEPOIS)

async def send_message_in_parts(to_number: str, message: str):
    # Dividir por quebras de linha duplas (parágrafos)
    parts = re.split(r'\n\s*\n', message.strip())

    # Se não houver quebras duplas, dividir por linha simples
    if len(parts) == 1:
        parts = message.split('\n')

    # Filtrar partes vazias
    final_parts = []
    for part in parts:
        part = part.strip()
        if part:
            # Se parte muito longa (>200 chars), dividir por frases
            if len(part) > 200:
                sentences = re.split(r'([.!?])\s+', part)
                current = ""
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    punct = sentences[i+1] if i+1 < len(sentences) else ""

                    if len(current) + len(sentence) > 200 and current:
                        final_parts.append(current.strip())
                        current = sentence + punct + " "
                    else:
                        current += sentence + punct + " "

                if current.strip():
                    final_parts.append(current.strip())
            else:
                final_parts.append(part)

    # Enviar cada parte INDIVIDUALMENTE com delay
    for i, part in enumerate(final_parts):
        await whatsapp_client.send_text(to_number, part)
        logger.info(f"  📤 Mensagem {i+1}/{len(final_parts)} enviada ({len(part)} chars)")

        # Delay entre mensagens (3-6 segundos)
        if i < len(final_parts) - 1:
            delay = min(3 + (len(part) / 100), 6)
            logger.info(f"  ⏱️ Aguardando {delay:.1f}s antes da próxima...")
            await asyncio.sleep(delay)
```

**Mudanças:**
1. ✅ Removida lógica de agrupamento
2. ✅ Cada parágrafo = mensagem separada
3. ✅ Delay proporcional ao tamanho (3-6 segundos)
4. ✅ Partes >200 chars divididas por frases

---

### Arquivo Modificado

- `main.py` (linhas 153-203)

### Restart Necessário

```bash
docker compose restart bot
```

---

### Impacto

**Antes:** Mensagens longas e robóticas
**Depois:** Mensagens curtas e naturais (parece humano)

---

## 🔵 BUG #3: Tabela "customer_info" Não Existe

### Data
Durante desenvolvimento (corrigido antes de deploy)

### Severidade
**BAIXA** 🔵

### Descrição

Script de limpeza tentava deletar de tabela inexistente.

**Erro:**
```sql
ERROR:  relation "customer_info" does not exist
```

---

### Causa Raiz

```sql
-- Script de limpeza (ANTES)
TRUNCATE TABLE customer_info CASCADE;
```

**Problema:** Tabela real é `customer_context`, não `customer_info`.

---

### Solução

```sql
-- Script de limpeza (DEPOIS)
TRUNCATE TABLE customer_context CASCADE;
```

---

### Impacto

**Antes:** Erro ao executar limpeza
**Depois:** Limpeza funciona perfeitamente

---

## 🟢 BUG #4: Buffer Não Resetava Timer

### Data
Durante testes iniciais (corrigido antes de deploy)

### Severidade
**MÉDIA** 🟡

### Descrição

Quando usuário enviava múltiplas mensagens, buffer acumulava mas não resetava o timer.

**Problema:**
```
09:00:00 - Mensagem 1 → Timer de 13s inicia
09:00:05 - Mensagem 2 → Timer NÃO resetava
09:00:13 - Processava só Mensagem 1 ❌
```

---

### Causa Raiz

```python
# main.py (ANTES)

async def add_to_buffer_and_schedule(from_number, message_text, payload):
    # Adiciona mensagem
    message_buffers[from_number]["messages"].append(message_text)

    # Agenda processamento
    task = asyncio.create_task(process_buffered_messages(from_number))
    message_buffers[from_number]["task"] = task
    # ❌ Não cancelava task anterior!
```

---

### Solução

```python
# main.py (DEPOIS)

async def add_to_buffer_and_schedule(from_number, message_text, payload):
    # Adiciona mensagem
    message_buffers[from_number]["messages"].append(message_text)

    # ✅ Cancelar timer anterior se existir
    if message_buffers[from_number]["task"]:
        message_buffers[from_number]["task"].cancel()
        logger.info(f"⏱️ Timer anterior cancelado para {from_number}")

    # Agendar novo processamento
    task = asyncio.create_task(process_buffered_messages(from_number))
    message_buffers[from_number]["task"] = task
    logger.info(f"⏳ Novo timer de {BUFFER_TIMEOUT}s iniciado")
```

---

### Impacto

**Antes:** Mensagens fracionadas não eram todas capturadas
**Depois:** Buffer espera corretamente até última mensagem

---

## 📊 Resumo de Bugs

| ID | Severidade | Status | Descrição | Arquivo |
|----|-----------|--------|-----------|---------|
| #1 | 🔴 CRÍTICA | ✅ Corrigido | Formato @lid não suportado | server.js |
| #2 | 🟡 MÉDIA | ✅ Corrigido | Mensagens agrupadas demais | main.py |
| #3 | 🔵 BAIXA | ✅ Corrigido | Tabela customer_info não existe | SQL |
| #4 | 🟡 MÉDIA | ✅ Corrigido | Buffer não resetava timer | main.py |

**Total:** 4 bugs encontrados, **4 corrigidos** (100%)

---

## ✅ Checklist de Correções

- [x] Bug #1: @lid suportado
- [x] Bug #2: Micro mensagens implementadas
- [x] Bug #3: Tabela correta usada
- [x] Bug #4: Buffer reseta timer corretamente
- [x] Todos os testes passando
- [x] Sistema 100% funcional

---

## 🔍 Como Reportar Novos Bugs

### Template de Bug Report

```markdown
## Descrição
[Descrever o problema]

## Sintomas
- O que acontece?
- Quando acontece?
- Com quais números/mensagens?

## Logs
```
[Colar logs relevantes]
```

## Reprodução
1. Passo 1
2. Passo 2
3. Passo 3

## Esperado
[O que deveria acontecer]

## Obtido
[O que realmente aconteceu]
```

---

## 📚 Próximos Passos

**[09-TROUBLESHOOTING.md](./09-TROUBLESHOOTING.md)** → Solução de problemas comuns

---

**Status:** ✅ Todos os bugs documentados e corrigidos
