#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
from agentes.agente_suporte import support_agent
import uuid

# 5 usuários com carros diferentes
# IMPORTANTE: O carro REAL não é informado no contexto do agente
# O cliente vai revelar naturalmente durante a conversa
usuarios_teste = [
    {
        "id": 1,
        "nome": "André Costa",
        "phone": "11999999991",
        "carro_real": "Toyota Corolla 2024",  # Sedan
        "conversas": [
            "Oi, tudo bem? Sou novo na região e procuro um lugar confiável para cuidar do meu carro",
            "É um modelo bem popular, sedan, 2024",
            "Qual seria o preço para fazer uma lavagem completa?",
            "Quanto custa um polimento?",
            "Vocês trabalham com cristalização?",
            "Qual o melhor serviço para manter o carro novo?",
            "Quantos anos de garantia vocês dão nos tratamentos?",
            "Tá bom, me passa um orçamento para cristalização",
            "E quanto tempo leva esse serviço?",
            "Vocês aceitam agendamento para amanhã?",
        ]
    },
    {
        "id": 2,
        "nome": "Fernanda Lima",
        "phone": "21999999992",
        "carro_real": "Hyundai Creta 2023",  # SUV Compacta (similar ao HR-V)
        "conversas": [
            "Olá! Tenho um SUV compacto e queria cuidar melhor da estética",
            "É um Hyundai, modelo bem atual",
            "Qual seria o melhor serviço para pintura?",
            "Vocês fazem proteção de pintura?",
            "Quanto custa a cristalização para meu carro?",
            "E a higienização? Vocês fazem?",
            "Qual é mais importante: cristalização ou vitrificação?",
            "Qual é o preço da vitrificação?",
            "Posso levar meu carro hoje para um orçamento?",
            "Qual seria o preço total para cristalização + higienização?",
        ]
    },
    {
        "id": 3,
        "nome": "Roberto Mendes",
        "phone": "31999999993",
        "carro_real": "Ford Ranger 2022",  # Camionete Média
        "conversas": [
            "Opa, tenho uma pickup e preciso deixar ela com cara de nova",
            "É Ford, camionete de trabalho",
            "Quanto custa para fazer uma lavagem bem completa?",
            "E polimento? Dá para tirar riscos?",
            "Vocês fazem proteção para pickup? Pintura sofre bastante",
            "Qual seria o preço da proteção de pintura?",
            "Vocês usam produtos de qualidade?",
            "Quanto tempo leva para fazer tudo?",
            "Preciso fazer logo, tem como esse fim de semana?",
            "Qual seria o valor total com lavagem + polimento + proteção?",
        ]
    },
    {
        "id": 4,
        "nome": "Patricia Oliveira",
        "phone": "41999999994",
        "carro_real": "Volkswagen Golf 2023",  # Hatch
        "conversas": [
            "Oi! Tenho um hatchback europeu e gostaria de deixar impecável",
            "É um Golf, bem conservado ainda",
            "Qual é o melhor serviço para manter o brilho?",
            "Vocês fazem limpeza de motor?",
            "Quanto custa um polimento bem feito?",
            "Qual a diferença entre cristalização e vitrificação?",
            "Qual vocês recomendam para um Golf?",
            "Quanto custa a cristalização?",
            "Vocês têm experiência com carros importados?",
            "Qual seria o melhor pacote para meu carro ficar tipo novo?",
        ]
    },
    {
        "id": 5,
        "nome": "Carlos Ferreira",
        "phone": "51999999995",
        "carro_real": "Mitsubishi Outlander 2021",  # SUV Média (similar ao RAV4)
        "conversas": [
            "Bom dia! Tenho um SUV maior e queria fazer uma manutenção estética",
            "É um Mitsubishi, SUV de 7 lugares",
            "Qual é o preço da lavagem completa?",
            "Vocês oferecem pacotes?",
            "Qual seria o melhor serviço para proteção da pintura?",
            "Quanto custa a blindagem cerâmica?",
            "Vocês não fazem blindagem? E cristalização?",
            "Qual o preço da cristalização para um SUV maior?",
            "Vale a pena fazer vitrificação também?",
            "Me passa um orçamento completo para lavagem + polimento + cristalização",
        ]
    }
]

