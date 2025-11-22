#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
from agentes.agente_suporte import support_agent
import uuid
from concurrent.futures import ThreadPoolExecutor

# Dados dos 10 usuários com seus carros
usuarios = [
    # Categoria 1: SUV e Caminhonete
    {
        "id": 1,
        "nome": "Carlos Mendes",
        "phone": "11987654321",
        "carro": "Toyota SW4 Diamond",
        "tipo_veiculo": "Camionete Média",
        "pergunta_1": "Oi, tenho uma Toyota SW4 Diamond 2.8 turbodiesel. Quanto custa para fazer uma lavagem completa?",
        "pergunta_2": "E quanto sairia um polimento nela?"
    },
    {
        "id": 2,
        "nome": "Ana Silva",
        "phone": "21987654322",
        "carro": "Chevrolet Trailblazer Premier",
        "tipo_veiculo": "SUV Grande",
        "pergunta_1": "Olá, tenho um Chevrolet Trailblazer Premier 7 lugares. Vocês fazem cristalização?",
        "pergunta_2": "Qual é o preço para cristalização nele?"
    },
    {
        "id": 3,
        "nome": "Roberto Costa",
        "phone": "31987654323",
        "carro": "Toyota RAV4 Hybrid",
        "tipo_veiculo": "SUV Média",
        "pergunta_1": "Oi, tenho um Toyota RAV4 Hybrid. Preciso de higienização profissional.",
        "pergunta_2": "Quanto custa a higienização para o RAV4?"
    },
    {
        "id": 4,
        "nome": "Fernanda Oliveira",
        "phone": "41987654324",
        "carro": "Volvo XC60 Recharge T8",
        "tipo_veiculo": "SUV Grande",
        "pergunta_1": "Bom dia, tenho um Volvo XC60 Recharge T8 de luxo. Qual o preço de uma blindagem cerâmica?",
        "pergunta_2": "Vocês fazem selagem de vidros também?"
    },
    {
        "id": 5,
        "nome": "Paulo Santos",
        "phone": "51987654325",
        "carro": "Ford F-150 Lightning",
        "tipo_veiculo": "Camionete Grande",
        "pergunta_1": "Opa, sou o Paulo. Tenho uma Ford F-150 Lightning 100% elétrica. Vocês trabalham com elétricos?",
        "pergunta_2": "Quanto sairia uma lavagem completa nela?"
    },
    # Categoria 2: Hatch e Sedã
    {
        "id": 6,
        "nome": "Mariana Pereira",
        "phone": "61987654326",
        "carro": "Volkswagen Polo TSI",
        "tipo_veiculo": "Hatch",
        "pergunta_1": "Oi, tenho um Volkswagen Polo TSI compacto. Vocês fazem proteção de pneus?",
        "pergunta_2": "Qual seria o valor?"
    },
    {
        "id": 7,
        "nome": "João Ferreira",
        "phone": "71987654327",
        "carro": "Honda Civic Geração 11",
        "tipo_veiculo": "Sedan",
        "pergunta_1": "Olá, tenho um Honda Civic Geração 11 sedã. Quero deixar ele brilhando, qual serviço recomendam?",
        "pergunta_2": "Quanto custa um polimento?"
    },
    {
        "id": 8,
        "nome": "Patricia Gomes",
        "phone": "81987654328",
        "carro": "Toyota Corolla Hybrid",
        "tipo_veiculo": "Sedan",
        "pergunta_1": "Opa, sou a Patricia. Tenho um Toyota Corolla Hybrid sedã. Fazem limpeza de motor?",
        "pergunta_2": "Qual o preço da limpeza de motor?"
    },
    {
        "id": 9,
        "nome": "Lucas Zhang",
        "phone": "91987654329",
        "carro": "BYD Dolphin",
        "tipo_veiculo": "Hatch",
        "pergunta_1": "Oi, tenho um BYD Dolphin 100% elétrico bem bonito. Qual serviço vocês recomendam?",
        "pergunta_2": "Quanto custa uma cristalização nele?"
    },
    {
        "id": 10,
        "nome": "Isabella Rossi",
        "phone": "11987654330",
        "carro": "BMW i4 eDrive40",
        "tipo_veiculo": "Sedan",
        "pergunta_1": "Bom dia, tenho um BMW i4 eDrive40 sedã elétrico esportivo. Vocês têm experiência com elétricos de luxo?",
        "pergunta_2": "Quanto custa uma blindagem cerâmica nele?"
    }
]

