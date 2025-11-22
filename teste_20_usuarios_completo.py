#!/usr/bin/env python3
"""
Teste Completo: 20 Usuários de Tráfego Pago (Leads Frios)
Simula conversas reais do início ao fim - com fechamento ou não
"""

import requests
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import sys

BOT_WEBHOOK_URL = "http://localhost:5000/webhook"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "spdrop_db",
    "user": "spdrop_user",
    "password": "spdrop_password"
}

# 20 PERFIS VARIADOS DE LEADS FRIOS
USUARIOS = [
    # INICIANTES
    {
        "id": 1,
        "nome": "Juliana Silva",
        "phone": "5511988001001",
        "perfil": "Mãe Iniciante",
        "idade": 32,
        "situacao": "Desempregada, quer renda extra em casa",
        "nivel": "Iniciante total - nunca vendeu online",
        "fluxo": [
            "Oi, vi o anúncio de vocês no Facebook",
            "Nunca vendi nada online, é muito difícil?",
            "Quanto preciso investir pra começar?",
            "Tenho medo de não conseguir vender nada",
            "Como funciona isso de dropshipping?",
            "Preciso ter dinheiro pra comprar estoque?",
            "Quanto tempo demora pra ter o primeiro resultado?",
            "Tá, mas vocês dão suporte se eu travar em algo?",
            "E se eu não souber usar a plataforma?",
            "Vou pensar melhor e volto"
        ]
    },
    {
        "id": 2,
        "nome": "Carlos Eduardo",
        "phone": "5521987002002",
        "perfil": "CLT buscando renda extra",
        "idade": 28,
        "situacao": "Trabalha 8h/dia, quer ganhar mais",
        "nivel": "Iniciante - conhece Mercado Livre como comprador",
        "fluxo": [
            "E aí, quanto custa pra começar?",
            "Trabalho o dia todo, dá pra fazer nas horas vagas?",
            "Quanto vou ganhar por mês?",
            "É garantido que vou vender?",
            "Tipo, eu só anuncio e vocês enviam? É isso?",
            "Mas e se o cliente reclamar?",
            "Vocês resolvem problemas de entrega?",
            "Hmm, deixa eu ver se tenho grana pra assinar",
            "69 reais tá caro não? Tem desconto?",
            "Bom, vou testar o plano mensal então"
        ]
    },
    {
        "id": 3,
        "nome": "Rafaela Costa",
        "phone": "5531986003003",
        "perfil": "Estudante de 19 anos",
        "idade": 19,
        "situacao": "Faculdade, sem renda, pais ajudam",
        "nivel": "Iniciante mas conhece redes sociais",
        "fluxo": [
            "oii vim pelo insta",
            "vcs vendem oq?",
            "aah entendi, tipo eu vendo mas sem ter produto",
            "isso é de boa? legal né",
            "mas tipo, preciso pagar quanto?",
            "69 reais?? nossaa",
            "e tem como testar gratis?",
            "sério? quanto tempo?",
            "pode crer, quero testar sim",
            "Rafaela Costa, CPF 111.222.333-44, email rafa@gmail.com, tel 31 98600-3003"
        ]
    },

    # NÍVEL MÉDIO
    {
        "id": 4,
        "nome": "Roberto Almeida",
        "phone": "5541985004004",
        "perfil": "Ex-lojista físico",
        "idade": 45,
        "situacao": "Fechou loja física, quer ir pro online",
        "nivel": "Médio - entende de vendas mas não de online",
        "fluxo": [
            "Boa tarde, já tive loja física de roupas",
            "Fechei por causa da crise, quero voltar online",
            "Vocês têm roupas no catálogo?",
            "E o preço é competitivo?",
            "No físico eu comprava com 50% de margem",
            "E aí, quanto fica de lucro no dropshipping?",
            "Margem de 20-30%? Não é pouco não?",
            "Mas não tenho custo de aluguel né, faz sentido",
            "Integra com quais plataformas?",
            "Shopee, Mercado Livre... ótimo",
            "Quanto é o investimento inicial?",
            "Pode parcelar?",
            "Tá bom, vou pegar o semestral, menos de 75/mês vale",
            "Como faço pra assinar?"
        ]
    },
    {
        "id": 5,
        "nome": "Patrícia Mendes",
        "phone": "5561984005005",
        "perfil": "Revendedora de cosméticos",
        "idade": 38,
        "situacao": "Revende Avon/Natura, quer escalar",
        "nivel": "Médio - vende mas quer automatizar",
        "fluxo": [
            "Olá! Revendo cosméticos mas é muito trabalho manual",
            "Ouvi falar de dropshipping, funciona pra cosméticos?",
            "Ah, vocês têm vários nichos então",
            "Quais produtos vendem mais?",
            "Interessante... e eu preciso fazer o que exatamente?",
            "Só anunciar? Vocês cuidam do resto?",
            "Nossa, parece bom demais pra ser verdade rsrs",
            "Qual a pegadinha? haha",
            "Entendi, o risco é não vender né",
            "Mas dá pra testar sem gastar muito?",
            "447 por 6 meses... 74 por mês tá ok",
            "Tem garantia ou algo assim?",
            "Beleza, vou fechar o semestral"
        ]
    },
    {
        "id": 6,
        "nome": "Thiago Santos",
        "phone": "5571983006006",
        "perfil": "Influencer pequeno (5k seguidores)",
        "idade": 24,
        "situacao": "Monetiza com publi, quer vender produtos",
        "nivel": "Médio - conhece marketing digital",
        "fluxo": [
            "Fala! Tenho 5k no insta, quero monetizar melhor",
            "Dropshipping dá pra linkar com perfil do insta?",
            "Tipo, anuncio nos stories e direciono pra loja?",
            "Maneiro, tem integração automática?",
            "E os produtos são de qualidade? Minha audiência é exigente",
            "Fornecedores confiáveis é essencial",
            "Vocês têm cases de sucesso?",
            "Legal, quanto custa?",
            "Tem plano anual? Vou entrar firme nisso",
            "897 no anual, menos de 75/mês... fechou",
            "Manda o link de pagamento"
        ]
    },

    # AVANÇADOS
    {
        "id": 7,
        "nome": "Fernando Ribeiro",
        "phone": "5581982007007",
        "perfil": "Já vendeu em marketplace",
        "idade": 35,
        "situacao": "Vende no ML, quer dropshipping pra escalar",
        "nivel": "Avançado - conhece operação de e-commerce",
        "fluxo": [
            "Opa, já vendo no Mercado Livre há 2 anos",
            "Compro estoque mas tá ficando caro o capital parado",
            "Vocês têm produtos com envio rápido?",
            "Full no ML exige entrega rápida",
            "Quantos fornecedores vocês têm?",
            "API pra integração automática tem?",
            "Preciso de webhook pra atualizar pedidos",
            "E o SLA de envio, qual a média?",
            "Rastreio é fornecido automaticamente?",
            "Certo, me interessou. Qual plano recomendam?",
            "Anual né, mais barato e já vou usar pesado",
            "Tem nota fiscal dos produtos?",
            "Perfeito, vou assinar agora"
        ]
    },
    {
        "id": 8,
        "nome": "Amanda Oliveira",
        "phone": "5511981008008",
        "perfil": "Empreendedora serial",
        "idade": 30,
        "situacao": "Tem 3 negócios online, quer adicionar dropshipping",
        "nivel": "Avançado - conhece o mercado",
        "fluxo": [
            "Oi, já trabalho com infoprodutos e afiliados",
            "Quero adicionar produtos físicos via dropshipping",
            "Quanto de margem média consigo?",
            "20-30% é ok se o volume compensar",
            "Ticket médio dos produtos qual é?",
            "Entre 50-200 reais? Bom pra escalar",
            "E taxa de conversão média de quem usa?",
            "Entendo, depende do tráfego né",
            "Posso rodar ads direcionando pra produtos específicos?",
            "Ótimo, vou precisar disso",
            "Qual o plano mais vantajoso?",
            "Anual com 45% off, show. Quero esse",
            "Aceita cartão? Parcela?"
        ]
    },

    # OBJEÇÕES FORTES
    {
        "id": 9,
        "nome": "Paulo Henrique",
        "phone": "5521980009009",
        "perfil": "Cético e desconfiado",
        "idade": 42,
        "situacao": "Já foi enganado em pirâmide",
        "nivel": "Médio mas desconfiado",
        "fluxo": [
            "Isso não é pirâmide financeira não né?",
            "Já perdi dinheiro com esquema online",
            "Como eu sei que é sério?",
            "Todo mundo fala que ganha dinheiro mas ninguém mostra prova",
            "Vocês têm CNPJ? São regularizados?",
            "E se eu pagar e não funcionar?",
            "Não tem garantia de devolução?",
            "Então o risco é todo meu?",
            "Complicado hein...",
            "Deixa eu pesquisar mais sobre vocês",
            "Vou ver avaliações no Reclame Aqui",
            "Se tiver reviews bons eu volto"
        ]
    },
    {
        "id": 10,
        "nome": "Mariana Souza",
        "phone": "5531979010010",
        "perfil": "Sem dinheiro disponível",
        "idade": 27,
        "situacao": "Desempregada, orçamento apertado",
        "nivel": "Iniciante com restrição financeira",
        "fluxo": [
            "Oi, tô desempregada e preciso de renda urgente",
            "Quanto custa?",
            "69 reais tá muito caro pra mim agora",
            "Não tenho nem pra comer direito",
            "Não tem mais barato?",
            "Ou de graça pra começar?",
            "7 dias grátis? Mas depois tenho que pagar?",
            "E se em 7 dias eu não vender nada?",
            "Vou ficar sem os 69 reais",
            "Melhor não arriscar agora",
            "Quando eu arrumar um emprego eu volto"
        ]
    },

    # MAIS PERFIS VARIADOS
    {
        "id": 11,
        "nome": "Gabriela Lima",
        "phone": "5541978011011",
        "perfil": "Mãe de 3 filhos",
        "idade": 35,
        "situacao": "Tempo limitado, precisa trabalhar em casa",
        "nivel": "Iniciante",
        "fluxo": [
            "Tenho 3 filhos pequenos, não posso sair pra trabalhar",
            "Vi que dá pra ganhar dinheiro de casa, é verdade?",
            "Quantas horas por dia preciso dedicar?",
            "2-3 horas dá? É o tempo que eles dormem",
            "E é complicado? Não entendo muito de internet",
            "Preciso de computador ou dá no celular?",
            "Ah, no celular mesmo já dá? Que bom!",
            "Quanto vou ganhar fazendo 2-3h por dia?",
            "Varia né, depende das vendas",
            "Certo... e se eu começar devagar?",
            "Acho que vale tentar, quanto é mesmo?",
            "Posso pagar com cartão parcelado?",
            "Não parcela? Então só no mês que vem consigo"
        ]
    },
    {
        "id": 12,
        "nome": "Lucas Martins",
        "phone": "5561977012012",
        "perfil": "Adolescente de 17 anos",
        "idade": 17,
        "situacao": "Quer comprar um PC gamer",
        "nivel": "Iniciante - muito jovem",
        "fluxo": [
            "eai mano",
            "queria ganhar uma grana pra comprar um pc gamer",
            "qnt eu consigo tirar vendendo?",
            "tipo uns 2k por mes da?",
            "serio? como faz?",
            "precisa pagar pra usar?",
            "poha 69 conto é caro dmais",
            "mano n tenho isso nao",
            "meus pais n vao dar",
            "tem algum jeito de ganhar sem pagar?",
            "tipo fazer divulgaçao sei la",
            "hmm saquei",
            "valeu entao flw"
        ]
    },
    {
        "id": 13,
        "nome": "Sandra Regina",
        "phone": "5581976013013",
        "perfil": "Aposentada que quer se manter ativa",
        "idade": 62,
        "situacao": "Aposentada, quer ocupação e renda extra",
        "nivel": "Iniciante - pouca familiaridade com tecnologia",
        "fluxo": [
            "Boa tarde, minha neta me mostrou esse anúncio",
            "Sou aposentada mas quero me manter ativa",
            "Será que consigo aprender? Tenho 62 anos",
            "Não sou muito boa com essas tecnologias",
            "Precisa saber mexer muito no computador?",
            "Tenho medo de errar e perder dinheiro",
            "Vocês têm paciência de ensinar pessoa mais velha?",
            "Tem vídeos explicativos bem detalhados?",
            "Posso ligar se tiver dúvida?",
            "Ah, tem WhatsApp de suporte, que bom!",
            "Vou tentar sim, afinal tenho tempo livre",
            "Como faço pra começar?",
            "Preciso pagar como?"
        ]
    },
    {
        "id": 14,
        "nome": "Diego Ferreira",
        "phone": "5521975014014",
        "perfil": "Comparador de preços",
        "idade": 29,
        "situacao": "Quer o melhor custo-benefício",
        "nivel": "Médio",
        "fluxo": [
            "Olá, estou pesquisando plataformas de dropshipping",
            "Já cotei com 3 concorrentes de vocês",
            "O que vocês têm de diferente?",
            "Preço é importante mas não é tudo",
            "Concorrente X cobra 49 reais, vocês 69",
            "Por que pagar mais caro?",
            "Hmm, integração melhor e mais fornecedores...",
            "Quantos fornecedores a mais?",
            "E o suporte responde rápido?",
            "Porque no concorrente demora dias",
            "Entendi, vocês parecem mais estruturados",
            "Mas o preço continua sendo um empecilho",
            "Não rola um desconto pra fechar agora?",
            "Promoção Black Friday... tá, vou aproveitar então"
        ]
    },
    {
        "id": 15,
        "nome": "Beatriz Alves",
        "phone": "5531974015015",
        "perfil": "Professora querendo renda passiva",
        "idade": 40,
        "situacao": "Trabalha muito e ganha pouco",
        "nivel": "Iniciante",
        "fluxo": [
            "Sou professora e trabalho demais",
            "Quero criar uma renda passiva",
            "Dropshipping é passivo mesmo ou tenho que ficar o dia todo?",
            "Entendi, no início precisa de dedicação",
            "E depois automatiza mais né",
            "Quantos meses até ficar mais automático?",
            "3-6 meses ok, consigo me programar",
            "E durante as férias posso focar total nisso",
            "Gosto da ideia, quanto preciso investir?",
            "Qual o melhor plano pra começar?",
            "Semestral parece fazer sentido",
            "Dá uns 74 por mês, cabe no orçamento",
            "Vou pegar esse, me manda o link"
        ]
    },
    {
        "id": 16,
        "nome": "Ricardo Souza",
        "phone": "5541973016016",
        "perfil": "Motorista de Uber",
        "idade": 33,
        "situacao": "Cansado de dirigir, quer outra fonte",
        "nivel": "Iniciante",
        "fluxo": [
            "Trabalho com Uber mas tá difícil",
            "Preço do combustível subiu demais",
            "Quero uma renda que não dependa de sair de casa",
            "Dropshipping eu posso fazer do celular entre corridas?",
            "Legal, posso gerenciar nos tempos livres",
            "Quanto tempo por dia preciso dedicar no início?",
            "1-2h por dia consigo encaixar",
            "E o investimento inicial é quanto?",
            "69 no mensal... é tipo um tanque de gasolina",
            "Mas esse eu não queimo, invisto né haha",
            "Faz sentido, vou tentar",
            "Começo com mensal pra testar",
            "Se der certo migro pro semestral depois"
        ]
    },
    {
        "id": 17,
        "nome": "Camila Torres",
        "phone": "5561972017017",
        "perfil": "Influencer fitness (15k seguidores)",
        "idade": 26,
        "situacao": "Quer vender produtos fit",
        "nivel": "Médio - conhece marketing",
        "fluxo": [
            "Oi! Tenho perfil fitness com 15k seguidores",
            "Quero vender produtos fit, vocês têm?",
            "Tipo whey, shakers, roupas de treino?",
            "Perfeito! Minha audiência compra muito isso",
            "Como funciona a integração com meu insta?",
            "Posso colocar link na bio direcionando pra loja?",
            "E stories com link de swipe up?",
            "Ótimo, é exatamente o que preciso",
            "Qual comissão eu fico em cada venda?",
            "20-30% de margem tá bom pra começar",
            "Quanto custa pra assinar?",
            "Vou de anual, já vou usar bastante",
            "Me passa o link de pagamento aí"
        ]
    },
    {
        "id": 18,
        "nome": "José Carlos",
        "phone": "5581971018018",
        "perfil": "Comerciante tradicional resistente",
        "idade": 55,
        "situacao": "Tem loja física mas está indo mal",
        "nivel": "Iniciante - resistente à tecnologia",
        "fluxo": [
            "Tenho loja de eletrônicos há 30 anos",
            "Mas o online tá matando a gente",
            "Meu filho disse pra eu vir falar com vocês",
            "Mas não entendo essas coisas de internet",
            "Como funciona esse tal de dropshipping?",
            "Não preciso ter os produtos? Estranho isso",
            "E se o cliente quiser ver antes de comprar?",
            "Ah, é venda online, não tem isso mesmo né",
            "Tô velho pra essas mudanças...",
            "Mas fazer o que, preciso me adaptar",
            "Vocês ensinam direitinho como funciona?",
            "Meu filho pode me ajudar a configurar",
            "Quanto custa pra começar?",
            "Vou tentar, se meu filho me ajudar"
        ]
    },
    {
        "id": 19,
        "nome": "Larissa Mendes",
        "phone": "5521970019019",
        "perfil": "Estudante de marketing",
        "idade": 21,
        "situacao": "TCC sobre e-commerce",
        "nivel": "Médio - estudando o tema",
        "fluxo": [
            "Oi! Estou fazendo TCC sobre e-commerce",
            "Posso fazer umas perguntas sobre dropshipping?",
            "Quantos clientes vocês têm ativos?",
            "E taxa média de conversão dos usuários?",
            "Entendo, vocês não podem divulgar esses dados",
            "Mas em termos gerais, o modelo funciona?",
            "A maioria dos usuários tem sucesso?",
            "Interessante... e qual o investimento médio?",
            "Hmm, pensando bem poderia testar na prática",
            "Seria útil pro meu TCC ter experiência real",
            "Posso usar os dados pro trabalho?",
            "Legal! Então vou assinar pra testar",
            "Qual plano você recomenda pra teste acadêmico?",
            "Mensal tá bom, é só por 3 meses mesmo"
        ]
    },
    {
        "id": 20,
        "nome": "Anderson Lima",
        "phone": "5531969020020",
        "perfil": "Desempregado desesperado",
        "idade": 38,
        "situacao": "Perdeu emprego na pandemia, contas atrasadas",
        "nivel": "Iniciante - situação urgente",
        "fluxo": [
            "Perdi meu emprego na pandemia",
            "Tô com contas atrasadas, preciso de dinheiro rápido",
            "Quanto tempo pra fazer a primeira venda?",
            "1-2 semanas? Preciso antes disso",
            "Tenho conta de luz pra pagar semana que vem",
            "Não dá pra esperar",
            "Mas se eu me dedicar todo dia, consigo mais rápido?",
            "Tá, entendo que não é garantido",
            "Mas preciso tentar alguma coisa",
            "Quanto custa?",
            "69 reais... vou ter que tirar da comida",
            "Mas se funcionar vale a pena",
            "Vou arriscar, não tenho escolha",
            "Como faço pra assinar?"
        ]
    }
]

