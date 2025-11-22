#!/usr/bin/env python3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from agentes.agente_suporte import support_agent

# Dados dos 5 usuários com carros e contextos diferentes
usuarios = [
    {
        "nome": "João Silva",
        "carro": "Toyota Corolla 2022",
        "perguntas": [
            "Oi, tenho um Toyota Corolla 2022 branco e gostaria de fazer uma lavagem completa. Quanto sai?",
            "Qual o tempo para fazer?"
        ]
    },
    {
        "nome": "Maria Santos",
        "carro": "Honda Civic Preto",
        "perguntas": [
            "Oi, tenho um Honda Civic preto bem sujo. Qual o melhor serviço para deixar brilhando?",
            "Quanto custa o polimento?"
        ]
    },
    {
        "nome": "Carlos Oliveira",
        "carro": "BMW X5",
        "perguntas": [
            "Olá, tenho uma BMW X5 e quero blindagem cerâmica. Vocês fazem?",
            "Qual é o valor?"
        ]
    },
    {
        "nome": "Ana Costa",
        "carro": "Fiat 500 Vermelho",
        "perguntas": [
            "Oi, meu Fiat é vermelho e parece apagado. Vocês fazem cristalização?",
            "Quanto tempo leva?"
        ]
    },
    {
        "nome": "Roberto Ferreira",
        "carro": "Volkswagen Golf GTi",
        "perguntas": [
            "E aí, tenho um Golf GTi que precisa de higienização profissional. Vocês fazem?",
            "Qual seria o melhor pacote para meu carro?"
        ]
    }
]

resultados = {}
lock = threading.Lock()

def simular_usuario(user_idx, usuario_data):
    """Simula um usuário fazendo contato com o agente"""
    nome = usuario_data["nome"]
    carro = usuario_data["carro"]
    perguntas = usuario_data["perguntas"]

    print(f"\n{'='*80}")
    print(f"👤 USUÁRIO {user_idx + 1}: {nome} ({carro})")
    print(f"{'='*80}\n")

    respostas_usuario = []

    for idx, pergunta in enumerate(perguntas, 1):
        print(f"[{nome} - Pergunta {idx}] {pergunta}\n")

        try:
            # Executar agente e capturar resposta
            support_agent.print_response(pergunta, stream=False)

            respostas_usuario.append({
                "pergunta": pergunta,
                "status": "Respondido com sucesso"
            })

        except Exception as e:
            print(f"[Erro] {str(e)}\n")
            respostas_usuario.append({
                "pergunta": pergunta,
                "status": f"Erro: {str(e)}"
            })

        time.sleep(0.3)  # Pequena pausa entre perguntas do mesmo usuário

    with lock:
        resultados[nome] = {
            "carro": carro,
            "interacoes": respostas_usuario
        }

    print(f"\n✅ Finalizado: {nome}\n")

def main():
    print("\n")
    print("🚗" * 40)
    print("TESTE DE 5 USUÁRIOS SIMULTÂNEOS - VANLU ESTÉTICA")
    print("🚗" * 40)
    print(f"Iniciando teste em: {time.strftime('%H:%M:%S')}\n")

    inicio = time.time()

    # Executar os 5 usuários em paralelo
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for idx, usuario_data in enumerate(usuarios):
            future = executor.submit(simular_usuario, idx, usuario_data)
            futures.append(future)

        # Aguardar conclusão de todos
        for future in futures:
            future.result()

    fim = time.time()
    tempo_total = fim - inicio

    # Relatório final
    print("\n")
    print("📊" * 40)
    print("RELATÓRIO FINAL DE TESTE")
    print("📊" * 40)
    print(f"\n⏱️  Tempo total: {tempo_total:.2f} segundos")
    print(f"👥 Usuários testados: {len(resultados)}")
    print(f"📍 Status: {'✅ SUCESSO' if len(resultados) == 5 else '❌ PARCIAL'}\n")

    # Verificar dados no banco
    print("🔍 VERIFICANDO DADOS NO BANCO DE DADOS:\n")

    import psycopg2
    from psycopg2.extras import RealDictCursor

    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="spdrop_db",
            user="spdrop_user",
            password="spdrop_password"
        )

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Verificar serviços
            cur.execute("SELECT COUNT(*) as count FROM services")
            service_count = cur.fetchone()["count"]
            print(f"✅ Serviços no banco: {service_count} (esperado: 15)")

            # Listar alguns serviços
            cur.execute("SELECT name, price FROM services LIMIT 5")
            print("\nAmostra de serviços:")
            for row in cur.fetchall():
                print(f"   • {row['name']}: R$ {row['price']}")

            # Verificar disponibilidade
            cur.execute("SELECT COUNT(*) as count FROM availability WHERE available = TRUE")
            avail_count = cur.fetchone()["count"]
            print(f"\n✅ Horários disponíveis: {avail_count}")

        conn.close()

    except Exception as e:
        print(f"❌ Erro ao verificar banco: {str(e)}")

    print("\n" + "🎉" * 40)
    print("TESTE CONCLUÍDO!")
    print("🎉" * 40 + "\n")

if __name__ == "__main__":
    main()