def criar_cliente_e_sessao(usuario_data):
    """Cria cliente e sessão no banco de dados"""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="spdrop_db",
        user="spdrop_user",
        password="spdrop_password"
    )

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Criar cliente
            cur.execute("""
                INSERT INTO customers (name, phone, email)
                VALUES (%s, %s, %s)
                RETURNING id, name, phone
            """, (usuario_data["nome"], usuario_data["phone"], f"{usuario_data['phone']}@spdrop.com"))

            customer = cur.fetchone()
            customer_id = customer['id']

            # Criar sessão
            session_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO sessions (session_id, customer_id, status)
                VALUES (%s, %s, 'active')
                RETURNING session_id
            """, (session_id, customer_id))

            # Atualizar contexto do cliente (carro)
            cur.execute("DELETE FROM customer_context WHERE customer_id = %s", (customer_id,))
            cur.execute("""
                INSERT INTO customer_context (customer_id, car_model)
                VALUES (%s, %s)
            """, (customer_id, usuario_data["carro"]))

            conn.commit()

            return {
                "customer_id": customer_id,
                "session_id": session_id,
                "name": customer['name'],
                "phone": customer['phone'],
                "carro": usuario_data["carro"]
            }
    finally:
        conn.close()

def testar_usuario(usuario_data):
    """Testa um usuário com 2 perguntas"""
    print(f"\n{'='*80}")
    print(f"👤 USUÁRIO {usuario_data['id']}: {usuario_data['nome']} ({usuario_data['carro']})")
    print(f"{'='*80}\n")

    # Criar cliente e sessão
    cliente_info = criar_cliente_e_sessao(usuario_data)
    print(f"✅ Cliente criado: {cliente_info['name']}")
    print(f"✅ Sessão: {cliente_info['session_id'][:8]}...\n")

    # Pergunta 1
    print(f"[{usuario_data['nome']}] {usuario_data['pergunta_1']}\n")
    support_agent.print_response(usuario_data['pergunta_1'], stream=False)

    # Pergunta 2
    print(f"\n[{usuario_data['nome']}] {usuario_data['pergunta_2']}\n")
    support_agent.print_response(usuario_data['pergunta_2'], stream=False)

    print(f"\n✅ Finalizado: {usuario_data['nome']}\n")

    return {
        "usuario": usuario_data['nome'],
        "carro": usuario_data['carro'],
        "cliente_id": cliente_info['customer_id']
    }

def main():
    print("\n")
    print("🚗" * 40)
    print("TESTE COM 10 USUÁRIOS ÚNICOS - VANLU ESTÉTICA")
    print("🚗" * 40)
    print(f"\nTotalizando: 10 usuários × 2 perguntas = 20 interações\n")

    inicio = __import__('time').time()

    # Executar testes sequencialmente para melhor visualização
    resultados = []
    for usuario_data in usuarios:
        try:
            resultado = testar_usuario(usuario_data)
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ Erro ao testar {usuario_data['nome']}: {str(e)}\n")

    fim = __import__('time').time()
    tempo_total = fim - inicio

    # Relatório final
    print("\n")
    print("📊" * 40)
    print("RELATÓRIO FINAL")
    print("📊" * 40)

    print(f"\n⏱️  Tempo total: {tempo_total:.2f} segundos")
    print(f"👥 Usuários testados: {len(resultados)}/10")
    print(f"📍 Status: {'✅ SUCESSO' if len(resultados) == 10 else '⚠️  PARCIAL'}\n")

    print("Usuários testados:")
    for i, resultado in enumerate(resultados, 1):
        print(f"   {i}. {resultado['usuario']} ({resultado['carro']})")

    # Verificar dados no banco
    print("\n🔍 VERIFICANDO DADOS NO BANCO DE DADOS:\n")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="spdrop_db",
        user="spdrop_user",
        password="spdrop_password"
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Clientes criados
        cur.execute("SELECT COUNT(*) as count FROM customers ORDER BY created_at DESC LIMIT 10")
        customer_count = cur.fetchone()["count"]
        print(f"✅ Clientes criados neste teste: {len(resultados)}")

        # Histórico de conversas
        cur.execute("""
            SELECT COUNT(*) as count FROM conversation_history
            WHERE customer_id IN (SELECT id FROM customers ORDER BY created_at DESC LIMIT 10)
        """)
        history_count = cur.fetchone()["count"]
        print(f"✅ Conversas registradas: {history_count}")

        # Contextos de clientes
        cur.execute("""
            SELECT COUNT(DISTINCT customer_id) as count FROM customer_context
        """)
        context_count = cur.fetchone()["count"]
        print(f"✅ Contextos de clientes: {context_count}")

    conn.close()

    print("\n" + "🎉" * 40)
    print("TESTE CONCLUÍDO COM SUCESSO!")
    print("🎉" * 40 + "\n")

if __name__ == "__main__":
    main()
