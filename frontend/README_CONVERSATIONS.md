# 💬 Conversas - Layout Tipo WhatsApp

## 🎯 NOVO FORMATO: Histórico Completo por Cliente

A página de conversas agora mostra o histórico **completo** de cada cliente em **blocos únicos**, exatamente como no WhatsApp!

---

## 🆕 O QUE MUDOU?

### ❌ ANTES:
```
Cada linha = 1 pergunta + 1 resposta
- Difícil ver o contexto completo
- Conversas fragmentadas
- Não parecia natural
```

### ✅ AGORA:
```
Cada bloco = TODO histórico do cliente
- Conversas agrupadas por cliente
- Layout tipo WhatsApp com bolhas
- Histórico completo em um único lugar
- Expandir/Recolher cada cliente
```

---

## 📊 NOVO LAYOUT:

### 1️⃣ **Cabeçalho do Cliente** (Sempre visível)

```
┌─────────────────────────────────────────────────┐
│ 👤 Paulo Henrique                    ⌄         │
│    5511999999999                               │
│                                                 │
│    7 mensagens                                 │
│    19/11/25 às 17:25                          │
└─────────────────────────────────────────────────┘
```

**Informações:**
- Avatar do cliente
- Nome completo
- Telefone
- Quantidade total de mensagens
- Data/hora da última mensagem
- Ícone para expandir/recolher

---

### 2️⃣ **Chat Completo** (Quando expandido)

