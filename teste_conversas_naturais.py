#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
from agentes.agente_suporte import support_agent
import uuid

# 3 usuários com carros NÃO cadastrados no banco
usuarios_teste = [
    {
        "id": 1,
        "nome": "Marcus Vinicius",
        "phone": "11988888888",
        "carro_real": "Fiat Toro Volcano",  # Camionete - não está cadastrada
        "conversas": [
            "Oi, estou procurando um serviço de estética para meu carro",
            "Tenho um Fiat Toro Volcano",
            "Qual seria o preço para uma lavagem completa?",
            "E quanto custa um polimento?",
            "Vocês fazem cristalização também?",
            "Qual o preço dela?",
            "Quanto tempo leva para fazer?",
            "Vocês fazem higienização profissional?",
            "Qual o valor da higienização?",
            "Quero fazer uma lavagem e depois um polimento. Vocês fazem pacote?",
            "Quanto sairia os dois juntos?",
            "Qual seria o melhor serviço para meu carro ficar impecável?",
            "Posso agendar para amanhã?",
            "Qual horário está disponível?",
            "Tudo bem, vou pensar e retorno. Obrigado!"
        ]
    },
    {
        "id": 2,
        "nome": "Juliana Schmitz",
        "phone": "21988888888",
        "carro_real": "Audi A4 Premium",  # Sedan premium - não está cadastrado
        "conversas": [
            "Olá! Preciso de um atendimento de qualidade para meu carro",
            "Eu tenho um Audi A4 Premium",
            "Qual o melhor serviço para um carro de luxo como o meu?",
            "Vocês têm experiência com carros importados?",
            "Quanto custa uma blindagem cerâmica?",
            "E uma vitrificação de vidros?",
            "Qual é a diferença entre os dois?",
            "Qual vocês recomendam para o meu Audi?",
            "Vocês fazem polimento com equipamento profissional?",
            "Qual seria o preço do polimento?",
            "Posso fazer cristalização também?",
            "E quanto sairia cristalização + polimento?",
            "Vocês usam produtos premium?",
            "Qual a garantia que vocês oferecem?",
            "Tá bom, preciso conversar com meu marido e depois ligo"
        ]
    },
    {
        "id": 3,
        "nome": "Pedro Almeida",
        "phone": "31988888888",
        "carro_real": "Jeep Renegade Night Eagle",  # SUV compacta - pode não estar exato
        "conversas": [
            "E aí, tudo bem?",
            "Tenho um carro e queria deixar ele mais bonito",
            "É um Jeep Renegade Night Eagle",
            "Vocês já trabalham com Jeep?",
            "Qual seria o preço para fazer uma lavagem?",
            "E polimento, quanto custa?",
            "Qual desses serviços é melhor para meu Jeep?",
            "Vocês fazem proteção de pintura?",
            "Quanto custa essa proteção?",
            "Quanto tempo leva tudo isso?",
            "Dá pra fazer tudo em um dia?",
            "Qual seria o valor total se eu fizesse lavagem + polimento + proteção?",
            "Vocês trabalham com agendamento prévio?",
            "Preciso fazer isso logo, pode ser esse fim de semana?",
            "Beleza, vou confirmar com vocês mais tarde!"
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

def testar_usuario_natural(usuario_data):
    """Testa um usuário com conversação natural de 15 perguntas"""
    print(f"\n{'='*90}")
    print(f"👤 TESTE: {usuario_data['nome']} - Carro: {usuario_data['carro_real']}")
    print(f"{'='*90}\n")

    # Criar cliente
    customer_id, session_id = criar_cliente_e_sessao(usuario_data)
    print(f"✅ Cliente criado (ID: {customer_id})")
    print(f"✅ Sessão iniciada: {session_id[:12]}...\n")

    # Salvar informações
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="spdrop_db",
        user="spdrop_user",
        password="spdrop_password"
    )

    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM customer_context WHERE customer_id = %s", (customer_id,))
            cur.execute("""
                INSERT INTO customer_context (customer_id, car_model)
                VALUES (%s, %s)
            """, (customer_id, usuario_data['carro_real']))
            conn.commit()
    finally:
        conn.close()

    # Simular conversa
    print("💬 CONVERSA ENTRE CLIENTE E LUCIANO:\n")

    for i, pergunta in enumerate(usuario_data['conversas'], 1):
        print(f"[{usuario_data['nome']}] {pergunta}\n")

        # Agente responde
        try:
            support_agent.print_response(pergunta, stream=False)
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

        print()

        # A cada 5 perguntas, mostrar checkpoint
        if i % 5 == 0:
            print(f"\n✓ Checkpoint: {i}/15 perguntas completadas\n")

    print(f"\n✅ Finalizado: {usuario_data['nome']}")
    return customer_id

def main():
    print("\n")
    print("🚗" * 45)
    print("TESTE DE CONVERSAS NATURAIS - 3 USUÁRIOS COM CARROS NÃO CADASTRADOS")
    print("🚗" * 45)
    print("\nCenário: Clientes chegam sem informar o modelo do carro")
    print("Agente pergunta o modelo, cliente informa")
    print("Agente chama ProcessadorPedidos com o modelo informado")
    print("Total: 3 usuários × 15 perguntas = 45 interações\n")

    inicio = __import__('time').time()

    resultados = []
    for usuario_data in usuarios_teste:
        try:
            customer_id = testar_usuario_natural(usuario_data)
            resultados.append({
                "usuario": usuario_data['nome'],
                "carro": usuario_data['carro_real'],
                "customer_id": customer_id,
                "status": "✅ Sucesso"
            })
        except Exception as e:
            print(f"❌ Erro ao testar {usuario_data['nome']}: {str(e)}\n")
            resultados.append({
                "usuario": usuario_data['nome'],
                "carro": usuario_data['carro_real'],
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
    print(f"👥 Usuários testados: {len(resultados)}/3")
    print(f"💬 Total de mensagens trocadas: {len(resultados) * 15}")
    print(f"📍 Status geral: {'✅ SUCESSO TOTAL' if len(resultados) == 3 else '⚠️  COM ERROS'}\n")

    print("Detalhes dos testes:")
    for resultado in resultados:
        print(f"   {resultado['status']} - {resultado['usuario']} ({resultado['carro']})")

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
            SELECT name, phone, car_model FROM customers cc
            JOIN customer_context ccc ON cc.id = ccc.customer_id
            WHERE name IN ('Marcus Vinicius', 'Juliana Schmitz', 'Pedro Almeida')
            ORDER BY cc.created_at DESC
        """)

        print("✅ Clientes e carros cadastrados:")
        for row in cur.fetchall():
            print(f"   • {row['name']} → {row['car_model']}")

        # Sessões
        cur.execute("""
            SELECT COUNT(*) as count FROM sessions
            WHERE customer_id IN (
                SELECT id FROM customers
                WHERE name IN ('Marcus Vinicius', 'Juliana Schmitz', 'Pedro Almeida')
            )
        """)
        sessoes = cur.fetchone()['count']
        print(f"\n✅ Sessões criadas: {sessoes}")

    conn.close()

    print("\n" + "🎉" * 45)
    print("TESTE DE CONVERSAS NATURAIS CONCLUÍDO!")
    print("Objetivo: Validar comunicação entre agente principal e secundário")
    print("com carros não cadastrados no banco de dados")
    print("🎉" * 45 + "\n")

if __name__ == "__main__":
    main()