def limpar_usuario(phone):
    """Limpa dados de teste de um usuário"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            DELETE FROM conversation_history
            WHERE customer_id IN (SELECT id FROM customers WHERE phone = %s)
        """, (phone,))
        
        cur.execute("""
            DELETE FROM customer_context
            WHERE customer_id IN (SELECT id FROM customers WHERE phone = %s)
        """, (phone,))
        
        cur.execute("DELETE FROM customers WHERE phone = %s", (phone,))
        
        conn.commit()
        conn.close()
    except:
        pass

def criar_usuario(nome, phone):
    """Cria usuário no banco"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO customers (name, phone, email, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (phone) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
        """, (nome, phone, f"{phone}@teste.com"))
        
        result = cur.fetchone()
        conn.commit()
        conn.close()
        
        return result['id'] if result else None
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return None

def enviar_mensagem(phone, mensagem):
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
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

def get_ultima_resposta(customer_id):
    """Pega última resposta da Gabi"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT agent_response, timestamp
            FROM conversation_history
            WHERE customer_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (customer_id,))
        
        result = cur.fetchone()
        conn.close()
        
        return result['agent_response'] if result else None
    except:
        return None

def analisar_conversa(customer_id):
    """Analisa o resultado da conversa"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Pegar toda a conversa
        cur.execute("""
            SELECT user_message, agent_response
            FROM conversation_history
            WHERE customer_id = %s
            ORDER BY timestamp ASC
        """, (customer_id,))
        
        conversas = cur.fetchall()
        conn.close()
        
        if not conversas:
            return {
                "total_mensagens": 0,
                "fechou": False,
                "motivo": "Sem conversa"
            }
        
        # Analisar última resposta
        ultima_resposta = conversas[-1]['agent_response'].lower() if conversas else ""
        todas_respostas = " ".join([c['agent_response'].lower() for c in conversas])
        
        # Detectar fechamento
        fechou = False
        motivo_fechamento = ""
        
        if any(palavra in todas_respostas for palavra in ["link de pagamento", "pay.kiwify", "assinar", "whatsapp do suporte"]):
            if any(palavra in todas_respostas for palavra in ["pay.kiwify", "kiwify.com"]):
                fechou = True
                motivo_fechamento = "Enviou link de pagamento"
            elif "whatsapp do suporte" in todas_respostas:
                motivo_fechamento = "Direcionou para suporte (possível assinante)"
        
        # Detectar objeção não resolvida
        ultima_msg_user = conversas[-1]['user_message'].lower() if conversas else ""
        
        if any(palavra in ultima_msg_user for palavra in ["vou pensar", "depois eu volto", "mais tarde", "não tenho"]):
            motivo_fechamento = "Objeção não resolvida - cliente adiou"
        elif any(palavra in ultima_msg_user for palavra in ["valeu", "flw", "obrigad", "tchau"]):
            if not fechou:
                motivo_fechamento = "Cliente encerrou sem fechar"
        
        return {
            "total_mensagens": len(conversas),
            "fechou": fechou,
            "motivo": motivo_fechamento if motivo_fechamento else "Em andamento",
            "conversas": conversas
        }
        
    except Exception as e:
        return {
            "total_mensagens": 0,
            "fechou": False,
            "motivo": f"Erro: {e}"
        }