```
┌─────────────────────────────────────────────────┐
│ 👤 Paulo Henrique                    ⌃         │
│    5511999999999                               │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌─────────────────────────────────┐            │
│ │ 👤 Paulo Henrique               │            │
│ │ Olá, quero saber mais sobre...  │            │
│ │ 17:00                            │            │
│ └─────────────────────────────────┘            │
│                                                 │
│           ┌─────────────────────────────────┐  │
│           │ 🤖 Gabi (Bot)                   │  │
│           │ Olá Paulo Henrique! A SPDrop... │  │
│           │ 17:00                            │  │
│           └─────────────────────────────────┘  │
│                                                 │
│ ┌─────────────────────────────────┐            │
│ │ 👤 Paulo Henrique               │            │
│ │ Quanto custa para começar?      │            │
│ │ 17:02                            │            │
│ └─────────────────────────────────┘            │
│                                                 │
│           ┌─────────────────────────────────┐  │
│           │ 🤖 Gabi (Bot)                   │  │
│           │ Temos 3 planos em promoção...   │  │
│           │ 17:02                            │  │
│           └─────────────────────────────────┘  │
│                                                 │
│ ... (mais mensagens)                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🎨 CORES DAS BOLHAS:

### Mensagem do Cliente (Esquerda)
```css
Cor de fundo: Cinza claro (#F3F4F6)
Cor do texto: Preto (#111827)
Alinhamento: Esquerda
Largura máxima: 75% da tela
```

### Resposta do Bot (Direita)
```css
Cor de fundo: Azul primário (#0EA5E9)
Cor do texto: Branco (#FFFFFF)
Alinhamento: Direita
Largura máxima: 75% da tela
```

---

## ⚙️ FUNCIONALIDADES:

### ✅ **Expandir/Recolher**
- Clique no cabeçalho do cliente
- Alterna entre mostrar/ocultar o chat completo
- Primeiro cliente auto-expandido

### ✅ **Preview quando Recolhido**
```
Última mensagem: "Obrigado! Como faço para acessar?"
```

### ✅ **Auto-refresh**
- Atualiza a cada 15 segundos
- Novas mensagens aparecem automaticamente

### ✅ **Busca**
- Busca por nome do cliente
- Busca por telefone
- Busca por conteúdo das mensagens

### ✅ **Scroll Infinito**
```
Altura máxima do chat: 600px
Scroll automático para ver todas as mensagens
```

---

## 🔌 NOVO ENDPOINT DA API:

### **GET** `/api/conversations/grouped`

#### Parâmetros:
```
limit: Quantidade de clientes (default: 20, max: 100)
```

#### Headers:
```
Authorization: Bearer <JWT_TOKEN>
```

#### Resposta:
```json
{
  "count": 2,
  "conversations": [
    {
      "customer": {
        "id": 1,
        "name": "Paulo Henrique",
        "phone": "5511999999999",
        "email": "paulo@exemplo.com"
      },
      "message_count": 7,
      "last_message_time": "2025-11-19T17:25:28",
      "messages": [
        {
          "id": "12_user",
          "sender": "user",
          "text": "Olá, quero saber mais...",
          "timestamp": "2025-11-19T17:00:28"
        },
        {
          "id": "12_agent",
          "sender": "agent",
          "text": "Olá Paulo Henrique! A SPDrop...",
          "timestamp": "2025-11-19T17:00:28"
        }
        // ... mais mensagens
      ]
    }
  ]
}
```

---

## 🗄️ ESTRUTURA NO BANCO:

### Como funciona o agrupamento:

1. **Busca clientes com conversas**
```sql
SELECT DISTINCT c.id, c.name, c.phone, c.email,
       MAX(ch.timestamp) as last_message_time,
       COUNT(ch.id) as message_count
FROM customers c
INNER JOIN conversation_history ch ON c.id = ch.customer_id
GROUP BY c.id
ORDER BY last_message_time DESC
```

2. **Para cada cliente, busca TODAS as mensagens**
```sql
SELECT id, user_message, agent_response, timestamp
FROM conversation_history
WHERE customer_id = X
ORDER BY timestamp ASC  -- Ordem cronológica!
```

3. **Transforma em formato de chat**
```javascript
// Cada linha vira 2 mensagens:
{user_message} → { sender: 'user', text: '...', timestamp: '...' }
{agent_response} → { sender: 'agent', text: '...', timestamp: '...' }
```

---

## 💡 EXEMPLO PRÁTICO:

### Banco de dados tem:
```
conversation_history:
ID | user_message          | agent_response              | timestamp
1  | "Olá"                 | "Olá Paulo! Como vai?"      | 17:00
2  | "Quero saber preços"  | "Temos 3 planos..."        | 17:02
```

### Frontend mostra:
```
┌─────────────────────────┐
│ 👤 Paulo                │
│ Olá                     │
│ 17:00                   │
└─────────────────────────┘

        ┌─────────────────────────┐
        │ 🤖 Gabi                 │
        │ Olá Paulo! Como vai?    │
        │ 17:00                   │
        └─────────────────────────┘

┌─────────────────────────┐
│ 👤 Paulo                │
│ Quero saber preços      │
│ 17:02                   │
└─────────────────────────┘

        ┌─────────────────────────┐
        │ 🤖 Gabi                 │
        │ Temos 3 planos...       │
        │ 17:02                   │
        └─────────────────────────┘
```

---

## 🚀 COMO TESTAR:

### 1. Acessar a página:
```
http://localhost:3002/conversations
```

### 2. Ver Paulo Henrique:
- Deve aparecer o card dele
- Clique para expandir
- Veja o histórico completo de 7 mensagens

### 3. Buscar:
```
Digite "plataforma" → Filtra conversas que falam de plataforma
Digite "Paulo" → Mostra só conversas do Paulo
Digite "5511" → Busca por telefone
```

---

## 🎯 BENEFÍCIOS:

### ✅ **Contexto Completo**
Ver toda a jornada do cliente em um único lugar

### ✅ **Visual Familiar**
Layout igual ao WhatsApp que todos conhecem

### ✅ **Fácil Navegação**
Expandir/recolher para ver detalhes

### ✅ **Performance**
Carrega até 100 clientes de uma vez

### ✅ **Busca Poderosa**
Encontra qualquer conversa rapidamente

---

## 📱 RESPONSIVO:

### Desktop:
- Bolhas com 75% de largura máxima
- Scroll vertical para mensagens longas

### Mobile:
- Bolhas se adaptam automaticamente
- Touch para expandir/recolher
- Scroll otimizado

---

## 🔧 PERSONALIZAÇÃO:

### Mudar cores das bolhas:

Edite `/frontend/src/pages/Conversations.jsx`:

```javascript
// Linha 145-149
className={`max-w-[75%] rounded-lg px-4 py-3 ${
  message.sender === 'user'
    ? 'bg-gray-100 text-gray-900'      // ← CLIENTE
    : 'bg-primary-500 text-white'      // ← BOT
}`}
```

### Mudar altura máxima do chat:

```javascript
// Linha 138
<div className="... max-h-[600px] ...">  // ← ALTURA
```

---

## 🐛 TROUBLESHOOTING:

### Conversas não aparecem?
1. Verificar se há dados no banco
2. Fazer logout/login
3. Limpar cache (Ctrl+Shift+R)

### Não expande ao clicar?
1. Verificar console do navegador (F12)
2. Verificar se JavaScript está habilitado

### Busca não funciona?
1. Verificar se digitou corretamente
2. Busca é case-insensitive

---

## 📊 MÉTRICAS:

- **Clientes mostrados**: Até 100
- **Auto-refresh**: 15 segundos
- **Primeira visualização**: Auto-expandido
- **Mensagens por cliente**: Ilimitadas

---

## ✨ RESUMO:

**Agora as conversas são mostradas EXATAMENTE como no WhatsApp:**

✅ Um bloco por cliente
✅ Histórico completo visível
✅ Bolhas coloridas alternadas
✅ Expandir/Recolher
✅ Preview da última mensagem
✅ Busca em tempo real
✅ Auto-refresh a cada 15s

**Acesse http://localhost:3002/conversations e veja!**
