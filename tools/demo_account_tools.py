from agno.tools import Toolkit
from agno.utils.log import logger
from typing import Dict

class DemoAccountTools(Toolkit):
    """Tools para gerenciar acesso à conta de demonstração da SPDrop"""

    def __init__(self):
        super().__init__(name="demo_account_tools")

        # Credenciais da conta demonstração
        self.demo_credentials = {
            "site": "https://app.spdrop.com.br/login",
            "email": "williamsiva4545@gmail.com",
            "senha": "264588aB@"
        }

        # Gatilhos que indicam que cliente quer ver a plataforma
        self.gatilhos_demo = [
            "ver produto", "ver catalogo", "ver catálogo", "ver fornecedor",
            "ver plataforma", "como funciona", "conhecer plataforma",
            "quero ver", "mostrar produto", "mostrar catalogo",
            "mostrar fornecedor", "ver como é", "ver por dentro"
        ]

        self.register(self.fornecer_conta_demo)
        self.register(self.verificar_se_deve_oferecer_demo)

    def fornecer_conta_demo(self) -> Dict:
        """
        Fornece as credenciais da conta de demonstração da SPDrop.

        Use quando cliente quer:
        - Ver os produtos
        - Ver o catálogo
        - Conhecer os fornecedores
        - Ver a plataforma por dentro
        - Entender como funciona

        ⚠️ IMPORTANTE: Conta demonstração é DIFERENTE de teste 7 dias
        - Demonstração: apenas para VER (não integrar com loja real)
        - Teste 7 dias: para usar de verdade (público qualificado)

        Returns:
            Dict com credenciais e instruções
        """
        logger.info("Fornecendo credenciais da conta de demonstração")

        return {
            "success": True,
            "tipo": "conta_demonstracao",
            "credenciais": self.demo_credentials,
            "mensagem_formatada": f"""Perfeito! Vou te passar o acesso à nossa conta de demonstração para você explorar a plataforma e ver nosso catálogo de produtos 😊

📱 **Acesso Demonstração:**

🌐 Site: {self.demo_credentials['site']}
📧 Email: {self.demo_credentials['email']}
🔑 Senha: {self.demo_credentials['senha']}

⚠️ **Importante:** Esta é uma conta apenas para você VER como funciona. Não integre com sua loja real!

Lá dentro você vai encontrar:
✅ Catálogo completo de produtos
✅ Fornecedores verificados
✅ Preços e margens sugeridas
✅ Como funciona a integração

Dá uma olhada e me conta o que achou! Qualquer dúvida, estou aqui 🙌""",
            "alerta": "⚠️ Conta demonstração - não integre com sua loja real"
        }

    def verificar_se_deve_oferecer_demo(self, mensagem_cliente: str) -> Dict:
        """
        Verifica se a mensagem do cliente indica que ele quer ver a plataforma/produtos.

        Args:
            mensagem_cliente: Mensagem enviada pelo cliente

        Returns:
            Dict indicando se deve oferecer demo e qual gatilho foi identificado
        """
        mensagem_lower = mensagem_cliente.lower()

        for gatilho in self.gatilhos_demo:
            if gatilho in mensagem_lower:
                logger.info(f"Gatilho identificado: '{gatilho}' - deve oferecer conta demo")
                return {
                    "deve_oferecer": True,
                    "gatilho_identificado": gatilho,
                    "mensagem": "Cliente demonstrou interesse em VER a plataforma/produtos. Ofereça a conta de demonstração!"
                }

        return {
            "deve_oferecer": False,
            "mensagem": "Nenhum gatilho de demonstração identificado nesta mensagem"
        }