def executar_teste():
    """Executa teste completo com 20 usuários"""
    print("\n" + "="*100)
    print("🧪 TESTE COMPLETO: 20 USUÁRIOS LEADS FRIOS DE TRÁFEGO PAGO")
    print("="*100)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👥 Total de usuários: {len(USUARIOS)}")
    print("🎯 Objetivo: Ver como a Gabi conduz vendas do início ao fim")
    print("="*100)
    
    resultados = []
    
    for usuario in USUARIOS:
        print(f"\n{'━'*100}")
        print(f"👤 USUÁRIO {usuario['id']}/20: {usuario['nome']}")
        print(f"{'━'*100}")
        print(f"📱 Telefone: {usuario['phone']}")
        print(f"👔 Perfil: {usuario['perfil']}")
        print(f"📊 Nível: {usuario['nivel']}")
        print(f"💼 Situação: {usuario['situacao']}")
        print(f"💬 Mensagens previstas: {len(usuario['fluxo'])}")
        
        # Limpar dados anteriores
        limpar_usuario(usuario['phone'])
        
        # Criar usuário
        customer_id = criar_usuario(usuario['nome'], usuario['phone'])
        
        if not customer_id:
            print(f"❌ Falha ao criar usuário")
            continue
        
        print(f"✅ Customer ID: {customer_id}")
        print(f"\n🔄 INICIANDO CONVERSA...")
        print("─"*100)
        
        # Enviar cada mensagem do fluxo
        for i, mensagem in enumerate(usuario['fluxo'], 1):
            print(f"\n  [{i}/{len(usuario['fluxo'])}] 👤 {usuario['nome']}: {mensagem}")
            
            if not enviar_mensagem(usuario['phone'], mensagem):
                print(f"      ❌ Falha ao enviar")
                continue
            
            # Aguardar processamento (13s buffer + 5s processamento)
            print(f"      ⏳ Aguardando 20s...")
            time.sleep(20)
            
            # Pegar resposta
            resposta = get_ultima_resposta(customer_id)
            
            if resposta:
                # Limitar exibição a 200 caracteres
                resposta_exibir = resposta[:200] + "..." if len(resposta) > 200 else resposta
                print(f"      🤖 Gabi: {resposta_exibir}")
            else:
                print(f"      ⚠️ Sem resposta registrada")
            
            # Pequeno delay entre mensagens do mesmo usuário
            time.sleep(3)
        
        # Analisar resultado da conversa
        print(f"\n{'─'*100}")
        print(f"📊 ANÁLISE DA CONVERSA:")
        analise = analisar_conversa(customer_id)
        
        print(f"   Total de trocas: {analise['total_mensagens']}")
        print(f"   Fechou venda: {'✅ SIM' if analise['fechou'] else '❌ NÃO'}")
        print(f"   Status: {analise['motivo']}")
        
        resultados.append({
            "id": usuario['id'],
            "nome": usuario['nome'],
            "perfil": usuario['perfil'],
            "nivel": usuario['nivel'],
            "total_mensagens": analise['total_mensagens'],
            "fechou": analise['fechou'],
            "motivo": analise['motivo']
        })
        
        # Delay maior entre usuários
        if usuario['id'] < len(USUARIOS):
            print(f"\n⏸️ Aguardando 10s antes do próximo usuário...")
            time.sleep(10)
    
    # RELATÓRIO FINAL
    print("\n" + "="*100)
    print("📊 RELATÓRIO FINAL - PERFORMANCE DA GABI")
    print("="*100)
    
    total_usuarios = len(resultados)
    total_fechamentos = sum(1 for r in resultados if r['fechou'])
    taxa_conversao = (total_fechamentos / total_usuarios * 100) if total_usuarios > 0 else 0
    
    print(f"\n📈 MÉTRICAS GERAIS:")
    print(f"   Total de conversas: {total_usuarios}")
    print(f"   Fechamentos: {total_fechamentos}")
    print(f"   Taxa de conversão: {taxa_conversao:.1f}%")
    
    # Por nível
    print(f"\n📊 PERFORMANCE POR NÍVEL:")
    for nivel in ["Iniciante", "Médio", "Avançado"]:
        usuarios_nivel = [r for r in resultados if nivel.lower() in r['nivel'].lower()]
        if usuarios_nivel:
            fechamentos_nivel = sum(1 for r in usuarios_nivel if r['fechou'])
            taxa_nivel = (fechamentos_nivel / len(usuarios_nivel) * 100) if usuarios_nivel else 0
            print(f"   {nivel}: {fechamentos_nivel}/{len(usuarios_nivel)} ({taxa_nivel:.1f}%)")
    
    # Detalhamento
    print(f"\n📋 DETALHAMENTO POR USUÁRIO:")
    print("─"*100)
    
    for r in resultados:
        status = "✅ FECHOU" if r['fechou'] else "❌ NÃO FECHOU"
        print(f"{r['id']:2d}. {r['nome']:25s} | {r['perfil']:30s} | {status:15s} | {r['motivo']}")
    
    print("="*100)
    
    # Salvar relatório
    with open('relatorio_20_usuarios.json', 'w', encoding='utf-8') as f:
        json.dump({
            "data": datetime.now().isoformat(),
            "total_usuarios": total_usuarios,
            "total_fechamentos": total_fechamentos,
            "taxa_conversao": taxa_conversao,
            "resultados": resultados
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Relatório salvo em: relatorio_20_usuarios.json")
    print("="*100)

if __name__ == "__main__":
    print("\n⚠️ ATENÇÃO: Este teste vai demorar aproximadamente 2-3 HORAS!")
    print("   - 20 usuários")
    print("   - ~10-15 mensagens por usuário")
    print("   - ~20s de delay por mensagem")
    print("   - Total: ~200-300 mensagens")

    # Verificar se foi passado argumento --auto ou --sim
    if len(sys.argv) > 1 and sys.argv[1] in ['--auto', '--sim', 'sim', 'auto']:
        print("\n✅ Modo automático ativado - iniciando teste...")
        executar_teste()
    else:
        confirma = input("\n▶️ Deseja continuar? (sim/não): ").lower().strip()

        if confirma in ['sim', 's', 'yes', 'y']:
            executar_teste()
        else:
            print("❌ Teste cancelado pelo usuário")
