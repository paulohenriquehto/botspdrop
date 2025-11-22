"""
Teste de Contexto: 10 Usuários com 25 Mensagens Cada
Verifica se a Gabi mantém o contexto da conversa
"""

import asyncio
import httpx
import time
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuração
BOT_WEBHOOK = "http://localhost:5000/webhook"

# 10 Usuários com conversas realistas
USUARIOS = [
    {
        "nome": "Carlos Silva",
        "phone": "5511987654321",
        "conversas": [
            "Oi, boa noite!",
            "Quero saber sobre dropshipping",
            "Nunca trabalhei com isso",
            "É complicado começar?",
            "Preciso de estoque?",
            "Quanto investir no início?",
            "Tem curso incluso?",
            "Quais são os planos?",
            "O semestral é melhor?",
            "Posso pagar no boleto?",
            "Tem desconto pra anual?",
            "Vocês têm suporte?",
            "Funciona 24 horas?",
            "Posso testar antes?",
            "Quanto tempo de teste?",
            "Preciso de cartão pro teste?",
            "Meu CPF é 111.222.333-44",
            "Meu email é carlos@teste.com",
            "Quando libera o acesso?",
            "Vou receber por email?",
            "Tem app mobile?",
            "Funciona no celular?",
            "Quantos produtos tem?",
            "Obrigado pela ajuda!",
            "Vou começar o teste hoje"
        ]
    },
    {
        "nome": "Maria Santos",
        "phone": "5521987654321",
        "conversas": [
            "Olá!",
            "Vi sobre vocês no Instagram",
            "Sou iniciante total",
            "Tenho 2 horas por dia",
            "Dá pra trabalhar de casa?",
            "Qual o plano mais barato?",
            "69 reais no mês?",
            "Esse valor é único?",
            "Tem taxa de entrega?",
            "Os fornecedores são confiáveis?",
            "Já tive problema com outra plataforma",
            "Vocês entregam rápido?",
            "Qual o prazo médio?",
            "E se o cliente reclamar?",
            "Vocês dão suporte nisso?",
            "Posso vender no Facebook?",
            "E no Mercado Livre?",
            "Precisa de CNPJ?",
            "Posso como MEI?",
            "Tem integração automática?",
            "Vou testar então",
            "Como faço?",
            "Precisa do CPF?",
            "É 222.333.444-55",
            "Email: maria@teste.com"
        ]
    },
    {
        "nome": "João Pedro",
        "phone": "5531987654321",
        "conversas": [
            "Fala!",
            "Quanto custa pra começar?",
            "Tô desempregado",
            "Preciso ganhar urgente",
            "Dá pra fazer 5 mil no mês?",
            "Em quanto tempo?",
            "Tem gente que consegue?",
            "Qual o segredo?",
            "Preciso investir em anúncio?",
            "Quanto de verba?",
            "Não tenho muito dinheiro",
            "O plano mensal serve?",
            "Posso cancelar depois?",
            "Tem multa?",
            "Vou experimentar",
            "Mas tenho medo de não dar certo",
            "E se não vender nada?",
            "Perco o dinheiro?",
            "Vocês garantem vendas?",
            "Entendo, depende de mim",
            "Tá, vou tentar",
            "Como começo o teste?",
            "CPF: 333.444.555-66",
            "Email: joao@teste.com",
            "Valeu!"
        ]
    },
    {
        "nome": "Ana Paula",
        "phone": "5541987654321",
        "conversas": [
            "Oi Gabi!",
            "Meu marido me indicou vocês",
            "Ele disse que é bom",
            "Trabalho meio período",
            "Tenho 3 filhos",
            "Preciso de renda extra",
            "Mas não posso sair de casa",
            "Dropshipping é pra mim?",
            "Consigo conciliar?",
            "E se precisar durante o dia?",
            "Dá pra pausar?",
            "Quanto tempo leva pra aprender?",
            "Sou meio lerda com tecnologia",
            "É difícil mexer?",
            "Tem tutorial?",
            "Vocês ensinam tudo?",
            "Que legal!",
            "Vou querer o semestral",
            "Assim tenho tempo de aprender",
            "Mas antes quero testar",
            "Pode ser?",
            "Meu CPF: 444.555.666-77",
            "Email: ana@teste.com",
            "Espero conseguir!",
            "Obrigada pelo carinho"
        ]
    },
    {
        "nome": "Pedro Alves",
        "phone": "5551987654321",
        "conversas": [
            "E aí!",
            "Quero dropshipping",
            "Já vendo no Instagram",
            "Mas quero escalar",
            "Vocês têm API?",
            "Integra com Shopify?",
            "E com WooCommerce?",
            "Preciso de automação",
            "Quantos pedidos por dia aguenta?",
            "Tem limite?",
            "E os fornecedores?",
            "Entregam rápido?",
            "Qual o SLA?",
            "Tem rastreio?",
            "E nota fiscal?",
            "Tudo certinho né?",
            "Beleza",
            "Vou precisar do plano anual",
            "Volume alto",
            "Desconto pra quem vende muito?",
            "Entendi",
            "Bora testar então",
            "CPF: 555.666.777-88",
            "Email: pedro@teste.com",
            "Vamos nessa!"
        ]
    },
    {
        "nome": "Juliana Costa",
        "phone": "5561987654321",
        "conversas": [
            "Olá, tudo bem?",
            "Estou interessada",
            "Mas tenho algumas dúvidas",
            "Vocês são empresa registrada?",
            "Tem CNPJ?",
            "Quanto tempo de mercado?",
            "Isso é importante pra mim",
            "Já fui enganada antes",
            "Preciso de garantias",
            "Vocês têm contrato?",
            "Posso ler antes?",
            "E a política de cancelamento?",
            "Tem reembolso?",
            "Em quanto tempo?",
            "Ok, me sinto mais segura",
            "Os produtos têm garantia?",
            "E se vier com defeito?",
            "Quem resolve?",
            "Entendi, vocês ajudam",
            "Então vou fazer o teste",
            "Quero ver como funciona",
            "CPF: 666.777.888-99",
            "Email: juliana@teste.com",
            "Aguardo o acesso",
            "Obrigada!"
        ]
    },
    {
        "nome": "Ricardo Mendes",
        "phone": "5571987654321",
        "conversas": [
            "Opa!",
            "Dropshipping dá grana mesmo?",
            "Conheço gente que fatura alto",
            "Mas também vi gente que perdeu",
            "Qual a real?",
            "Vocês são honestos nisso?",
            "Aprecio a sinceridade",
            "Então depende de mim",
            "Quanto tempo dedicar?",
            "4 horas por dia dá?",
            "Tenho outro trabalho",
            "Mas quero sair dele",
            "Quanto preciso faturar?",
            "Pra substituir o salário",
            "Em média 8 mil",
            "É possível?",
            "Vou me esforçar então",
            "Qual plano recomenda?",
            "Semestral é suficiente?",
            "Ou preciso de mais tempo?",
            "Vou de semestral",
            "Mas testa antes né",
            "CPF: 777.888.999-00",
            "Email: ricardo@teste.com",
            "Vamos ver no que dá"
        ]
    },
    {
        "nome": "Fernanda Lima",
        "phone": "5581987654321",
        "conversas": [
            "Oi querida!",
            "Adoro o nome Gabi",
            "Minha filha se chama assim",
            "Bom, vim saber sobre vocês",
            "Estou desempregada há 6 meses",
            "Tá difícil achar emprego",
            "Tenho 45 anos",
            "As empresas não querem",
            "Pensei em empreender",
            "Mas não sei por onde começar",
            "Vocês ajudam nisso?",
            "Que bom!",
            "Não entendo nada de internet",
            "Mal sei usar WhatsApp",
            "Consigo mesmo assim?",
            "Vocês são pacientes?",
            "Preciso de muito suporte",
            "Ok, vou tentar",
            "Qual o mais barato?",
            "69 reais?",
            "Dá pra pagar",
            "Vou fazer o teste",
            "CPF: 888.999.000-11",
            "Email: fernanda@teste.com",
            "Torce por mim!"
        ]
    },
    {
        "nome": "Lucas Oliveira",
        "phone": "5591987654321",
        "conversas": [
            "Salve!",
            "Meu primo usa vocês",
            "Ele tá faturando bem",
            "Falou que é top",
            "Quero entrar também",
            "Ele faz quanto?",
            "Uns 15 mil por mês",
            "Caraca, dá nisso?",
            "Quanto tempo levou?",
            "8 meses?",
            "Dá pra acelerar?",
            "Quero em 3 meses",
            "Sou determinado",
            "Vou meter 8 horas por dia",
            "Qual plano ele tem?",
            "Anual né",
            "Vou direto nesse",
            "Sem enrolação",
            "Quanto tá?",
            "897?",
            "Fechou",
            "Mas testa 7 dias antes",
            "CPF: 999.000.111-22",
            "Email: lucas@teste.com",
            "Bora faturar!"
        ]
    },
    {
        "nome": "Patrícia Rocha",
        "phone": "5502987654321",
        "conversas": [
            "Boa noite!",
            "Vi um anúncio de vocês",
            "Promete muito",
            "É verdade mesmo?",
            "Não é pegadinha?",
            "Desculpa a desconfiança",
            "Mas internet tá cheio de golpe",
            "Vocês são sérios?",
            "Que bom",
            "Então vou arriscar",
            "Trabalho em loja",
            "Ganho pouco",
            "Preciso complementar",
            "Umas 2 mil a mais já ajuda",
            "Consigo isso?",
            "Ótimo!",
            "Que plano vocês indicam?",
            "Pra quem quer começar devagar",
            "Mensal então",
            "Se der certo eu renovo",
            "Posso fazer teste?",
            "Maravilha",
            "CPF: 000.111.222-33",
            "Email: patricia@teste.com",
            "Vamos começar!"
        ]
    }
]

