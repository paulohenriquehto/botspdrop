#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
from agentes.agente_suporte import support_agent
import uuid
import time

# 5 usuários com carros e serviços únicos
usuarios_teste = [
    {
        "id": 1,
        "nome": "Ana Silva",
        "phone": "11988888811",
        "carro_real": "Honda Civic Sedan",
        "primeira_fase": [
            "Oi, quanto custa lavagem?",
            "É um Honda Civic",  # Cliente responde qual é o carro
        ],
        "segunda_fase": [
            "Oi de novo! Agora quero um polimento",
            "Quanto sai o polimento?",
        ]
    },
    {
        "id": 2,
        "nome": "Bruno Costa",
        "phone": "21988888822",
        "carro_real": "Toyota CR-V SUV",
        "primeira_fase": [
            "Olá! Qual melhor serviço pra meu carro?",
            "Tenho um Toyota CR-V",  # Cliente responde qual é o carro
        ],
        "segunda_fase": [
            "Tá bom, agora quero cristalização",
            "Qual é o preço?",
        ]
    },
    {
        "id": 3,
        "nome": "Carlos Mendes",
        "phone": "31988888833",
        "carro_real": "Ford Ranger Camionete",
        "primeira_fase": [
            "Opa, preciso deixar minha pickup nova!",
            "É uma Ford Ranger",  # Cliente responde qual é o carro
        ],
        "segunda_fase": [
            "E aí, voltei! Agora quero polimento",
            "Quanto custa?",
        ]
    },
    {
        "id": 4,
        "nome": "Diana Oliveira",
        "phone": "41988888844",
        "carro_real": "Volkswagen Golf Hatch",
        "primeira_fase": [
            "Oi, tá bom? Qual é o melhor serviço?",
            "Tenho um Volkswagen Golf",  # Cliente responde qual é o carro
        ],
        "segunda_fase": [
            "Oi Luciano! Quero higienização agora",
            "Qual é o valor?",
        ]
    },
    {
        "id": 5,
        "nome": "Eduardo Ferreira",
        "phone": "51988888855",
        "carro_real": "Mitsubishi Outlander SUV Grande",
        "primeira_fase": [
            "Olá, quanto custa cristalização?",
            "Tenho um Mitsubishi Outlander",  # Cliente responde qual é o carro
        ],
        "segunda_fase": [
            "Voltei! Agora quero lavagem completa",
            "Qual é o preço?",
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

def primeira_fase(customer_ids_por_nome):
    """FASE 1: Clientes novos chegando, informando modelo do carro"""
    print("\n" + "=" * 90)
    print("⭐ FASE 1: CLIENTES NOVOS - AGENTE DEVE SOLICITAR O VEÍCULO")
    print("=" * 90)

    for usuario_data in usuarios_teste:
        customer_id = customer_ids_por_nome[usuario_data['nome']]
        session_id = str(uuid.uuid4())

        print(f"\n👤 {usuario_data['nome']} (Carro real: {usuario_data['carro_real']})")
        print(f"   ID: {customer_id} | Sessão: {session_id[:12]}...")
        print("-" * 90)

        for i, pergunta in enumerate(usuario_data['primeira_fase']):
            print(f"\n[{usuario_data['nome']}] {pergunta}")

            # Na primeira mensagem, incluir informação do customer_id
            if i == 0:
                mensagem_com_contexto = f"[CONTEXTO INTERNO: customer_id={customer_id}]\n{pergunta}"
                support_agent.print_response(
                    mensagem_com_contexto,
                    user_id=str(customer_id),
                    session_id=session_id,
                    stream=False
                )
            else:
                # Mensagens subsequentes já têm contexto
                support_agent.print_response(
                    pergunta,
                    user_id=str(customer_id),
                    session_id=session_id,
                    stream=False
                )

    print("\n" + "=" * 90)
    print("✅ FASE 1 CONCLUÍDA - Todos os clientes informaram seus veículos")
    print("=" * 90)

def segunda_fase(customer_ids_por_nome):
    """FASE 2: Clientes voltam, agente NÃO deve pedir o veículo novamente"""
    print("\n" + "=" * 90)
    print("⭐ FASE 2: CLIENTES RETORNAM - AGENTE NÃO DEVE SOLICITAR VEÍCULO")
    print("=" * 90)

    for usuario_data in usuarios_teste:
        customer_id = customer_ids_por_nome[usuario_data['nome']]
        session_id = str(uuid.uuid4())  # Nova sessão
        print(f"\n👤 {usuario_data['nome']} (Carro salvo: {usuario_data['carro_real']})")
        print(f"   ID: {customer_id} | Sessão: {session_id[:12]}...")
        print("-" * 90)

        for i, pergunta in enumerate(usuario_data['segunda_fase']):
            print(f"\n[{usuario_data['nome']}] {pergunta}")

            # Na primeira mensagem da FASE 2, incluir contexto com customer_id
            if i == 0:
                mensagem_com_contexto = f"[CONTEXTO INTERNO: customer_id={customer_id}]\n{pergunta}"
                support_agent.print_response(
                    mensagem_com_contexto,
                    user_id=str(customer_id),
                    session_id=session_id,
                    stream=False
                )
            else:
                # Mensagens subsequentes já têm contexto
                support_agent.print_response(
                    pergunta,
                    user_id=str(customer_id),
                    session_id=session_id,
                    stream=False
                )

    print("\n" + "=" * 90)
    print("✅ FASE 2 CONCLUÍDA - Verificar se agente lembrou dos carros!")
    print("=" * 90)

def main():
    print("\n")
    print("🚗" * 45)
    print("TESTE DE PERSISTÊNCIA - VERIFICAR SE AGENTE SALVA/LEMBRA DO VEÍCULO")
    print("🚗" * 45)
    print("\nCenário:")
    print("• 5 usuários únicos com carros únicos")
    print("• FASE 1: Cliente novo chega, agente PEDE o veículo, cliente informa")
    print("• PAUSA: Aguarda tempo para simular sessão diferente")
    print("• FASE 2: Cliente volta, agente NÃO deve pedir o veículo novamente")
    print("• OBJETIVO: Validar storage/memory do agente com user_id isolado\n")

    # Criar clientes primeiro
    customer_ids_por_nome = {}
    for usuario_data in usuarios_teste:
        customer_id, session_id = criar_cliente_e_sessao(usuario_data)
        customer_ids_por_nome[usuario_data['nome']] = customer_id

    # FASE 1: Clientes novos chegam e informam veículos
    primeira_fase(customer_ids_por_nome)

    # PAUSA
    print("\n" + "⏳" * 45)
    print("AGUARDANDO 5 SEGUNDOS ANTES DA FASE 2...")
    print("(Simulando: cliente desconectou e voltou mais tarde)")
    print("⏳" * 45)
    time.sleep(5)

    # FASE 2: Clientes retornam
    segunda_fase(customer_ids_por_nome)

    # Verificar dados no banco
    print("\n" + "🔍" * 45)
    print("VERIFICAÇÃO DE DADOS NO BANCO")
    print("🔍" * 45)

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="spdrop_db",
        user="spdrop_user",
        password="spdrop_password"
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Verificar clientes e seus contextos
        cur.execute("""
            SELECT
                c.name as cliente,
                cc.car_model as veiculo_salvo
            FROM customers c
            LEFT JOIN customer_context cc ON c.id = cc.customer_id
            WHERE c.name IN ('Ana Silva', 'Bruno Costa', 'Carlos Mendes', 'Diana Oliveira', 'Eduardo Ferreira')
            ORDER BY c.created_at DESC
            LIMIT 5
        """)

        print("\n✅ Clientes e Veículos Salvos no Storage:")
        print("-" * 90)
        for row in cur.fetchall():
            if row['veiculo_salvo']:
                print(f"   {row['cliente']:<20} → {row['veiculo_salvo']}")
            else:
                print(f"   {row['cliente']:<20} → (NENHUM VEÍCULO SALVO!)")

        # Verificar sessões
        cur.execute("""
            SELECT COUNT(*) as count FROM sessions
            WHERE customer_id IN (
                SELECT id FROM customers
                WHERE name IN ('Ana Silva', 'Bruno Costa', 'Carlos Mendes', 'Diana Oliveira', 'Eduardo Ferreira')
            )
        """)
        sessoes = cur.fetchone()['count']
        print(f"\n✅ Sessões criadas: {sessoes}")

    conn.close()

    print("\n" + "🎉" * 45)
    print("TESTE DE PERSISTÊNCIA CONCLUÍDO!")
    print("📌 RESULTADO ESPERADO:")
    print("   • Fase 1: Agente PERGUNTA o veículo ✅")
    print("   • Fase 2: Agente NÃO PERGUNTA o veículo (usa storage) ✅")
    print("   • Storage: Todos os 5 veículos salvos ✅")
    print("🎉" * 45 + "\n")

if __name__ == "__main__":
    main()
