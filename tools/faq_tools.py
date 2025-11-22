import csv
import os
from agno.tools import Toolkit
from typing import List, Dict, Any
from difflib import SequenceMatcher

class SPDropFAQTools(Toolkit):
    """Ferramenta de FAQ para SPDrop - Base de conhecimento interna"""

    def __init__(self):
        # Setup FAQ data
        self.faq_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs da minha empresa",
            "suporte - transformar esse texto em uma planilha de pergunt....csv"
        )
        self.faqs = self._load_faqs()

        # Register all tools in the constructor
        tools = [
            self.buscar_faq,
            self.listar_todas_perguntas,
            self.buscar_resposta_por_palavra_chave
        ]

        super().__init__(name="spdrop_faq", tools=tools)

    def _load_faqs(self) -> List[Dict[str, str]]:
        """Carrega todas as FAQs do arquivo CSV"""
        faqs = []

        try:
            if not os.path.exists(self.faq_file_path):
                return []

            with open(self.faq_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    faqs.append({
                        'pergunta': row.get('Pergunta', ''),
                        'resposta': row.get('Resposta', ''),
                        'resposta_recomendada': row.get('Resposta Recomendada', '')
                    })

            return faqs
        except Exception as e:
            return []

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos (0 a 1)"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def buscar_faq(self, pergunta_cliente: str) -> Dict[str, Any]:
        """
        Busca a FAQ mais similar à pergunta do cliente.

        Args:
            pergunta_cliente: Pergunta feita pelo cliente

        Returns:
            Dict com pergunta, resposta e resposta recomendada
        """
        if not self.faqs:
            return {
                "encontrado": False,
                "erro": "Base de FAQs não carregada"
            }

        # Encontrar a pergunta mais similar
        melhor_match = None
        melhor_score = 0

        for faq in self.faqs:
            score = self._similarity_score(pergunta_cliente, faq['pergunta'])
            if score > melhor_score:
                melhor_score = score
                melhor_match = faq

        # Considerar match válido se similaridade > 0.3
        if melhor_score > 0.3 and melhor_match:
            return {
                "encontrado": True,
                "pergunta_original": pergunta_cliente,
                "pergunta_faq": melhor_match['pergunta'],
                "resposta_recomendada": melhor_match['resposta_recomendada'],
                "resposta_informal": melhor_match['resposta'],
                "confianca": round(melhor_score * 100, 1)
            }
        else:
            return {
                "encontrado": False,
                "pergunta_original": pergunta_cliente,
                "mensagem": "Nenhuma FAQ similar encontrada"
            }

    def listar_todas_perguntas(self) -> Dict[str, Any]:
        """
        Lista todas as perguntas disponíveis no FAQ.

        Returns:
            Dict com lista de todas as perguntas
        """
        if not self.faqs:
            return {
                "total": 0,
                "perguntas": []
            }

        perguntas = [faq['pergunta'] for faq in self.faqs]

        return {
            "total": len(perguntas),
            "perguntas": perguntas
        }

    def buscar_resposta_por_palavra_chave(self, palavra_chave: str) -> Dict[str, Any]:
        """
        Busca FAQs que contenham a palavra-chave na pergunta ou resposta.

        Args:
            palavra_chave: Palavra ou termo para buscar

        Returns:
            Dict com lista de FAQs encontradas
        """
        if not self.faqs:
            return {
                "encontrado": False,
                "total": 0,
                "resultados": []
            }

        palavra_lower = palavra_chave.lower()
        resultados = []

        for faq in self.faqs:
            # Buscar na pergunta e nas respostas
            if (palavra_lower in faq['pergunta'].lower() or
                palavra_lower in faq['resposta'].lower() or
                palavra_lower in faq['resposta_recomendada'].lower()):

                resultados.append({
                    "pergunta": faq['pergunta'],
                    "resposta_recomendada": faq['resposta_recomendada']
                })

        if resultados:
            return {
                "encontrado": True,
                "palavra_chave": palavra_chave,
                "total": len(resultados),
                "resultados": resultados
            }
        else:
            return {
                "encontrado": False,
                "palavra_chave": palavra_chave,
                "total": 0,
                "mensagem": f"Nenhuma FAQ encontrada com a palavra '{palavra_chave}'"
            }
