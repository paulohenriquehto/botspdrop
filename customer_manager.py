import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
import logging
import re
import os

logger = logging.getLogger(__name__)

class CustomerManager:
    """Gerencia clientes e mapeia telefone → customer_id"""

    def __init__(self):
        self.conn_params = {
            "host": os.getenv("DB_HOST", "postgres"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "spdrop_db"),
            "user": os.getenv("DB_USER", "spdrop_user"),
            "password": os.getenv("DB_PASSWORD", "spdrop_password")
        }

    def _get_connection(self):
        """Criar conexão com o banco"""
        try:
            return psycopg2.connect(**self.conn_params)
        except psycopg2.Error as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            return None

    def normalize_phone(self, phone: str) -> str:
        """
        Normaliza número de telefone removendo caracteres especiais

        Args:
            phone: Número bruto (ex: 5511999999999@c.us)

        Returns:
            Número normalizado (ex: 5511999999999)
        """
        # Remover @c.us, @g.us, espaços, hífens, parênteses
        phone = re.sub(r'@.*', '', phone)
        phone = re.sub(r'[^\d]', '', phone)
        return phone

    def get_or_create_customer(self, phone: str, name: Optional[str] = None) -> Optional[int]:
        """
        Busca ou cria cliente pelo telefone

        Args:
            phone: Número de telefone
            name: Nome do cliente (opcional)

        Returns:
            customer_id ou None
        """
        phone_normalized = self.normalize_phone(phone)
        conn = self._get_connection()

        if not conn:
            return None

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Buscar cliente existente
                cur.execute("""
                    SELECT id, name, phone
                    FROM customers
                    WHERE phone = %s
                """, (phone_normalized,))

                customer = cur.fetchone()

                if customer:
                    logger.info(f"Cliente encontrado: ID={customer['id']}, Nome={customer['name']}")
                    return customer['id']

                # Cliente não existe, criar novo
                customer_name = name or f"Cliente {phone_normalized[-4:]}"

                cur.execute("""
                    INSERT INTO customers (name, phone)
                    VALUES (%s, %s)
                    RETURNING id, name
                """, (customer_name, phone_normalized))

                conn.commit()
                new_customer = cur.fetchone()

                logger.info(f"Novo cliente criado: ID={new_customer['id']}, Nome={new_customer['name']}")
                return new_customer['id']

        except psycopg2.Error as e:
            logger.error(f"Erro ao buscar/criar cliente: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_customer_info(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca informações completas do cliente

        Args:
            customer_id: ID do cliente

        Returns:
            Dict com informações ou None
        """
        conn = self._get_connection()
        if not conn:
            return None

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        c.id,
                        c.name,
                        c.phone,
                        c.email,
                        cc.car_model,
                        cc.car_color,
                        up.interested_services,
                        up.conversation_count
                    FROM customers c
                    LEFT JOIN customer_context cc ON c.id = cc.customer_id
                    LEFT JOIN user_preferences up ON c.id = up.customer_id
                    WHERE c.id = %s
                """, (customer_id,))

                customer = cur.fetchone()
                return dict(customer) if customer else None

        except psycopg2.Error as e:
            logger.error(f"Erro ao buscar info do cliente: {e}")
            return None
        finally:
            conn.close()

    def build_context_message(self, customer_id: int, user_message: str) -> str:
        """
        Constrói mensagem com contexto interno para o agente

        Args:
            customer_id: ID do cliente
            user_message: Mensagem original do usuário

        Returns:
            Mensagem com contexto
        """
        context_prefix = f"[CONTEXTO INTERNO: customer_id={customer_id}]\n"
        return context_prefix + user_message

    def get_or_create_session(self, session_id: str, customer_id: int) -> bool:
        """
        Busca ou cria uma sessão para o cliente

        Args:
            session_id: ID da sessão
            customer_id: ID do cliente

        Returns:
            True se sessão existe ou foi criada, False caso contrário
        """
        conn = self._get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                # Verificar se sessão já existe
                cur.execute("SELECT session_id FROM sessions WHERE session_id = %s", (session_id,))
                if cur.fetchone():
                    return True

                # Criar nova sessão
                cur.execute("""
                    INSERT INTO sessions (session_id, customer_id, status)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (session_id) DO NOTHING
                """, (session_id, customer_id, 'active'))

                conn.commit()
                logger.info(f"Nova sessão criada: {session_id}")
                return True

        except psycopg2.Error as e:
            logger.error(f"Erro ao criar sessão: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def save_conversation(self, session_id: str, customer_id: int, user_message: str, agent_response: str) -> bool:
        """
        Salva a conversa no histórico do PostgreSQL

        Args:
            session_id: ID da sessão (baseado no número WhatsApp)
            customer_id: ID do cliente
            user_message: Mensagem do usuário
            agent_response: Resposta do agente

        Returns:
            True se salvou com sucesso, False caso contrário
        """
        conn = self._get_connection()
        if not conn:
            return False

        try:
            # Garantir que a sessão existe
            self.get_or_create_session(session_id, customer_id)

            with conn.cursor() as cur:
                # Inserir na tabela conversation_history
                cur.execute("""
                    INSERT INTO conversation_history
                    (session_id, customer_id, user_message, agent_response, message_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (session_id, customer_id, user_message, agent_response, 'chat'))

                conn.commit()
                logger.info(f"Conversa salva no histórico para session_id={session_id}")
                return True

        except psycopg2.Error as e:
            logger.error(f"Erro ao salvar conversa: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

# Instância global
customer_manager = CustomerManager()