class TesteContexto:
    def __init__(self):
        self.resultados = []
        self.erros = []

    def conectar_db(self):
        """Conecta ao banco de dados"""
        return psycopg2.connect(
            host="localhost",
            port=5432,
            database="spdrop_db",
            user="spdrop_user",
            password="spdrop_password"
        )

    def criar_usuario_db(self, usuario_data):
        """Cria usuário no banco se não existir"""
        conn = self.conectar_db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar se já existe
                cur.execute("SELECT id FROM customers WHERE phone = %s", (usuario_data["phone"],))
                existing = cur.fetchone()

                if existing:
                    print(f"✓ Usuário {usuario_data['nome']} já existe (ID: {existing['id']})")
                    return existing['id']

                # Criar novo
                cur.execute("""
                    INSERT INTO customers (name, phone, email, created_at)
                    VALUES (%s, %s, %s, NOW())
                    RETURNING id
                """, (usuario_data["nome"], usuario_data["phone"], f"{usuario_data['phone']}@spdrop.com"))
                conn.commit()
                customer_id = cur.fetchone()['id']
                print(f"✓ Usuário {usuario_data['nome']} criado (ID: {customer_id})")
                return customer_id
        finally:
            conn.close()

    async def enviar_mensagem(self, phone, mensagem, index, total):
        """Envia uma mensagem para o bot"""
        payload = {
            "from": f"{phone}@c.us",
            "body": mensagem,
            "timestamp": int(time.time()),
            "hasMedia": False,
            "type": "chat"
        }

        print(f"  [{index+1}/{total}] Enviando: {mensagem[:50]}...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(BOT_WEBHOOK, json=payload)

                if response.status_code == 200:
                    print(f"  ✓ Resposta recebida")
                    return True
                else:
                    print(f"  ✗ Erro: {response.status_code}")
                    self.erros.append({
                        "phone": phone,
                        "mensagem": mensagem,
                        "erro": f"HTTP {response.status_code}"
                    })
                    return False
        except Exception as e:
            print(f"  ✗ Erro: {str(e)}")
            self.erros.append({
                "phone": phone,
                "mensagem": mensagem,
                "erro": str(e)
            })
            return False

    def verificar_contexto(self, customer_id, total_mensagens):
        """Verifica se o contexto foi mantido no histórico"""
        conn = self.conectar_db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT COUNT(*) as total
                    FROM conversation_history
                    WHERE customer_id = %s
                """, (customer_id,))

                result = cur.fetchone()
                mensagens_salvas = result['total']

                # Verificar se há pelo menos metade das mensagens salvas
                esperado = total_mensagens * 0.5

                if mensagens_salvas >= esperado:
                    print(f"  ✓ Contexto OK: {mensagens_salvas} mensagens salvas")
                    return True
                else:
                    print(f"  ✗ Contexto PERDIDO: apenas {mensagens_salvas} de {total_mensagens} esperadas")
                    return False
        finally:
            conn.close()

    def analisar_perda_contexto(self, customer_id):
        """Analisa se houve perda de contexto (respostas repetitivas)"""
        conn = self.conectar_db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT agent_response
                    FROM conversation_history
                    WHERE customer_id = %s
                    ORDER BY timestamp DESC
                    LIMIT 10
                """, (customer_id,))

                respostas = [row['agent_response'] for row in cur.fetchall()]

                # Verificar se a mesma resposta aparece mais de 3 vezes
                pergunta_padrao = "Você já é assinante da SPDrop ou quer conhecer a plataforma?"

                count = sum(1 for r in respostas if pergunta_padrao in r)

                if count > 3:
                    print(f"  ⚠️  ALERTA: Pergunta padrão repetida {count} vezes!")
                    return False

                return True
        finally:
            conn.close()

    async def testar_usuario(self, usuario):
        """Testa um usuário completo"""
        print(f"\n{'='*80}")
        print(f"🧪 TESTANDO: {usuario['nome']} ({usuario['phone']})")
        print(f"{'='*80}")

        # Criar usuário no banco
        customer_id = self.criar_usuario_db(usuario)

        # Enviar todas as mensagens
        total = len(usuario['conversas'])
        sucesso = 0

        for i, mensagem in enumerate(usuario['conversas']):
            if await self.enviar_mensagem(usuario['phone'], mensagem, i, total):
                sucesso += 1

            # Aguardar entre mensagens (buffer de 13s + processamento)
            if i < total - 1:  # Não aguardar após última mensagem
                await asyncio.sleep(15)  # 13s buffer + 2s processamento

        # Aguardar processamento final
        await asyncio.sleep(10)

        # Verificar contexto
        print(f"\n📊 VERIFICANDO CONTEXTO...")
        contexto_ok = self.verificar_contexto(customer_id, total)
        sem_repeticao = self.analisar_perda_contexto(customer_id)

        resultado = {
            "usuario": usuario['nome'],
            "phone": usuario['phone'],
            "mensagens_enviadas": sucesso,
            "mensagens_total": total,
            "contexto_mantido": contexto_ok,
            "sem_repeticao": sem_repeticao,
            "sucesso": contexto_ok and sem_repeticao
        }

        self.resultados.append(resultado)

        if resultado['sucesso']:
            print(f"\n✅ SUCESSO: {usuario['nome']} - Contexto mantido!")
        else:
            print(f"\n❌ FALHA: {usuario['nome']} - Problema no contexto!")

        return resultado

    async def executar_teste(self):
        """Executa teste para todos os usuários"""
        print("\n" + "="*80)
        print("🚀 INICIANDO TESTE DE CONTEXTO - 10 USUÁRIOS x 25 MENSAGENS")
        print("="*80)

        inicio = datetime.now()

        # Testar cada usuário sequencialmente
        for usuario in USUARIOS:
            await self.testar_usuario(usuario)

        fim = datetime.now()
        duracao = (fim - inicio).total_seconds()

        # Relatório final
        self.gerar_relatorio(duracao)

    def gerar_relatorio(self, duracao):
        """Gera relatório final do teste"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO FINAL DO TESTE")
        print("="*80)

        total_usuarios = len(self.resultados)
        sucesso = sum(1 for r in self.resultados if r['sucesso'])
        falhas = total_usuarios - sucesso

        print(f"\n⏱️  Duração total: {duracao:.0f}s ({duracao/60:.1f} min)")
        print(f"👥 Total de usuários: {total_usuarios}")
        print(f"✅ Sucessos: {sucesso}")
        print(f"❌ Falhas: {falhas}")
        print(f"📈 Taxa de sucesso: {(sucesso/total_usuarios)*100:.1f}%")

        print(f"\n📝 DETALHES POR USUÁRIO:")
        print("-" * 80)

        for r in self.resultados:
            status = "✅" if r['sucesso'] else "❌"
            print(f"{status} {r['usuario']:20} | Msgs: {r['mensagens_enviadas']}/{r['mensagens_total']} | "
                  f"Contexto: {'OK' if r['contexto_mantido'] else 'PERDIDO'} | "
                  f"Repetição: {'NÃO' if r['sem_repeticao'] else 'SIM'}")

        if self.erros:
            print(f"\n⚠️  ERROS ENCONTRADOS: {len(self.erros)}")
            for erro in self.erros[:10]:  # Mostrar até 10 erros
                print(f"  • {erro['phone']}: {erro['erro']}")

        print("\n" + "="*80)

        if falhas == 0:
            print("🎉 TESTE 100% APROVADO! Contexto mantido em todas as conversas!")
        else:
            print(f"⚠️  ATENÇÃO: {falhas} conversas com perda de contexto!")

        print("="*80 + "\n")

async def main():
    teste = TesteContexto()
    await teste.executar_teste()

if __name__ == "__main__":
    asyncio.run(main())
