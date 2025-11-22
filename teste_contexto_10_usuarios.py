#!/usr/bin/env python3
"""
Teste de Contexto - 10 Usuários com 25 Mensagens Cada

Objetivo: Verificar se a Gabi mantém o contexto da conversa
mesmo com conversas longas e múltiplos usuários simultâneos.
"""

import requests
import time
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurações
BOT_WEBHOOK_URL = "http://localhost:5000/webhook"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "spdrop_db",
    "user": "spdrop_user",
    "password": "spdrop_password"
}

# 10 Usuários de Teste
USUARIOS = [
    {
        "nome": "Carlos Silva",
        "phone": "5511987654321",
        "perfil": "iniciante_interessado",
        "objetivo": "Fazer teste grátis"
    },
    {
        "nome": "Maria Santos",
        "phone": "5521976543210",
        "perfil": "experiente_rapido",
        "objetivo": "Comprar plano semestral"
    },
    {
        "nome": "João Oliveira",
        "phone": "5531965432109",
        "perfil": "indeciso",
        "objetivo": "Esclarecer dúvidas"
    },
    {
        "nome": "Ana Costa",
        "phone": "5541954321098",
        "perfil": "sem_dinheiro",
        "objetivo": "Negociar desconto"
    },
    {
        "nome": "Pedro Lima",
        "phone": "5551943210987",
        "perfil": "comparando_plataformas",
        "objetivo": "Comparar com concorrentes"
    },
    {
        "nome": "Julia Martins",
        "phone": "5561932109876",
        "perfil": "empolgada",
        "objetivo": "Começar imediatamente"
    },
    {
        "nome": "Lucas Ferreira",
        "phone": "5571921098765",
        "perfil": "tecnico",
        "objetivo": "Entender funcionamento"
    },
    {
        "nome": "Beatriz Alves",
        "phone": "5581910987654",
        "perfil": "desconfiada",
        "objetivo": "Verificar legitimidade"
    },
    {
        "nome": "Rafael Souza",
        "phone": "5591909876543",
        "perfil": "apressado",
        "objetivo": "Resposta rápida"
    },
    {
        "nome": "Camila Rocha",
        "phone": "5585898765432",
        "perfil": "detalhista",
        "objetivo": "Todas as informações"
    }
]