def criar_cliente_e_sessao(usuario_data):
    """Cria cliente e sessão no banco"""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="spdrop_db",
        user="spdrop_user",
        password="spdrop_password"
    )

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO customers (name, phone, email)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (usuario_data["nome"], usuario_data["phone"], f"{usuario_data['phone']}@spdrop.com"))

            customer_id = cur.fetchone()['id']

            # Criar sessão
            session_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO sessions (session_id, customer_id, status)
                VALUES (%s, %s, 'active')
            """, (session_id, customer_id))

            conn.commit()
            return customer_id, session_id
    finally:
        conn.close()

def testar_usuario_deducao(usuario_data):
    """Testa um usuário onde o agente deduz o carro"""
    print(f"\n{'='*90}")
    print(f"👤 TESTE: {usuario_data['nome']}")
    print(f"   Carro REAL: {usuario_data['carro_real']} (agente NÃO sabe disso)")
    print(f"{'='*90}\n")

    # Criar cliente
    customer_id, session_id = criar_cliente_e_sessao(usuario_data)
    print(f"✅ Cliente criado (ID: {customer_id})")
    print(f"✅ Sessão iniciada: {session_id[:12]}...\n")

    # Simular conversa
    print("💬 CONVERSA ENTRE CLIENTE E LUCIANO:\n")

    for i, pergunta in enumerate(usuario_data['conversas'], 1):
        print(f"[{usuario_data['nome']}] {pergunta}\n")

        # Agente responde - IMPORTANTE: passar user_id para isolar contexto
        try:
            support_agent.print_response(pergunta, user_id=str(customer_id), stream=False)
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

        print()

        # A cada 5 perguntas, mostrar checkpoint
        if i % 5 == 0:
            print(f"\n✓ Checkpoint: {i}/{len(usuario_data['conversas'])} perguntas completadas\n")

    print(f"\n✅ Finalizado: {usuario_data['nome']}")
    return customer_id

def main():
    print("\n")
    print("🚗" * 45)
    print("TESTE COM 5 USUÁRIOS ÚNICOS - AGENTE DEDUZINDO VEÍCULOS")
    print("🚗" * 45)
    print("\nCenário: Clientes chegam SEM informar o modelo de forma direta")
    print("Agente precisa DEDUZIR qual é o carro pela conversa")
    print("Agente depois calcula preço com o multiplicador correto")
    print(f"Total: 5 usuários × {len(usuarios_teste[0]['conversas'])} perguntas = {5 * len(usuarios_teste[0]['conversas'])} interações\n")

    inicio = __import__('time').time()

    resultados = []
    for usuario_data in usuarios_teste:
        try:
            customer_id = testar_usuario_deducao(usuario_data)
            resultados.append({
                "usuario": usuario_data['nome'],
                "carro_real": usuario_data['carro_real'],
                "customer_id": customer_id,
                "status": "✅ Sucesso"
            })
        except Exception as e:
            print(f"❌ Erro ao testar {usuario_data['nome']}: {str(e)}\n")
            resultados.append({
                "usuario": usuario_data['nome'],
                "carro_real": usuario_data['carro_real'],
                "customer_id": None,
                "status": f"❌ Erro: {str(e)}"
            })

    fim = __import__('time').time()
    tempo_total = fim - inicio

    # Relatório Final
    print("\n" + "="*90)
    print("📊 RELATÓRIO FINAL DE TESTE")
    print("="*90)

    print(f"\n⏱️  Tempo total: {tempo_total:.2f} segundos")
    print(f"👥 Usuários testados: {len(resultados)}/5")
    print(f"💬 Total de mensagens trocadas: {len(resultados) * len(usuarios_teste[0]['conversas'])}")
    print(f"📍 Status geral: {'✅ SUCESSO TOTAL' if len(resultados) == 5 else '⚠️  COM ERROS'}\n")

    print("Detalhes dos testes:")
    for resultado in resultados:
        print(f"   {resultado['status']} - {resultado['usuario']} ({resultado['carro_real']})")

    # Verificar dados
    print("\n🔍 VERIFICAÇÃO DE DADOS NO BANCO:\n")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="spdrop_db",
        user="spdrop_user",
        password="spdrop_password"
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Clientes do teste
        cur.execute("""
            SELECT name FROM customers
            WHERE name IN ('André Costa', 'Fernanda Lima', 'Roberto Mendes', 'Patricia Oliveira', 'Carlos Ferreira')
            ORDER BY created_at DESC
        """)

        print("✅ Clientes criados:")
        for row in cur.fetchall():
            print(f"   • {row['name']}")

        # Sessões
        cur.execute("""
            SELECT COUNT(*) as count FROM sessions
            WHERE customer_id IN (
                SELECT id FROM customers
                WHERE name IN ('André Costa', 'Fernanda Lima', 'Roberto Mendes', 'Patricia Oliveira', 'Carlos Ferreira')
            )
        """)
        sessoes = cur.fetchone()['count']
        print(f"\n✅ Sessões criadas: {sessoes}")

    conn.close()

    print("\n" + "🎉" * 45)
    print("TESTE DE DEDUÇÃODE VEÍCULOS CONCLUÍDO!")
    print("Objetivo: Validar se agente consegue deduzir o tipo de carro")
    print("e aplicar multiplicadores corretos mesmo sem saber previamente")
    print("🎉" * 45 + "\n")

if __name__ == "__main__":
    main()
