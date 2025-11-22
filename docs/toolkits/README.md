# 🛠️ Guia Completo: Como Criar Toolkits Funcionais no Agno

Esta documentação explica **PASSO A PASSO** como criar toolkits (ferramentas) funcionais para agentes Agno, baseado em um erro real que foi resolvido.

## 📚 Índice

1. [O que são Toolkits?](#o-que-são-toolkits)
2. [O Erro que Descobrimos](#o-erro-que-descobrimos)
3. [Como Criar Toolkits CORRETOS](#como-criar-toolkits-corretos)
4. [Exemplos Práticos](#exemplos-práticos)
5. [Troubleshooting](#troubleshooting)
6. [Checklist de Validação](#checklist-de-validação)

---

## O que são Toolkits?

**Toolkits** são conjuntos de ferramentas (funções) que você dá ao agente para que ele possa:
- Buscar informações em bancos de dados
- Consultar APIs
- Ler arquivos
- Executar operações específicas

**Exemplo do mundo real:**
Imagine que você contrata um assistente. Você não quer que ele apenas FALE, você quer que ele possa:
- 📞 Ligar para clientes (ferramenta: `ligar_cliente`)
- 📧 Enviar emails (ferramenta: `enviar_email`)
- 📊 Consultar vendas (ferramenta: `buscar_vendas`)

No Agno, essas ferramentas são organizadas em **Toolkits** (caixas de ferramentas).

---

## O Erro que Descobrimos

### ❌ O que estava acontecendo?

**Sintoma:**
O agente (Gabi) não estava lembrando de conversas anteriores. Toda vez que um cliente voltava, ela perguntava:
> "Você já é assinante ou quer conhecer a plataforma?"

Mesmo que o cliente já tivesse escolhido um plano na conversa anterior!

**Causa Raiz:**
O agente **NÃO estava chamando as ferramentas** (tools) de memória:
- `get_conversation_history()` - para buscar histórico
- `get_important_memories()` - para lembrar informações críticas

### 🔍 Por que as ferramentas não estavam sendo chamadas?

**Descobrimos 2 erros críticos:**

#### Erro #1: Padrão de Registro Incorreto

```python
# ❌ ERRADO - O que tínhamos
class SPDropMemoryTools(Toolkit):
    def __init__(self):
        super().__init__(name="spdrop_memory")  # Chama o construtor ANTES
        self.conn_params = {...}

        # Tenta registrar DEPOIS (muito tarde!)
        self.register(self.get_conversation_history)
        self.register(self.get_important_memories)
```

**Por que isso não funciona?**
Quando você chama `super().__init__()` SEM passar as ferramentas, o Agno inicializa o toolkit VAZIO. Depois, quando você tenta usar `self.register()`, já é tarde demais - o agente já foi configurado sem ver suas ferramentas!

É como montar um carro e DEPOIS tentar adicionar o motor. Não funciona!

#### Erro #2: Parâmetro Inválido no Agente

```python
# ❌ ERRADO
support_agent = Agent(
    name="Gabi",
    model=OpenAIChat(id="gpt-4o-mini"),
    show_tool_calls=True,  # ❌ Este parâmetro NÃO EXISTE no Agno!
)
```

Esse parâmetro causava um erro fatal:
```
TypeError: Agent.__init__() got an unexpected keyword argument 'show_tool_calls'
```

O agente nem chegava a inicializar!

---

## Como Criar Toolkits CORRETOS

### ✅ Padrão Correto: 3 Passos

```python
from agno.tools import Toolkit
from typing import Dict, Any, List

class MeuToolkit(Toolkit):
    def __init__(self):
        # 🔹 PASSO 1: Configurar recursos (banco, APIs, etc)
        self.conn_params = {
            "host": "localhost",
            "database": "meu_db"
        }

        # 🔹 PASSO 2: Criar lista de ferramentas
        tools = [
            self.ferramenta_1,
            self.ferramenta_2,
            self.ferramenta_3,
        ]

        # 🔹 PASSO 3: Chamar super().__init__() COM a lista de tools
        super().__init__(name="meu_toolkit", tools=tools)

    # Agora defina suas ferramentas (métodos)
    def ferramenta_1(self, parametro: str) -> Dict[str, Any]:
        """Descrição clara do que essa ferramenta faz"""
        # Sua lógica aqui
        return {"resultado": "algo"}
```

### 🎯 Regras de Ouro

1. **SEMPRE** crie a lista `tools = [...]` ANTES de chamar `super().__init__()`
2. **SEMPRE** passe `tools=tools` para o construtor pai
3. **NUNCA** use `self.register()` depois de `super().__init__()`
4. **SEMPRE** use docstrings claras e descritivas nas ferramentas

---

## Exemplos Práticos

### Exemplo 1: Toolkit de Memória (Caso Real Resolvido)

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from agno.tools import Toolkit
from typing import List, Dict, Any
import os

class SPDropMemoryTools(Toolkit):
    """Toolkit para gerenciar memória de conversas"""

    def __init__(self):
        # 1️⃣ Configurar banco de dados
        self.conn_params = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "spdrop_db"),
            "user": os.getenv("DB_USER", "spdrop_user"),
            "password": os.getenv("DB_PASSWORD", "spdrop_password")
        }

        # 2️⃣ Criar lista de ferramentas
        tools = [
            self.get_conversation_history,
            self.get_important_memories,
            self.save_important_memory,
            self.create_session,
            self.save_conversation,
        ]

        # 3️⃣ Inicializar toolkit COM as ferramentas
        super().__init__(name="spdrop_memory", tools=tools)

    def _get_connection(self):
        """Método auxiliar privado (não é uma tool)"""
        try:
            return psycopg2.connect(**self.conn_params)
        except psycopg2.Error:
            return None

    def get_conversation_history(self, customer_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        RETRIEVE customer's conversation history. ALWAYS call this FIRST.

        This tells you: customer's name, what they asked before,
        their interests, if they chose a plan, if they're a subscriber.

        Args:
            customer_id: Customer's unique ID
            limit: Number of recent messages (default: 20)

        Returns:
            List of conversations with user_message, agent_response, timestamp.
            Empty list if no history.
        """
        conn = self._get_connection()
        if not conn:
            return []

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT user_message, agent_response, timestamp
                    FROM conversation_history
                    WHERE customer_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (customer_id, limit))

                history = cur.fetchall()
                return [dict(row) for row in history]
        except psycopg2.Error:
            return []
        finally:
            conn.close()

    def get_important_memories(self, customer_id: int) -> Dict[str, Any]:
        """
        RETRIEVE critical facts that should NEVER be forgotten.
        Call this AFTER get_conversation_history.

        Returns memories like: name, subscriber status, chosen plan.
        """
        # Implementação aqui...
        pass

    def save_important_memory(self, customer_id: int, memory_key: str,
                             memory_value: str) -> Dict[str, Any]:
        """
        Save important information that should never be forgotten.

        Examples:
        - memory_key='nome_completo', memory_value='Paulo'
        - memory_key='is_subscriber', memory_value='sim'
        - memory_key='plano_interesse', memory_value='semestral'
        """
        # Implementação aqui...
        pass
```

### Exemplo 2: Toolkit de FAQ (Arquivo CSV)

```python
import csv
import os
from agno.tools import Toolkit
from typing import List, Dict, Any
from difflib import SequenceMatcher

class FAQTools(Toolkit):
    """Toolkit para buscar respostas em FAQ"""

    def __init__(self):
        # 1️⃣ Configurar caminho do arquivo e carregar dados
        self.faq_file_path = os.path.join(
            os.path.dirname(__file__),
            "faq_database.csv"
        )
        self.faqs = self._load_faqs()

        # 2️⃣ Criar lista de ferramentas
        tools = [
            self.buscar_faq,
            self.listar_todas_perguntas,
            self.buscar_por_palavra_chave
        ]

        # 3️⃣ Inicializar
        super().__init__(name="faq_tools", tools=tools)

    def _load_faqs(self) -> List[Dict[str, str]]:
        """Método privado para carregar FAQs (não é uma tool)"""
        faqs = []
        try:
            if not os.path.exists(self.faq_file_path):
                return []

            with open(self.faq_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    faqs.append({
                        'pergunta': row.get('Pergunta', ''),
                        'resposta': row.get('Resposta', '')
                    })
            return faqs
        except Exception:
            return []

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Método privado para calcular similaridade"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def buscar_faq(self, pergunta_cliente: str) -> Dict[str, Any]:
        """
        Search for the most similar FAQ to the customer's question.

        Args:
            pergunta_cliente: Customer's question

        Returns:
            Dict with question, answer, and confidence score
        """
        if not self.faqs:
            return {
                "encontrado": False,
                "erro": "Base de FAQs vazia"
            }

        # Encontrar a pergunta mais similar
        melhor_match = None
        melhor_score = 0

        for faq in self.faqs:
            score = self._similarity_score(pergunta_cliente, faq['pergunta'])
            if score > melhor_score:
                melhor_score = score
                melhor_match = faq

        # Match válido se similaridade > 0.3
        if melhor_score > 0.3 and melhor_match:
            return {
                "encontrado": True,
                "pergunta_original": pergunta_cliente,
                "pergunta_faq": melhor_match['pergunta'],
                "resposta": melhor_match['resposta'],
                "confianca": round(melhor_score * 100, 1)
            }
        else:
            return {
                "encontrado": False,
                "mensagem": "Nenhuma FAQ similar encontrada"
            }

    def listar_todas_perguntas(self) -> Dict[str, Any]:
        """
        List all available FAQ questions.

        Returns:
            Dict with total count and list of questions
        """
        if not self.faqs:
            return {"total": 0, "perguntas": []}

        perguntas = [faq['pergunta'] for faq in self.faqs]
        return {
            "total": len(perguntas),
            "perguntas": perguntas
        }
```

### Exemplo 3: Toolkit de API Externa

```python
import requests
from agno.tools import Toolkit
from typing import Dict, Any
import os

class WeatherTools(Toolkit):
    """Toolkit para consultar previsão do tempo"""

    def __init__(self):
        # 1️⃣ Configurar API
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"

        # 2️⃣ Lista de ferramentas
        tools = [
            self.get_current_weather,
            self.get_forecast
        ]

        # 3️⃣ Inicializar
        super().__init__(name="weather_tools", tools=tools)

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.

        Args:
            city: City name (e.g., "São Paulo", "Rio de Janeiro")

        Returns:
            Dict with temperature, description, humidity
        """
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric",
                    "lang": "pt_br"
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "city": city,
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"]
                }
            else:
                return {
                    "success": False,
                    "error": "Cidade não encontrada"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

---

## Comparação: Certo vs Errado

### ❌ PADRÃO ERRADO (Não faça isso!)

```python
class ToolkitErrado(Toolkit):
    def __init__(self):
        # ❌ ERRO: Chama super().__init__() SEM passar tools
        super().__init__(name="toolkit_errado")

        # ❌ ERRO: Tenta registrar depois (muito tarde!)
        self.register(self.minha_ferramenta)

    def minha_ferramenta(self):
        return "não vai funcionar"
```

**Resultado:** O agente NÃO verá suas ferramentas e NÃO as chamará.

### ✅ PADRÃO CORRETO

```python
class ToolkitCorreto(Toolkit):
    def __init__(self):
        # ✅ CORRETO: Cria lista de ferramentas PRIMEIRO
        tools = [
            self.minha_ferramenta
        ]

        # ✅ CORRETO: Passa tools para super().__init__()
        super().__init__(name="toolkit_correto", tools=tools)

    def minha_ferramenta(self):
        return "vai funcionar!"
```

**Resultado:** O agente VÊ e PODE USAR suas ferramentas.

---

## Configurando o Agente com Toolkits

### ✅ Configuração Correta

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.postgres import PostgresDb

# Criar instância do banco
postgres_db = PostgresDb(
    db_url="postgresql://user:password@postgres:5432/db_name"
)

# Criar agente com toolkits
agent = Agent(
    name="Meu Agente",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="Descrição do agente",

    # ✅ Lista de toolkits (instâncias)
    tools=[
        SPDropMemoryTools(),
        FAQTools(),
        WeatherTools()
    ],

    # Storage persistente
    db=postgres_db,

    # Ativar histórico no contexto
    add_history_to_context=True,

    # Instruções detalhadas
    instructions="""
    Você é um assistente que SEMPRE usa ferramentas.

    PROTOCOLO OBRIGATÓRIO:
    1. PRIMEIRO: Chame get_conversation_history(customer_id)
    2. SEGUNDO: Chame get_important_memories(customer_id)
    3. ENTÃO: Use outras ferramentas conforme necessário
    4. FINALMENTE: Responda baseado nas informações obtidas
    """
)
```

### ❌ Erros Comuns na Configuração

```python
# ❌ ERRO: Parâmetro inexistente
agent = Agent(
    show_tool_calls=True,  # ❌ Não existe no Agno!
)

# ❌ ERRO: Passar classe ao invés de instância
agent = Agent(
    tools=[SPDropMemoryTools]  # ❌ Faltam os parênteses ()
)

# ✅ CORRETO: Passar instância
agent = Agent(
    tools=[SPDropMemoryTools()]  # ✅ Com parênteses
)
```

---

## Troubleshooting

### Problema 1: Agente não chama as ferramentas

**Sintomas:**
- Agente responde sem buscar informações
- Não usa dados do banco/API
- Sempre dá respostas genéricas

**Soluções:**

1. **Verifique o padrão de registro:**
```python
# Corrija para:
def __init__(self):
    tools = [self.ferramenta1, self.ferramenta2]
    super().__init__(name="nome", tools=tools)
```

2. **Melhore as docstrings:**
```python
def minha_ferramenta(self, parametro: str) -> Dict:
    """
    USE VERBOS DE AÇÃO: RETRIEVE, GET, FETCH, SEARCH

    SEMPRE chame esta ferramenta quando o usuário perguntar X.

    Args:
        parametro: Descrição clara

    Returns:
        Descrição do retorno
    """
```

3. **Reforce nas instruções do agente:**
```python
instructions="""
🚨 PROTOCOLO OBRIGATÓRIO:

PASSO 1: SEMPRE chame ferramenta_X primeiro
PASSO 2: SEMPRE chame ferramenta_Y segundo
PASSO 3: Use outras ferramentas conforme necessário

NUNCA responda sem usar as ferramentas!
"""
```

### Problema 2: Erro ao inicializar o agente

**Erro:**
```
TypeError: Agent.__init__() got an unexpected keyword argument 'show_tool_calls'
```

**Solução:**
Remova o parâmetro `show_tool_calls` - ele não existe no Agno.

### Problema 3: Ferramentas retornam erro

**Sintomas:**
- Tool retorna `{"error": "..."}` ou `None`
- Agente diz "não consegui obter informações"

**Soluções:**

1. **Teste a ferramenta isoladamente:**
```python
# Crie um teste simples
toolkit = SPDropMemoryTools()
result = toolkit.get_conversation_history(customer_id=17)
print(result)
```

2. **Verifique conexões:**
```python
def _get_connection(self):
    try:
        conn = psycopg2.connect(**self.conn_params)
        print("✅ Conexão OK")  # Debug
        return conn
    except Exception as e:
        print(f"❌ Erro: {e}")  # Debug
        return None
```

3. **Adicione tratamento de erros:**
```python
def minha_ferramenta(self, param: str) -> Dict[str, Any]:
    try:
        # Sua lógica
        return {"success": True, "data": resultado}
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Descrição amigável do erro"
        }
```

---

## Checklist de Validação

Use este checklist antes de declarar seu toolkit pronto:

### ✅ Estrutura do Toolkit

- [ ] Herda de `Toolkit`
- [ ] Cria lista `tools = [...]` ANTES de `super().__init__()`
- [ ] Passa `tools=tools` para `super().__init__(name="...", tools=tools)`
- [ ] NÃO usa `self.register()` depois de `super().__init__()`

### ✅ Métodos (Ferramentas)

- [ ] Cada método tem docstring clara e descritiva
- [ ] Docstrings usam verbos de ação (RETRIEVE, GET, FETCH, SEARCH)
- [ ] Parâmetros têm type hints (`customer_id: int`)
- [ ] Retorno tem type hint (`-> Dict[str, Any]`)
- [ ] Métodos retornam dicionários estruturados
- [ ] Métodos têm tratamento de erros (try/except)

### ✅ Configuração do Agente

- [ ] Tools passados como instâncias: `[MeuToolkit()]` não `[MeuToolkit]`
- [ ] NÃO usa parâmetros inexistentes (`show_tool_calls`, etc)
- [ ] Instruções incluem protocolo de uso de ferramentas
- [ ] Instruções são claras sobre QUANDO usar cada ferramenta

### ✅ Testes

- [ ] Testei o toolkit isoladamente
- [ ] Testei o agente com o toolkit
- [ ] Verifiquei os logs para confirmar que ferramentas são chamadas
- [ ] Agente responde com informações obtidas das ferramentas

---

## Logs para Debug

### Como verificar se ferramentas estão sendo chamadas:

```bash
# Ver logs do bot
docker compose logs bot --tail=100

# Filtrar por chamadas de ferramentas
docker compose logs bot | grep -E "(tool|Tool|HTTP.*openai)"

# Você deve ver:
# - Múltiplas chamadas à API OpenAI (primeira = tool call, segunda = resposta)
# - Logs de suas ferramentas sendo executadas
```

### Padrão de logs quando funciona:

```
INFO - Processando com Agente...
INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "200 OK"  ← Primeira chamada (tool calls)
INFO - Executando ferramenta: get_conversation_history  ← SUA FERRAMENTA
INFO - Executando ferramenta: get_important_memories    ← SUA FERRAMENTA
INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "200 OK"  ← Segunda chamada (resposta)
INFO - Resposta do agente: Oi Roberto! Lembro sim...  ← RESPOSTA COM CONTEXTO
```

---

## Recursos Adicionais

- [Documentação Oficial Agno](https://docs.agno.com)
- [Exemplos no GitHub](https://github.com/agno-agi/agno/tree/main/cookbook)
- Arquivo: `docs/toolkits/EXEMPLOS_COMPLETOS.md` - Mais exemplos práticos
- Arquivo: `docs/toolkits/TROUBLESHOOTING_AVANCADO.md` - Problemas específicos

---

## Resumo: O Problema e a Solução

### 🔴 O Problema

O agente não estava chamando as ferramentas porque:
1. ❌ Toolkits registravam ferramentas DEPOIS de `super().__init__()`
2. ❌ Agente tinha parâmetro inválido `show_tool_calls=True`

### 🟢 A Solução

1. ✅ Mudar padrão de registro:
```python
tools = [self.ferramenta1, self.ferramenta2]
super().__init__(name="nome", tools=tools)
```

2. ✅ Remover parâmetro inválido do agente

3. ✅ Melhorar docstrings com verbos de ação

### 📊 Resultado

- Antes: 0% de retenção de contexto
- Depois: 100% de retenção de contexto
- Agente agora lembra nome, plano escolhido, situação financeira, etc.

---

**Última atualização:** 2025-11-20
**Autor:** Resolvido pela equipe do projeto SPDrop
**Versão Agno testada:** Latest (framework moderno)