# Fluxos de Conversa por Perfil
FLUXOS = {
    "iniciante_interessado": [
        "Oi", "Quero conhecer a plataforma", "Nunca fiz dropshipping",
        "Como funciona?", "Quanto custa?", "Tem teste grátis?",
        "Sim, quero testar", "Meu nome é {nome}", "Sou totalmente iniciante",
        "Preciso de ajuda", "Quanto tempo leva pra aprender?",
        "Vocês dão suporte?", "Tem cursos?", "E os fornecedores são confiáveis?",
        "Posso vender no Mercado Livre?", "E no Instagram?",
        "Preciso de CNPJ?", "Quanto dá pra ganhar?", "Tem garantia?",
        "Ok, quero o teste", "Como faço pra começar?", "Preciso pagar agora?",
        "Pode me explicar de novo o teste?", "Tá bom, vamos fazer!",
        "Qual meu próximo passo?"
    ],
    "experiente_rapido": [
        "Boa noite", "Já trabalho com dropshipping", "Quero mudar de plataforma",
        "Quais são os diferenciais?", "Quantos produtos tem?",
        "Os fornecedores entregam rápido?", "Tem API?", "Integra com Shopify?",
        "Qual o melhor plano?", "Tem desconto?", "Quanto tá o semestral?",
        "Aceita cartão?", "Tem boleto?", "Pode parcelar?",
        "Quantas parcelas?", "Tem suporte prioritário?", "E analista dedicado?",
        "Ok, quero fechar", "Meu nome é {nome}", "Pode me mandar o link?",
        "Vou pagar agora", "Quanto tempo pra liberar?", "Vou receber por email?",
        "Perfeito", "Obrigada!"
    ],
    "indeciso": [
        "Olá", "Vi um anúncio", "Não sei se é pra mim",
        "Isso funciona mesmo?", "Já ouvi falar de golpes", "Como sei que é sério?",
        "Tem depoimentos?", "Alguém que eu conheça usa?", "Quanto é o investimento?",
        "Nossa, é caro", "Tem mais barato?", "E se não der certo?",
        "Posso cancelar?", "Tem reembolso?", "Deixa eu pensar",
        "Quanto tempo tenho pra decidir?", "A promoção acaba quando?",
        "Tem só 3 vagas?", "Não sei se tenho tempo", "Trabalho muito",
        "Vou conversar com minha esposa", "Posso te dar uma resposta amanhã?",
        "Pode me mandar mais informações?", "Vou pensar melhor",
        "Te respondo depois"
    ],
    "sem_dinheiro": [
        "Oi", "Quero trabalhar com vocês", "Mas tô duro agora",
        "Tem como começar sem pagar?", "Não tem plano grátis?",
        "69 reais tá caro pra mim", "Dá pra parcelar em mais vezes?",
        "Aceita Pix parcelado?", "E se eu pagar metade agora?", "Tem desconto?",
        "Não tem uma promoção melhor?", "Posso pagar com comissão das vendas?",
        "Eu vendo e pago depois?", "Tá difícil esse mês", "Meu nome é {nome}",
        "Eu realmente quero", "Mas não tenho dinheiro agora",
        "Semana que vem recebo", "Pode reservar uma vaga?",
        "Não perde esse desconto pra mim", "Eu volto quando puder pagar",
        "Tem lista de espera?", "Me avisa de promoções", "Valeu"
    ],
    "comparando_plataformas": [
        "Boa tarde", "Tô comparando plataformas", "Uso a Dropi hoje",
        "O que vocês tem de diferente?", "Lá tem 2000 produtos",
        "Quantos produtos vocês tem?", "Os preços são melhores?",
        "E a margem de lucro?", "Fornecedores são os mesmos?",
        "Tem fornecedor exclusivo?", "Prazo de entrega é menor?",
        "A plataforma é mais rápida?", "Tem mais recursos?",
        "Qual vantagem real?", "Por que eu deveria mudar?",
        "Lá eu pago 79", "Aqui é quanto?", "69 na promoção né",
        "Mas no normal é quanto?", "Meu nome é {nome}",
        "Vou testar pra comparar", "Tem período de teste?",
        "Posso usar as duas?", "Deixa eu avaliar", "Obrigado"
    ],
    "empolgada": [
        "Oiiii!", "Quero começar AGORA!", "Tô super animada!",
        "Como faço?", "Meu nome é {nome}", "Pode me explicar rápido?",
        "Tô pronta pra começar!", "Quanto é?", "Aceita cartão?",
        "Vou pagar já!", "Quando libera?", "Hoje ainda?",
        "Maravilha!", "E aí, o que eu faço?", "Já posso escolher produtos?",
        "Como vendo?", "Boto no Instagram?", "E no TikTok?",
        "Vou arrasar!", "Tô muito feliz!", "Sempre quis ter meu negócio!",
        "Vai dar certo!", "Vou me dedicar muito!", "Pode confiar!",
        "Obrigadaaaa!", "Vamos lá!"
    ],
    "tecnico": [
        "Olá", "Preciso de informações técnicas", "Qual a stack da plataforma?",
        "Tem API REST?", "Documentação?", "Tem webhook?",
        "Como é a integração?", "Usa OAuth?", "Tem SDK?",
        "Rate limit é quanto?", "Tem ambiente de sandbox?",
        "Como funciona o fluxo de pedidos?", "É em tempo real?",
        "Tem notificações push?", "E sobre segurança?", "Usa SSL?",
        "Os dados são criptografados?", "Tem backup?", "E redundância?",
        "Meu nome é {nome}", "Qual o SLA?", "Tem status page?",
        "Uptime é quanto?", "Ok, vou testar", "Obrigado"
    ],
    "desconfiada": [
        "Oi", "Isso é golpe?", "Como sei que é real?",
        "Tem CNPJ?", "Cadê o endereço?", "Tem telefone fixo?",
        "Quem é o dono?", "Empresa existe há quanto tempo?",
        "Tem reclamação no Reclame Aqui?", "Já vi muita gente sendo enganada",
        "Dropshipping é pirâmide?", "Isso é legal?", "Receita aceita?",
        "E se eu não receber o produto?", "Cliente pode processar?",
        "Vocês têm CNPJ mesmo?", "Meu nome é {nome}", "Ainda tô com medo",
        "Me prova que é sério", "Tem certificado?", "E se der problema?",
        "Quem responde?", "Vou pesquisar mais", "Depois volto"
    ],
    "apressado": [
        "Oi", "Tô com pressa", "Responde rápido", "Quanto custa?",
        "Aceita cartão?", "Pode parcelar?", "Quantas vezes?",
        "Libera hoje?", "Sim ou não?", "Meu nome é {nome}",
        "Passa o link", "Vou pagar", "Agora", "Já era", "E aí?",
        "Liberou?", "Demora quanto?", "Preciso sair", "Responde!",
        "Tá aí?", "Oi?", "Vou ter que ir", "Flw", "Valeu"
    ],
    "detalhista": [
        "Boa noite", "Preciso de todas as informações",
        "Quais são todos os planos?", "Preços de cada um?",
        "O que vem em cada plano?", "Diferenças entre eles?",
        "Quantos produtos exatamente?", "Em quantas categorias?",
        "Quantos fornecedores?", "De quais estados?",
        "Prazo médio de entrega?", "Política de troca?",
        "E de devolução?", "Como funciona o estorno?",
        "Posso vender em marketplaces?", "Quais exatamente?",
        "Tem integração automática?", "Preciso fazer manual?",
        "Meu nome é {nome}", "Suporte funciona que horas?",
        "Tem SLA de atendimento?", "Respondem em quanto tempo?",
        "Ok, anotei tudo", "Vou analisar", "Obrigada!"
    ]
}

