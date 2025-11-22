#!/usr/bin/env python3
"""
Teste Isolado da FAQ Tool
Testa a ferramenta diretamente sem passar pelo agente
"""

import sys
import os

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.faq_tools import SPDropFAQTools

def testar_faq():
    print("\n" + "="*80)
    print("🧪 TESTE ISOLADO DA FAQ TOOL")
    print("="*80)

    # Instanciar toolkit
    print("\n1️⃣ Instanciando SPDropFAQTools...")
    try:
        faq_tool = SPDropFAQTools()
        print("   ✅ Toolkit instanciado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao instanciar: {e}")
        return

    # Verificar se FAQs foram carregadas
    print(f"\n2️⃣ Verificando FAQs carregadas...")
    if hasattr(faq_tool, 'faqs'):
        total = len(faq_tool.faqs)
        print(f"   ✅ {total} FAQs carregadas")

        if total > 0:
            print(f"\n   📝 Primeira FAQ:")
            print(f"      Pergunta: {faq_tool.faqs[0].get('pergunta', 'N/A')[:80]}...")
            print(f"      Resposta: {faq_tool.faqs[0].get('resposta', 'N/A')[:80]}...")
        else:
            print(f"   ⚠️ Arquivo existe mas está vazio")
    else:
        print(f"   ❌ Atributo 'faqs' não encontrado")

    # Verificar caminho do arquivo
    print(f"\n3️⃣ Verificando caminho do arquivo...")
    if hasattr(faq_tool, 'faq_file_path'):
        print(f"   📁 Caminho: {faq_tool.faq_file_path}")
        if os.path.exists(faq_tool.faq_file_path):
            print(f"   ✅ Arquivo existe")
            size = os.path.getsize(faq_tool.faq_file_path)
            print(f"   📊 Tamanho: {size} bytes")
        else:
            print(f"   ❌ Arquivo NÃO existe neste caminho!")
    else:
        print(f"   ❌ Atributo 'faq_file_path' não encontrado")

    # Testar busca
    print(f"\n4️⃣ Testando busca no FAQ...")

    perguntas_teste = [
        "Quais são os planos?",
        "Vocês têm estoque?",
        "Como funciona o envio?",
        "Tem treinamento?"
    ]

    for pergunta in perguntas_teste:
        print(f"\n   🔍 Buscando: '{pergunta}'")
        try:
            resultado = faq_tool.buscar_faq(pergunta)

            if resultado.get('encontrado'):
                print(f"      ✅ ENCONTRADO!")
                print(f"      📌 Confiança: {resultado.get('confianca', 0)}%")
                print(f"      📝 Resposta: {resultado.get('resposta_informal', 'N/A')[:100]}...")
            else:
                print(f"      ❌ Não encontrado")
                print(f"      💬 {resultado.get('mensagem', 'Nenhuma mensagem')}")
        except Exception as e:
            print(f"      ❌ Erro: {e}")

    # Testar listar perguntas
    print(f"\n5️⃣ Testando listar_todas_perguntas...")
    try:
        resultado = faq_tool.listar_todas_perguntas()
        total = resultado.get('total', 0)
        print(f"   ✅ Total de perguntas: {total}")

        if total > 0:
            print(f"\n   📋 Primeiras 3 perguntas:")
            for i, pergunta in enumerate(resultado.get('perguntas', [])[:3], 1):
                print(f"      {i}. {pergunta}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Verificar se toolkit tem tools registradas
    print(f"\n6️⃣ Verificando tools registradas no toolkit...")
    if hasattr(faq_tool, 'functions'):
        print(f"   ✅ Toolkit tem {len(faq_tool.functions)} ferramentas:")
        for func in faq_tool.functions:
            print(f"      • {func.__name__}")
    else:
        print(f"   ⚠️ Atributo 'functions' não encontrado (pode ser normal no Agno)")

    print("\n" + "="*80)
    print("✅ TESTE ISOLADO CONCLUÍDO")
    print("="*80)

if __name__ == "__main__":
    testar_faq()
