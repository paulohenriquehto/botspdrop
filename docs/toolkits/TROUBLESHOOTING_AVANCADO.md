# 🔧 Troubleshooting Avançado de Toolkits

Este guia cobre problemas específicos e suas soluções detalhadas.

## Índice

1. [Problema: Agente não chama as ferramentas](#problema-1-agente-não-chama-as-ferramentas)
2. [Problema: Ferramentas retornam erro](#problema-2-ferramentas-retornam-erro)
3. [Problema: Agente chama ferramenta errada](#problema-3-agente-chama-ferramenta-errada)
4. [Problema: Performance lenta](#problema-4-performance-lenta)
5. [Problema: Erro ao inicializar toolkit](#problema-5-erro-ao-inicializar-toolkit)

---

## Problema 1: Agente não chama as ferramentas

### Sintomas
- Agente responde sem buscar informações
- Logs não mostram chamadas de ferramentas
- Sempre dá respostas genéricas

### Diagnóstico Passo a Passo

#### Passo 1: Verificar se toolkit está registrado corretamente

```python
# ❌ ERRADO
class MeuToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="meu_toolkit")  # ❌ Sem tools
        self.register(self.ferramenta)  # ❌ Tarde demais

# ✅ CORRETO
class MeuToolkit(Toolkit):
    def __init__(self):
        tools = [self.ferramenta]  # ✅ Lista primeiro
        super().__init__(name="meu_toolkit", tools=tools)  # ✅ Passa tools
```

#### Passo 2: Verificar se agente recebe toolkit

```python
# ❌ ERRADO - Passa a classe
agent = Agent(
    tools=[MeuToolkit]  # ❌ Falta ()
)

# ✅ CORRETO - Passa a instância
agent = Agent(
    tools=[MeuToolkit()]  # ✅ Com ()
)
```

#### Passo 3: Testar toolkit isoladamente

Crie um script de teste:

```python
#!/usr/bin/env python3
"""
Teste isolado do toolkit
"""
from tools.meu_toolkit import MeuToolkit

# Instanciar
toolkit = MeuToolkit()

# Verificar se ferramentas foram registradas
print("=" * 70)
print("FERRAMENTAS DISPONÍVEIS:")
print("=" * 70)

if hasattr(toolkit, 'functions'):
    for func in toolkit.functions:
        print(f"✓ {func.__name__}")
        print(f"  Docstring: {func.__doc__[:100]}...")
        print()
else:
    print("❌ Nenhuma ferramenta encontrada!")

# Testar uma ferramenta
print("=" * 70)
print("TESTE DE EXECUÇÃO:")
print("=" * 70)

try:
    result = toolkit.minha_ferramenta(parametro="teste")
    print(f"✓ Resultado: {result}")
except Exception as e:
    print(f"❌ Erro: {e}")
```

Execute:
```bash
python3 teste_toolkit_isolado.py
```

#### Passo 4: Verificar logs do agente

Adicione logging no main.py:

```python
import logging

# Configurar logging verbose
logging.basicConfig(
    level=logging.DEBUG,  # ← DEBUG ao invés de INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Antes de chamar o agente
logger.info(f"Ferramentas disponíveis: {[type(t).__name__ for t in support_agent.tools]}")
```

Você deve ver:
```
INFO - Ferramentas disponíveis: ['MeuToolkit', 'OutroToolkit']
```

#### Passo 5: Verificar múltiplas chamadas à API OpenAI

Quando ferramentas são usadas, você verá 2+ chamadas:

```bash
docker compose logs bot | grep "HTTP.*openai"
```

Saída esperada:
```
INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "200 OK"  # 1ª chamada (tool calls)
INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "200 OK"  # 2ª chamada (resposta)
```

Se houver **apenas 1 chamada**, o agente não está usando ferramentas.

### Soluções

#### Solução 1: Corrigir registro do toolkit

Aplique o padrão correto documentado em `README.md`.

#### Solução 2: Melhorar docstrings

```python
def minha_ferramenta(self, parametro: str) -> Dict[str, Any]:
    """
    🚨 USE ESTA FERRAMENTA quando o usuário perguntar sobre X.

    IMPORTANTE: SEMPRE chame esta ferramenta ANTES de responder.

    Esta ferramenta retorna informações críticas sobre Y.

    Args:
        parametro: O que buscar

    Returns:
        Dict com os dados encontrados
    """
```

Palavras-chave que ajudam:
- **RETRIEVE** (recuperar)
- **GET** (obter)
- **FETCH** (buscar)
- **SEARCH** (procurar)
- **ALWAYS** (sempre)
- **IMPORTANT** (importante)
- **REQUIRED** (obrigatório)

#### Solução 3: Reforçar instruções do agente

```python
agent = Agent(
    instructions="""
    # PROTOCOLO OBRIGATÓRIO DE FERRAMENTAS

    🚨 VOCÊ DEVE USAR FERRAMENTAS EM TODA RESPOSTA!

    NUNCA responda sem consultar as ferramentas primeiro.

    ## Ordem de execução:

    1. PASSO 1: SEMPRE chame get_conversation_history(customer_id)
    2. PASSO 2: SEMPRE chame get_important_memories(customer_id)
    3. PASSO 3: Use outras ferramentas conforme necessário
    4. PASSO 4: Responda baseado nos dados obtidos

    Se você não seguir este protocolo, você estará falhando na sua missão.
    """
)
```

#### Solução 4: Usar modelo mais avançado

GPT-4o-mini pode ser inconsistente. Se possível, teste com:

```python
model=OpenAIChat(id="gpt-4o")  # Mais confiável com tool calling
```

---

## Problema 2: Ferramentas retornam erro

### Sintomas
- Tool retorna `{"error": "..."}`
- Tool retorna `None` ou lista vazia
- Agente diz "não consegui obter as informações"

### Diagnóstico

#### Verificar conexão com recursos externos

```python
def _get_connection(self):
    """Método de conexão com debug"""
    try:
        conn = psycopg2.connect(**self.conn_params)
        print("✅ Conexão com banco OK")
        return conn
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print(f"   Params: {self.conn_params}")
        return None
```

#### Testar ferramenta com dados reais

```python
# Script de teste
toolkit = MeuToolkit()

print("Testando ferramenta...")
result = toolkit.buscar_dados(id=17)

if result:
    print(f"✅ Sucesso: {result}")
else:
    print("❌ Falha: resultado vazio")
```

### Soluções

#### Solução 1: Adicionar tratamento de erros robusto

```python
def minha_ferramenta(self, id: int) -> Dict[str, Any]:
    """Ferramenta com tratamento de erros"""

    # Validar entrada
    if not id or id <= 0:
        return {
            "success": False,
            "error": "invalid_id",
            "message": "ID deve ser um número positivo"
        }

    conn = self._get_connection()
    if not conn:
        return {
            "success": False,
            "error": "connection_failed",
            "message": "Falha ao conectar ao banco de dados"
        }

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM tabela WHERE id = %s", (id,))
            result = cur.fetchone()

            if not result:
                return {
                    "success": False,
                    "error": "not_found",
                    "message": f"Nenhum registro encontrado para ID {id}"
                }

            return {
                "success": True,
                "data": dict(result)
            }

    except psycopg2.Error as e:
        return {
            "success": False,
            "error": "database_error",
            "message": f"Erro no banco: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": "unknown_error",
            "message": f"Erro inesperado: {str(e)}"
        }

    finally:
        if conn:
            conn.close()
```

#### Solução 2: Logging detalhado

```python
import logging

logger = logging.getLogger(__name__)

def minha_ferramenta(self, id: int) -> Dict[str, Any]:
    logger.info(f"Executando minha_ferramenta com id={id}")

    conn = self._get_connection()
    if not conn:
        logger.error("Falha na conexão")
        return {"error": "connection_failed"}

    try:
        logger.debug("Executando query...")
        # ... código ...
        logger.info("Query executada com sucesso")
        return result

    except Exception as e:
        logger.exception(f"Erro ao executar ferramenta: {e}")
        return {"error": str(e)}
```

#### Solução 3: Fallback values

```python
def get_customer_name(self, id: int) -> str:
    """Retorna nome do cliente com fallback"""
    try:
        result = self._query_database(id)
        return result.get('name', 'Cliente')  # Fallback: 'Cliente'
    except:
        return 'Cliente'  # Fallback em caso de erro
```

---

## Problema 3: Agente chama ferramenta errada

### Sintomas
- Agente usa `buscar_faq` quando deveria usar `buscar_produto`
- Chama ferramentas em ordem errada
- Pula ferramentas obrigatórias

### Soluções

#### Solução 1: Nomes mais descritivos

```python
# ❌ Nome ambíguo
def get_data(self, id: int):
    """Get data"""

# ✅ Nome específico
def get_customer_conversation_history(self, customer_id: int):
    """GET the complete conversation history for a specific customer"""
```

#### Solução 2: Docstrings com casos de uso

```python
def buscar_produto(self, query: str) -> Dict:
    """
    SEARCH for products in the catalog.

    🎯 USE THIS TOOL when:
    - Customer asks "quanto custa X?"
    - Customer wants to know about products
    - Customer says "quero comprar"
    - Customer asks "o que vocês vendem?"

    ❌ DO NOT use this for:
    - FAQ questions (use buscar_faq instead)
    - Customer support issues (use buscar_suporte instead)

    Args:
        query: Product name or description to search for

    Returns:
        List of matching products with price and details
    """
```

#### Solução 3: Instruções explícitas no agente

```python
instructions="""
# GUIA DE USO DE FERRAMENTAS

## Quando o cliente pergunta sobre PREÇOS ou PRODUTOS:
→ Use: buscar_produto(query)

## Quando o cliente tem DÚVIDA TÉCNICA:
→ Use: buscar_faq(pergunta)

## Quando o cliente quer HISTÓRICO:
→ Use: get_conversation_history(customer_id)

## Quando o cliente menciona PAGAMENTO:
→ Use: create_payment_link(...)
"""
```

---

## Problema 4: Performance Lenta

### Sintomas
- Resposta demora mais de 10 segundos
- Timeout em ferramentas
- Usuário reclama de lentidão

### Diagnóstico

Adicione medição de tempo:

```python
import time

def minha_ferramenta(self, param: str) -> Dict:
    start_time = time.time()

    # ... código ...

    elapsed = time.time() - start_time
    print(f"⏱️ minha_ferramenta levou {elapsed:.2f}s")

    return result
```

### Soluções

#### Solução 1: Limitar resultados

```python
def get_history(self, customer_id: int, limit: int = 10):  # ← Limit padrão
    """Busca histórico limitado"""
    cur.execute("""
        SELECT * FROM history
        WHERE customer_id = %s
        ORDER BY timestamp DESC
        LIMIT %s  -- ← Limita no banco
    """, (customer_id, limit))
```

#### Solução 2: Usar índices no banco

```sql
-- Adicionar índices para queries rápidas
CREATE INDEX idx_customer_id ON conversation_history(customer_id);
CREATE INDEX idx_timestamp ON conversation_history(timestamp DESC);
```

#### Solução 3: Cache em memória

```python
from functools import lru_cache

class MeuToolkit(Toolkit):
    @lru_cache(maxsize=100)
    def get_static_data(self, id: int):
        """Dados que não mudam frequentemente"""
        # Resultado fica em cache
        return self._query_database(id)
```

#### Solução 4: Timeout em requests

```python
def call_api(self, param: str):
    response = requests.get(
        url,
        timeout=5  # ← Timeout de 5 segundos
    )
```

---

## Problema 5: Erro ao inicializar toolkit

### Erro: `TypeError: Agent.__init__() got an unexpected keyword argument`

```python
# ❌ ERRADO - Parâmetro inválido
agent = Agent(
    show_tool_calls=True  # ← NÃO EXISTE
)
```

**Solução:** Remover parâmetros inválidos.

### Erro: `AttributeError: 'MeuToolkit' object has no attribute 'functions'`

**Causa:** Toolkit não foi inicializado corretamente.

**Solução:** Verificar se `super().__init__()` foi chamado com `tools=`.

### Erro: `Module not found`

```
ImportError: cannot import name 'MeuToolkit' from 'tools.meu_toolkit'
```

**Soluções:**
1. Verificar caminho do arquivo
2. Verificar nome da classe
3. Adicionar `__init__.py` na pasta tools

```python
# tools/__init__.py
from .meu_toolkit import MeuToolkit
from .outro_toolkit import OutroToolkit

__all__ = ['MeuToolkit', 'OutroToolkit']
```

---

## Checklist de Debug

Use este checklist quando tiver problemas:

```
□ Toolkit herda de Toolkit?
□ Tools registrados com super().__init__(name="...", tools=[...])?
□ Docstrings claras em todas as ferramentas?
□ Agente recebe toolkit como instância ([Toolkit()])?
□ Sem parâmetros inválidos no agente?
□ Testei toolkit isoladamente?
□ Logs mostram 2+ chamadas à API OpenAI?
□ Tratamento de erros em todas as ferramentas?
□ Timeouts configurados em operações externas?
□ Queries limitadas (LIMIT clause)?
```

---

**Para mais ajuda, consulte:**
- `README.md` - Guia principal
- `EXEMPLOS_COMPLETOS.md` - Exemplos práticos
- [Documentação Oficial Agno](https://docs.agno.com)
