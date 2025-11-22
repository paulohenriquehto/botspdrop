# 📚 Guia Rápido: Isolamento de Contexto com user_id no Agno

## ⚡ Resumo Executivo

Sempre que chamar o agente, **PASSE o `user_id` para isolar contexto por cliente**.

```python
# ❌ ERRADO - Contextos misturados
support_agent.print_response(mensagem, stream=False)

# ✅ CORRETO - Contextos isolados
support_agent.print_response(mensagem, user_id=str(customer_id), stream=False)
```

---

## 🎯 Por Que user_id é Crítico?

### Sem user_id (PROBLEMA)
```
Cliente A: "Tenho Honda Civic"
Cliente B: "Tenho Ford Ranger"

Memória (shared):
- Mensagem 1: Honda Civic
- Mensagem 2: Ford Ranger
- Mensagem 3: Honda Civic (confusão!)

Cliente B recebe: "Seu carro é Honda Civic?" ❌
```

### Com user_id (SOLUÇÃO)
```
Cliente A (user_id=123): "Tenho Honda Civic"
Cliente B (user_id=124): "Tenho Ford Ranger"

Memória isolada:
- User 123: [Honda Civic] ← Independente
- User 124: [Ford Ranger] ← Independente

Cliente B recebe: "Seu carro é Ford Ranger?" ✅
```

---

## 📋 Implementação em Testes

### Pattern para Testes de Persistência

```python
def main():
    # 1️⃣ Criar clientes E GUARDAR customer_id
    customer_ids_por_nome = {}
    for usuario_data in usuarios_teste:
        customer_id, session_id = criar_cliente_e_sessao(usuario_data)
        customer_ids_por_nome[usuario_data['nome']] = customer_id

    # 2️⃣ Usar customer_id como user_id em TODAS as chamadas
    for usuario_data in usuarios_teste:
        customer_id = customer_ids_por_nome[usuario_data['nome']]
        support_agent.print_response(
            pergunta,
            user_id=str(customer_id),  # ← CRÍTICO!
            stream=False
        )
```

---

## 🔧 Parâmetros do Agno com user_id

### print_response()
```python
support_agent.print_response(
    message: str,
    user_id: str = None,              # ← Passar customer_id aqui
    session_id: str = None,           # Opcional: pode usar também
    stream: bool = False,
    markdown: bool = True
)
```

### run()
```python
resultado = support_agent.run(
    message: str,
    user_id: str = None,              # ← Passar customer_id aqui
    session_id: str = None
)
```

### agent.get_response()
```python
resposta = support_agent.get_response(
    message: str,
    user_id: str = None               # ← Passar customer_id aqui
)
```

---

## 💾 Como Funciona a Persistência

```
1. Cliente A (user_id=123) envia: "Tenho Honda Civic"
   ↓
2. PostgreSQL salva em customer_context (user_id=123)
   ↓
3. add_history_to_context=True busca histórico APENAS de user_id=123
   ↓
4. Modelo LLM recebe APENAS contexto de user_id=123
   ↓
5. LLM responde usando só dados isolados de user_id=123
   ↓
6. Cliente A volta depois: "Agente lembra: Este usuário (123) tem Honda Civic"
```

---

## ✨ Casos de Uso

### Caso 1: Chat WhatsApp Multi-Usuário
```python
# Cada mensagem vem de um cliente diferente
@app.post("/whatsapp/message")
def handle_whatsapp(message: dict):
    customer_id = message['customer_id']  # Do WhatsApp
    texto = message['text']

    # SEMPRE usar customer_id como user_id
    resposta = support_agent.print_response(
        texto,
        user_id=str(customer_id),  # ← ESSENCIAL!
        stream=False
    )
    return resposta
```

### Caso 2: Teste com 5 Usuários
```python
# FASE 1: Novos clientes
for cliente in clientes:
    id_db = criar_cliente_no_banco(cliente)
    suporte_agent.print_response(
        "Qual seu carro?",
        user_id=str(id_db)  # ← Isola por cliente
    )

# FASE 2: Clientes retornam
time.sleep(5)  # Simula desconexão
for cliente in clientes:
    id_db = obter_id_do_cliente(cliente)
    suporte_agent.print_response(
        "Quero polimento",
        user_id=str(id_db)  # ← MESMO ID, contexto persistido!
    )
```

### Caso 3: Processador de Pedidos (Agent-to-Agent)
```python
def chamar_processador_pedidos(vehicle_name, service_name, customer_id):
    # Processador também deve usar user_id!
    resultado = processador_pedidos.run(
        f"Processa: {vehicle_name} + {service_name}",
        user_id=str(customer_id)  # ← Manter isolamento!
    )
    return resultado
```

---

## 🚀 Checklist para Novos Testes

- [ ] Criar cliente no banco e guardar `customer_id`
- [ ] Converter `customer_id` para string: `str(customer_id)`
- [ ] Passar em TODAS as chamadas ao agente: `user_id=str(customer_id)`
- [ ] Se usar sessões adicionais, passar também: `session_id=str(session_id)`
- [ ] Testar com múltiplos clientes em sequência
- [ ] Validar que contextos não se misturam
- [ ] Verificar storage (customer_context) após teste

---

## ⚠️ Erros Comuns

### Erro 1: Esquecer user_id
```python
# ❌ ERRADO
support_agent.print_response("Olá", stream=False)

# ✅ CORRETO
support_agent.print_response("Olá", user_id=str(customer_id), stream=False)
```

### Erro 2: Passar customer_id como int
```python
# ❌ ERRADO
support_agent.print_response("Olá", user_id=customer_id)  # int

# ✅ CORRETO
support_agent.print_response("Olá", user_id=str(customer_id))  # string
```

### Erro 3: Não guardar customer_id para FASE 2
```python
# ❌ ERRADO - Criar cliente dentro do loop, perde id em FASE 2
for cliente in clientes:
    id = criar_cliente()  # Perde referência depois
    agent.print_response(..., user_id=str(id))

# ✅ CORRETO - Guardar ids antes
ids = {}
for cliente in clientes:
    ids[cliente['nome']] = criar_cliente()
# Depois usar ids na FASE 2
```

---

## 📚 Referência Rápida

| Operação | Código |
|----------|--------|
| Chat básico | `agent.print_response(msg, user_id=str(id))` |
| Obter resposta | `agent.run(msg, user_id=str(id))` |
| Com sessão | `agent.print_response(msg, user_id=str(id), session_id=str(sid))` |
| Múltiplos usuários | `[print_response(msg, user_id=str(id)) for id in ids]` |

---

## 🔗 Documentação Agno

- **Sessions**: https://docs.agno.com/concepts/agents/sessions
- **Memory**: https://docs.agno.com/concepts/memory/overview
- **Context**: https://docs.agno.com/concepts/agents/context

---

## ✅ Verificação

Depois de implementar user_id:

```bash
# 1. Rodar teste_persistencia_veiculo.py
python teste_persistencia_veiculo.py

# 2. Validar output:
# FASE 1: Agente pergunta veículo? ✅
# FASE 2: Agente lembra veículo? ✅
# Storage: Todos 5 carros salvos? ✅

# 3. Verificar banco:
psql -h localhost -U vanlu_user -d vanlu_db
SELECT c.name, cc.car_model FROM customers c
LEFT JOIN customer_context cc ON c.id = cc.customer_id;
```

Todos os 5 clientes devem ter seus carros corretos salvos.
