#!/usr/bin/env python3
"""Script para atualizar o prompt do agente com o prompt integrado"""

# Ler o prompt integrado
with open('gabi_prompt_integrated.md', 'r', encoding='utf-8') as f:
    new_prompt = f.read()

# Template do arquivo do agente
agent_code = '''from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.postgres import PostgresDb
from dotenv import load_dotenv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.faq_tools import SPDropFAQTools
from tools.memory_tools import SPDropMemoryTools
from tools.conversation_scripts_tools import ConversationScriptsTools

load_dotenv()

# STORAGE: Configurar PostgreSQL como banco de dados para armazenamento
database_url = os.getenv("DATABASE_URL", "postgresql://spdrop_user:spdrop_password@postgres:5432/spdrop_db")
postgres_db = PostgresDb(
    db_url=database_url
)

support_agent = Agent(
    name="Gabi - Especialista em Vendas Consultivas SPDrop",
    model=OpenAIChat(id="gpt-4.1-mini"),
    description="Especialista em vendas consultivas e transformação digital - SPDrop",
    tools=[SPDropFAQTools(), SPDropMemoryTools(), ConversationScriptsTools()],

    # STORAGE: Usar PostgreSQL como storage persistente
    db=postgres_db,

    # MEMORY: Ativar memória de contexto
    add_history_to_context=True,
    instructions="""PROMPT_PLACEHOLDER""",
    markdown=True,
)

if __name__ == "__main__":
    support_agent.print_response(
        "Oi Gabi, queria saber mais sobre os planos da SPDrop",
        stream=True
    )
'''

# Substituir o placeholder pelo prompt real
agent_code = agent_code.replace("PROMPT_PLACEHOLDER", new_prompt)

# Salvar o arquivo atualizado
with open('agentes/agente_suporte.py', 'w', encoding='utf-8') as f:
    f.write(agent_code)

print("✓ Arquivo agente_suporte.py atualizado com sucesso!")
print(f"✓ Prompt tem {len(new_prompt)} caracteres")
print(f"✓ Arquivo final tem {len(agent_code)} caracteres")