class TestadorContexto:
    def __init__(self):
        self.resultados = []
        self.erros = []
        self.contexto_perdido = []

    def limpar_banco_teste(self):
        """Limpa dados de teste anteriores"""
        print("\n🧹 Limpando dados de teste anteriores...")
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            # Pegar IDs dos usuários de teste
            phones = [u["phone"] for u in USUARIOS]
            phones_str = "', '".join(phones)

            cur.execute(f"""
                DELETE FROM conversation_history
                WHERE customer_id IN (
                    SELECT id FROM customers WHERE phone IN ('{phones_str}')
                )
            """)

            cur.execute(f"""
                DELETE FROM sessions
                WHERE customer_id IN (
                    SELECT id FROM customers WHERE phone IN ('{phones_str}')
                )
            """)

            cur.execute(f"DELETE FROM customers WHERE phone IN ('{phones_str}')")

            conn.commit()
            conn.close()
            print("✅ Banco limpo!")

        except Exception as e:
            print(f"⚠️ Erro ao limpar banco: {e}")

    def criar_usuario_no_banco(self, usuario):
        """Cria usuário no banco antes do teste"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("""
                INSERT INTO customers (name, phone, email, created_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (phone) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
            """, (usuario["nome"], usuario["phone"], f"{usuario['phone']}@spdrop.com"))

            result = cur.fetchone()
            conn.commit()
            conn.close()

            return result['id'] if result else None

        except Exception as e:
            print(f"❌ Erro ao criar usuário {usuario['nome']}: {e}")
            return None

    def enviar_mensagem(self, phone, mensagem, delay=0.5):
        """Envia mensagem via webhook"""
        payload = {
            "from": f"{phone}@lid",
            "body": mensagem,
            "timestamp": int(time.time()),
            "hasMedia": False,
            "type": "chat"
        }

        try:
            response = requests.post(BOT_WEBHOOK_URL, json=payload, timeout=30)
            time.sleep(delay)  # Delay entre mensagens
            return response.status_code == 200
        except Exception as e:
            self.erros.append({
                "phone": phone,
                "mensagem": mensagem,
                "erro": str(e)
            })
            return False

    def verificar_contexto(self, customer_id, phone):
        """Verifica se o contexto foi mantido"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Contar mensagens salvas
            cur.execute("""
                SELECT COUNT(*) as total
                FROM conversation_history
                WHERE customer_id = %s
            """, (customer_id,))

            result = cur.fetchone()
            total_mensagens = result['total'] if result else 0

            # Pegar últimas mensagens
            cur.execute("""
                SELECT user_message, agent_response, timestamp
                FROM conversation_history
                WHERE customer_id = %s
                ORDER BY timestamp DESC
                LIMIT 5
            """, (customer_id,))

            ultimas = cur.fetchall()

            conn.close()

            return {
                "customer_id": customer_id,
                "phone": phone,
                "total_mensagens": total_mensagens,
                "ultimas_mensagens": ultimas
            }

        except Exception as e:
            print(f"❌ Erro ao verificar contexto para {phone}: {e}")
            return None

    def testar_usuario(self, usuario, numero_usuario):
        """Testa um usuário completo"""
        print(f"\n{'='*60}")
        print(f"👤 Testando Usuário {numero_usuario}/10: {usuario['nome']}")
        print(f"📱 Telefone: {usuario['phone']}")
        print(f"🎯 Perfil: {usuario['perfil']}")
        print(f"{'='*60}")

        # Criar usuário no banco
        customer_id = self.criar_usuario_no_banco(usuario)
        if not customer_id:
            print(f"❌ Falha ao criar usuário no banco")
            return

        print(f"✅ Usuário criado no banco (ID: {customer_id})")

        # Pegar fluxo de mensagens
        fluxo = FLUXOS[usuario["perfil"]]
        total_mensagens = len(fluxo)

        print(f"📨 Enviando {total_mensagens} mensagens...\n")

        mensagens_enviadas = 0
        for i, mensagem_template in enumerate(fluxo, 1):
            # Substituir variáveis
            mensagem = mensagem_template.replace("{nome}", usuario["nome"])

            print(f"  [{i}/{total_mensagens}] {usuario['nome']}: {mensagem[:50]}...")

            if self.enviar_mensagem(usuario["phone"], mensagem, delay=1.0):
                mensagens_enviadas += 1
            else:
                print(f"    ❌ Falha ao enviar")

        print(f"\n✅ {mensagens_enviadas}/{total_mensagens} mensagens enviadas")

        # Aguardar processamento final
        print("⏳ Aguardando processamento final (10s)...")
        time.sleep(10)

        # Verificar contexto
        print("🔍 Verificando contexto...")
        contexto = self.verificar_contexto(customer_id, usuario["phone"])

        if contexto:
            print(f"📊 Total de conversas salvas: {contexto['total_mensagens']}")

            if contexto['total_mensagens'] < mensagens_enviadas * 0.8:
                print(f"⚠️ POSSÍVEL PERDA DE CONTEXTO! Esperado ~{mensagens_enviadas}, salvou {contexto['total_mensagens']}")
                self.contexto_perdido.append({
                    "usuario": usuario["nome"],
                    "esperado": mensagens_enviadas,
                    "salvo": contexto['total_mensagens']
                })
            else:
                print(f"✅ Contexto mantido corretamente!")

            self.resultados.append(contexto)

    def testar_todos_usuarios(self):
        """Testa todos os 10 usuários"""
        print("\n" + "="*60)
        print("🚀 INICIANDO TESTE DE CONTEXTO - 10 USUÁRIOS")
        print("="*60)
        print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👥 Total de usuários: {len(USUARIOS)}")
        print(f"💬 Mensagens por usuário: 25")
        print(f"📨 Total de mensagens: {len(USUARIOS) * 25}")
        print("="*60)

        # Limpar dados antigos
        self.limpar_banco_teste()

        # Testar cada usuário
        for i, usuario in enumerate(USUARIOS, 1):
            self.testar_usuario(usuario, i)

            # Delay entre usuários (exceto o último)
            if i < len(USUARIOS):
                print(f"\n⏸️ Aguardando 5s antes do próximo usuário...")
                time.sleep(5)

        # Relatório final
        self.gerar_relatorio()

    def gerar_relatorio(self):
        """Gera relatório final do teste"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL DO TESTE")
        print("="*60)

        total_usuarios = len(self.resultados)
        total_erros = len(self.erros)
        total_perda_contexto = len(self.contexto_perdido)

        print(f"\n✅ Usuários testados: {total_usuarios}/10")
        print(f"❌ Erros de envio: {total_erros}")
        print(f"⚠️ Perda de contexto: {total_perda_contexto}")

        if self.contexto_perdido:
            print("\n⚠️ USUÁRIOS COM PERDA DE CONTEXTO:")
            for item in self.contexto_perdido:
                print(f"  - {item['usuario']}: esperado ~{item['esperado']}, salvou {item['salvo']}")

        if self.erros:
            print(f"\n❌ ERROS ENCONTRADOS ({len(self.erros)}):")
            for erro in self.erros[:10]:  # Mostrar primeiros 10
                print(f"  - {erro['phone']}: {erro['erro']}")

        # Estatísticas
        if self.resultados:
            total_msgs = sum(r['total_mensagens'] for r in self.resultados)
            media_msgs = total_msgs / len(self.resultados)

            print(f"\n📈 ESTATÍSTICAS:")
            print(f"  Total de conversas salvas: {total_msgs}")
            print(f"  Média por usuário: {media_msgs:.1f}")
            print(f"  Taxa de sucesso: {((total_usuarios - total_perda_contexto) / total_usuarios * 100):.1f}%")

        print("\n" + "="*60)

        if total_perda_contexto == 0 and total_erros == 0:
            print("🎉 TESTE PASSOU! Contexto mantido para todos os usuários!")
        elif total_perda_contexto > 0:
            print("⚠️ ATENÇÃO! Alguns usuários perderam contexto!")
        else:
            print("❌ TESTE FALHOU! Houve erros durante o teste!")

        print("="*60)

if __name__ == "__main__":
    testador = TestadorContexto()
    testador.testar_todos_usuarios()
