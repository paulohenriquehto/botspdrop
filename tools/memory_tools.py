import psycopg2
from psycopg2.extras import RealDictCursor
from agno.tools import Toolkit
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import os

class SPDropMemoryTools(Toolkit):
    def __init__(self):
        # Database configuration
        self.conn_params = {
            "host": os.getenv("DB_HOST", "postgres"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "spdrop_db"),
            "user": os.getenv("DB_USER", "spdrop_user"),
            "password": os.getenv("DB_PASSWORD", "spdrop_password")
        }

        # Register all tools in the constructor
        tools = [
            self.create_session,
            self.save_conversation,
            self.get_conversation_history,
            self.update_customer_preferences,
            self.get_customer_context,
            self.update_customer_context,
            self.get_customer_by_phone,
            self.end_session,
            self.save_important_memory,
            self.get_important_memories
        ]

        super().__init__(name="spdrop_memory", tools=tools)

    def _get_connection(self):
        """Criar conexão com o banco de dados"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            return conn
        except psycopg2.Error as e:
            return None

    def create_session(self, customer_id: int) -> Dict[str, Any]:
        """Cria uma nova sessão de conversa"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            session_id = str(uuid.uuid4())
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO sessions (session_id, customer_id, status)
                    VALUES (%s, %s, 'active')
                    RETURNING id, session_id, customer_id, started_at, status
                """, (session_id, customer_id))
                conn.commit()
                session = cur.fetchone()
                return dict(session) if session else {}
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    def save_conversation(self, session_id: str, customer_id: int, user_message: str, agent_response: str) -> Dict[str, Any]:
        """Salva uma troca de mensagens no histórico"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO conversation_history
                    (session_id, customer_id, user_message, agent_response, message_type)
                    VALUES (%s, %s, %s, %s, 'standard')
                    RETURNING id, session_id, customer_id, timestamp
                """, (session_id, customer_id, user_message, agent_response))
                conn.commit()
                record = cur.fetchone()
                return dict(record) if record else {}
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    def get_conversation_history(self, customer_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        RETRIEVE customer's conversation history. ALWAYS call this FIRST at the start of EVERY interaction.

        This tells you: customer's name, what they asked before, their interests, if they chose a plan, if they're a subscriber.

        Args:
            customer_id: Customer's unique ID
            limit: Number of recent messages (default: 20)

        Returns:
            List of conversations with user_message, agent_response, timestamp. Empty list if no history.
        """
        conn = self._get_connection()
        if not conn:
            return []

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT user_message, agent_response, timestamp
                    FROM conversation_history
                    WHERE customer_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (customer_id, limit))
                history = cur.fetchall()
                return [dict(row) for row in history]
        except psycopg2.Error:
            return []
        finally:
            conn.close()

    def update_customer_preferences(self, customer_id: int, interested_services: str = None, preferred_time_slot: str = None) -> Dict[str, Any]:
        """Atualiza preferências do cliente"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar se existe registro
                cur.execute("SELECT id FROM user_preferences WHERE customer_id = %s", (customer_id,))
                exists = cur.fetchone()

                if exists:
                    # Update
                    cur.execute("""
                        UPDATE user_preferences
                        SET interested_services = COALESCE(%s, interested_services),
                            preferred_time_slot = COALESCE(%s, preferred_time_slot),
                            last_interaction = CURRENT_TIMESTAMP,
                            conversation_count = conversation_count + 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE customer_id = %s
                        RETURNING id, customer_id, interested_services, preferred_time_slot, conversation_count
                    """, (interested_services, preferred_time_slot, customer_id))
                else:
                    # Insert
                    cur.execute("""
                        INSERT INTO user_preferences
                        (customer_id, interested_services, preferred_time_slot, last_interaction, conversation_count)
                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 1)
                        RETURNING id, customer_id, interested_services, preferred_time_slot, conversation_count
                    """, (customer_id, interested_services, preferred_time_slot))

                conn.commit()
                record = cur.fetchone()
                return dict(record) if record else {}
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    def get_customer_context(self, customer_id: int) -> Dict[str, Any]:
        """Retorna contexto completo do cliente"""
        conn = self._get_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM customer_context
                    WHERE customer_id = %s
                """, (customer_id,))
                context = cur.fetchone()
                return dict(context) if context else {}
        except psycopg2.Error:
            return {}
        finally:
            conn.close()

    def update_customer_context(self, customer_id: int, business_niche: str = None, experience_level: str = None,
                               current_situation: str = None, financial_situation: str = None, notes: str = None) -> Dict[str, Any]:
        """Atualiza contexto do cliente empreendedor (nicho, experiência, situação)"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar se existe
                cur.execute("SELECT id FROM customer_context WHERE customer_id = %s", (customer_id,))
                exists = cur.fetchone()

                if exists:
                    # Update
                    cur.execute("""
                        UPDATE customer_context
                        SET business_niche = COALESCE(%s, business_niche),
                            experience_level = COALESCE(%s, experience_level),
                            current_situation = COALESCE(%s, current_situation),
                            financial_situation = COALESCE(%s, financial_situation),
                            notes = COALESCE(%s, notes),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE customer_id = %s
                        RETURNING id, customer_id, business_niche, experience_level, current_situation, financial_situation, notes
                    """, (business_niche, experience_level, current_situation, financial_situation, notes, customer_id))
                else:
                    # Insert
                    cur.execute("""
                        INSERT INTO customer_context
                        (customer_id, business_niche, experience_level, current_situation, financial_situation, notes)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id, customer_id, business_niche, experience_level, current_situation, financial_situation, notes
                    """, (customer_id, business_niche, experience_level, current_situation, financial_situation, notes))

                conn.commit()
                record = cur.fetchone()
                return dict(record) if record else {}
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    def get_customer_by_phone(self, phone: str) -> Dict[str, Any]:
        """Busca cliente por telefone com todo seu contexto"""
        conn = self._get_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT c.*, up.interested_services, up.conversation_count, cc.business_niche, cc.experience_level, cc.current_situation, cc.financial_situation
                    FROM customers c
                    LEFT JOIN user_preferences up ON c.id = up.customer_id
                    LEFT JOIN customer_context cc ON c.id = cc.customer_id
                    WHERE c.phone = %s
                """, (phone,))
                customer = cur.fetchone()
                return dict(customer) if customer else {}
        except psycopg2.Error:
            return {}
        finally:
            conn.close()

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """Finaliza uma sessão de conversa"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    UPDATE sessions
                    SET ended_at = CURRENT_TIMESTAMP, status = 'closed'
                    WHERE session_id = %s
                    RETURNING session_id, status, ended_at
                """, (session_id,))
                conn.commit()
                record = cur.fetchone()
                return dict(record) if record else {}
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    def save_important_memory(self, **kwargs) -> Dict[str, Any]:
        """
        Salva uma lembrança importante sobre o cliente que nunca será esquecida.

        Args:
            customer_id: ID do cliente
            memory_key: Nome da chave da memória (string)
            memory_value: Valor a ser salvo (string)

        EXEMPLOS DE USO:

        save_important_memory(customer_id=17, memory_key='nome_completo', memory_value='Paulo')
        save_important_memory(customer_id=17, memory_key='plano_interesse', memory_value='semestral')

        MEMORY_KEYS DISPONÍVEIS:
        'nome_completo', 'is_subscriber', 'plano_interesse', 'referred_by', 'objetivo', etc.
        """
        import json

        # Extrair customer_id
        customer_id = kwargs.get('customer_id')
        if not customer_id:
            return {"error": "customer_id é obrigatório"}

        # Extrair memory_key e memory_value (formato correto)
        memory_key = kwargs.get('memory_key')
        memory_value = kwargs.get('memory_value')

        # AUTO-FIX: Se não achou memory_key/memory_value, procura em outros kwargs (formato que o modelo usa)
        if not memory_key or not memory_value:
            for key, value in kwargs.items():
                if key not in ['customer_id', 'memory_key', 'memory_value']:
                    memory_key = key
                    memory_value = str(value)
                    break

        # Validação final
        if not memory_key or not memory_value:
            return {"error": "Não foi possível identificar memory_key e memory_value. Use: save_important_memory(customer_id=X, memory_key='key', memory_value='value')"}

        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Buscar memórias existentes
                cur.execute("SELECT notes FROM customer_context WHERE customer_id = %s", (customer_id,))
                result = cur.fetchone()

                # Carregar memórias existentes ou criar novo dict
                if result and result['notes']:
                    try:
                        memories = json.loads(result['notes'])
                    except:
                        memories = {}
                else:
                    memories = {}

                # Adicionar/atualizar a nova memória
                memories[memory_key] = {
                    'value': memory_value,
                    'updated_at': datetime.now().isoformat()
                }

                # Salvar de volta
                notes_json = json.dumps(memories, ensure_ascii=False)

                # Verificar se já existe registro
                cur.execute("SELECT id FROM customer_context WHERE customer_id = %s", (customer_id,))
                exists = cur.fetchone()

                if exists:
                    cur.execute("""
                        UPDATE customer_context
                        SET notes = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE customer_id = %s
                        RETURNING id, customer_id, notes
                    """, (notes_json, customer_id))
                else:
                    cur.execute("""
                        INSERT INTO customer_context (customer_id, notes)
                        VALUES (%s, %s)
                        RETURNING id, customer_id, notes
                    """, (customer_id, notes_json))

                conn.commit()
                record = cur.fetchone()
                return {
                    "success": True,
                    "memory_key": memory_key,
                    "memory_value": memory_value,
                    "customer_id": customer_id
                }
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    def get_important_memories(self, customer_id: int) -> Dict[str, Any]:
        """
        RETRIEVE critical facts about the customer that should NEVER be forgotten.
        Call this AFTER get_conversation_history to get: name, subscriber status, who referred them, chosen plan.

        Args:
            customer_id: Customer's unique ID

        Returns:
            Dictionary with memories like: {'nome_completo': {'value': 'Paulo', 'updated_at': '...'}, 'is_subscriber': {...}}
            Empty dict if no memories saved.
        """
        import json

        conn = self._get_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT notes FROM customer_context
                    WHERE customer_id = %s
                """, (customer_id,))
                result = cur.fetchone()

                if result and result['notes']:
                    try:
                        memories = json.loads(result['notes'])
                        return memories
                    except:
                        return {}
                else:
                    return {}
        except psycopg2.Error:
            return {}
        finally:
            conn.close()
