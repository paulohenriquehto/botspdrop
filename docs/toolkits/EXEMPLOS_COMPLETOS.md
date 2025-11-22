# 📝 Exemplos Completos de Toolkits

Este arquivo contém exemplos completos e funcionais de toolkits para diferentes casos de uso.

## Índice

1. [Toolkit de Banco de Dados (PostgreSQL)](#1-toolkit-de-banco-de-dados-postgresql)
2. [Toolkit de API REST](#2-toolkit-de-api-rest)
3. [Toolkit de Arquivos (CSV/JSON)](#3-toolkit-de-arquivos-csvjson)
4. [Toolkit de Integração (Email/SMS)](#4-toolkit-de-integração-emailsms)
5. [Toolkit Híbrido (Múltiplas Fontes)](#5-toolkit-híbrido-múltiplas-fontes)

---

## 1. Toolkit de Banco de Dados (PostgreSQL)

### Caso de Uso: Sistema de CRM com Memória de Clientes

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from agno.tools import Toolkit
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

class CRMMemoryTools(Toolkit):
    """
    Toolkit completo para gerenciar memória e contexto de clientes em CRM.

    Funcionalidades:
    - Buscar histórico de conversas
    - Salvar e recuperar memórias importantes
    - Gerenciar preferências do cliente
    - Rastrear interações
    """

    def __init__(self):
        # Configuração do banco de dados
        self.conn_params = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "crm_db"),
            "user": os.getenv("DB_USER", "crm_user"),
            "password": os.getenv("DB_PASSWORD", "crm_password")
        }

        # Lista de ferramentas disponíveis
        tools = [
            # Ferramentas de leitura
            self.get_conversation_history,
            self.get_important_memories,
            self.get_customer_preferences,
            self.get_customer_full_context,

            # Ferramentas de escrita
            self.save_conversation,
            self.save_important_memory,
            self.update_customer_preferences,

            # Ferramentas de análise
            self.count_interactions,
            self.get_last_interaction_date,
        ]

        # Inicializar toolkit
        super().__init__(name="crm_memory", tools=tools)

    # ============================================================================
    # MÉTODOS AUXILIARES PRIVADOS (Não são tools)
    # ============================================================================

    def _get_connection(self):
        """Cria conexão com o banco de dados"""
        try:
            return psycopg2.connect(**self.conn_params)
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao banco: {e}")
            return None

    def _safe_json_loads(self, json_str: str) -> Dict:
        """Converte string JSON em dict de forma segura"""
        try:
            return json.loads(json_str) if json_str else {}
        except:
            return {}

    # ============================================================================
    # FERRAMENTAS DE LEITURA
    # ============================================================================

    def get_conversation_history(
        self,
        customer_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        RETRIEVE the complete conversation history for a customer.

        🚨 ALWAYS call this FIRST when starting a conversation!

        This tool returns:
        - All previous messages from the customer
        - All previous responses from the agent
        - Timestamps of each interaction

        Use this to understand:
        - What the customer asked before
        - What plans/products they were interested in
        - If they made any decisions
        - Their communication style

        Args:
            customer_id (int): Unique customer identifier
            limit (int): Maximum number of conversations to retrieve (default: 20)

        Returns:
            List[Dict]: List of conversations, each containing:
                - user_message: What the customer said
                - agent_response: What you responded
                - timestamp: When the conversation happened

            Returns empty list [] if no history found.

        Example:
            >>> history = get_conversation_history(customer_id=123, limit=10)
            >>> print(history[0])
            {
                "user_message": "Quanto custa o plano mensal?",
                "agent_response": "O plano mensal custa R$ 69!",
                "timestamp": "2024-11-20 10:30:00"
            }
        """
        conn = self._get_connection()
        if not conn:
            return []

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        user_message,
                        agent_response,
                        timestamp,
                        session_id
                    FROM conversation_history
                    WHERE customer_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (customer_id, limit))

                history = cur.fetchall()
                return [dict(row) for row in history]
        except psycopg2.Error as e:
            print(f"Erro ao buscar histórico: {e}")
            return []
        finally:
            conn.close()

    def get_important_memories(self, customer_id: int) -> Dict[str, Any]:
        """
        RETRIEVE critical facts about the customer that should NEVER be forgotten.

        🚨 ALWAYS call this SECOND (after get_conversation_history)!

        This tool returns structured memories like:
        - Customer's full name
        - Subscriber status (yes/no)
        - Chosen plan
        - Who referred them
        - Financial situation
        - Business goals
        - Any other critical information

        These memories persist forever and should guide your responses.

        Args:
            customer_id (int): Unique customer identifier

        Returns:
            Dict: Memories organized by keys, each containing:
                - value: The actual information
                - updated_at: When this memory was last updated

            Returns empty dict {} if no memories found.

        Example:
            >>> memories = get_important_memories(customer_id=123)
            >>> print(memories)
            {
                "nome_completo": {
                    "value": "Paulo Silva",
                    "updated_at": "2024-11-20T10:30:00"
                },
                "is_subscriber": {
                    "value": "sim",
                    "updated_at": "2024-11-20T10:35:00"
                },
                "plano_escolhido": {
                    "value": "semestral",
                    "updated_at": "2024-11-20T10:36:00"
                }
            }
        """
        conn = self._get_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT notes
                    FROM customer_context
                    WHERE customer_id = %s
                """, (customer_id,))

                result = cur.fetchone()

                if result and result['notes']:
                    return self._safe_json_loads(result['notes'])
                else:
                    return {}
        except psycopg2.Error as e:
            print(f"Erro ao buscar memórias: {e}")
            return {}
        finally:
            conn.close()

    def get_customer_preferences(self, customer_id: int) -> Dict[str, Any]:
        """
        GET customer preferences and interaction statistics.

        Returns information about:
        - Services they're interested in
        - Preferred contact time
        - Total number of interactions
        - Last interaction date

        Args:
            customer_id (int): Customer identifier

        Returns:
            Dict with preferences or empty dict if not found
        """
        conn = self._get_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        interested_services,
                        preferred_time_slot,
                        conversation_count,
                        last_interaction
                    FROM user_preferences
                    WHERE customer_id = %s
                """, (customer_id,))

                result = cur.fetchone()
                return dict(result) if result else {}
        except psycopg2.Error as e:
            print(f"Erro ao buscar preferências: {e}")
            return {}
        finally:
            conn.close()

    def get_customer_full_context(self, customer_id: int) -> Dict[str, Any]:
        """
        GET complete context about a customer from all sources.

        This is a comprehensive tool that combines:
        - Conversation history (last 10 messages)
        - Important memories
        - Preferences
        - Interaction statistics

        Use this when you need a complete picture of the customer.

        Args:
            customer_id (int): Customer identifier

        Returns:
            Dict containing all available information about the customer
        """
        return {
            "conversation_history": self.get_conversation_history(customer_id, limit=10),
            "memories": self.get_important_memories(customer_id),
            "preferences": self.get_customer_preferences(customer_id),
            "stats": {
                "total_interactions": self.count_interactions(customer_id),
                "last_interaction": self.get_last_interaction_date(customer_id)
            }
        }

    # ============================================================================
    # FERRAMENTAS DE ESCRITA
    # ============================================================================

    def save_conversation(
        self,
        session_id: str,
        customer_id: int,
        user_message: str,
        agent_response: str
    ) -> Dict[str, Any]:
        """
        SAVE a conversation exchange to the database.

        Args:
            session_id: Unique session identifier
            customer_id: Customer identifier
            user_message: What the customer said
            agent_response: What you responded

        Returns:
            Dict with success status and saved record info
        """
        conn = self._get_connection()
        if not conn:
            return {"success": False, "error": "Database connection failed"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO conversation_history
                    (session_id, customer_id, user_message, agent_response, message_type)
                    VALUES (%s, %s, %s, %s, 'standard')
                    RETURNING id, timestamp
                """, (session_id, customer_id, user_message, agent_response))

                conn.commit()
                record = cur.fetchone()

                return {
                    "success": True,
                    "record_id": record['id'],
                    "timestamp": str(record['timestamp'])
                }
        except psycopg2.Error as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def save_important_memory(
        self,
        customer_id: int,
        memory_key: str,
        memory_value: str
    ) -> Dict[str, Any]:
        """
        SAVE critical information about a customer that should never be forgotten.

        🔹 Use this when the customer tells you something important!

        Common memory keys:
        - 'nome_completo': Customer's full name
        - 'is_subscriber': 'sim' or 'não'
        - 'plano_escolhido': 'mensal', 'semestral', 'anual'
        - 'referred_by': Who referred this customer
        - 'objetivo': Customer's business goal
        - 'nicho': Business niche
        - 'situacao_financeira': Financial situation notes

        This function automatically updates if the memory already exists.

        Args:
            customer_id (int): Customer identifier
            memory_key (str): Key to identify this memory
            memory_value (str): The actual information to save

        Returns:
            Dict with success status

        Example:
            >>> save_important_memory(123, 'nome_completo', 'Paulo Silva')
            {"success": True, "memory_key": "nome_completo", "memory_value": "Paulo Silva"}
        """
        conn = self._get_connection()
        if not conn:
            return {"success": False, "error": "Database connection failed"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Buscar memórias existentes
                cur.execute(
                    "SELECT notes FROM customer_context WHERE customer_id = %s",
                    (customer_id,)
                )
                result = cur.fetchone()

                # Carregar ou criar dict de memórias
                memories = self._safe_json_loads(result['notes']) if result and result['notes'] else {}

                # Adicionar/atualizar memória
                memories[memory_key] = {
                    'value': memory_value,
                    'updated_at': datetime.now().isoformat()
                }

                # Salvar de volta
                notes_json = json.dumps(memories, ensure_ascii=False)

                # Verificar se registro existe
                cur.execute(
                    "SELECT id FROM customer_context WHERE customer_id = %s",
                    (customer_id,)
                )
                exists = cur.fetchone()

                if exists:
                    # Update
                    cur.execute("""
                        UPDATE customer_context
                        SET notes = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE customer_id = %s
                    """, (notes_json, customer_id))
                else:
                    # Insert
                    cur.execute("""
                        INSERT INTO customer_context (customer_id, notes)
                        VALUES (%s, %s)
                    """, (customer_id, notes_json))

                conn.commit()

                return {
                    "success": True,
                    "memory_key": memory_key,
                    "memory_value": memory_value,
                    "customer_id": customer_id
                }
        except psycopg2.Error as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def update_customer_preferences(
        self,
        customer_id: int,
        interested_services: Optional[str] = None,
        preferred_time_slot: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        UPDATE customer preferences and increment interaction count.

        Args:
            customer_id: Customer identifier
            interested_services: Services they're interested in (optional)
            preferred_time_slot: Best time to contact (optional)

        Returns:
            Dict with updated preferences
        """
        conn = self._get_connection()
        if not conn:
            return {"success": False, "error": "Database connection failed"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if exists
                cur.execute(
                    "SELECT id FROM user_preferences WHERE customer_id = %s",
                    (customer_id,)
                )
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
                        RETURNING id, interested_services, preferred_time_slot, conversation_count
                    """, (interested_services, preferred_time_slot, customer_id))
                else:
                    # Insert
                    cur.execute("""
                        INSERT INTO user_preferences
                        (customer_id, interested_services, preferred_time_slot, last_interaction, conversation_count)
                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 1)
                        RETURNING id, interested_services, preferred_time_slot, conversation_count
                    """, (customer_id, interested_services, preferred_time_slot))

                conn.commit()
                record = cur.fetchone()
                return {"success": True, **dict(record)}
        except psycopg2.Error as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # ============================================================================
    # FERRAMENTAS DE ANÁLISE
    # ============================================================================

    def count_interactions(self, customer_id: int) -> int:
        """
        COUNT total number of interactions with this customer.

        Args:
            customer_id: Customer identifier

        Returns:
            int: Total number of conversations
        """
        conn = self._get_connection()
        if not conn:
            return 0

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) as total
                    FROM conversation_history
                    WHERE customer_id = %s
                """, (customer_id,))

                result = cur.fetchone()
                return result[0] if result else 0
        except psycopg2.Error:
            return 0
        finally:
            conn.close()

    def get_last_interaction_date(self, customer_id: int) -> Optional[str]:
        """
        GET the date and time of the last interaction with this customer.

        Args:
            customer_id: Customer identifier

        Returns:
            str: ISO formatted datetime of last interaction, or None
        """
        conn = self._get_connection()
        if not conn:
            return None

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT MAX(timestamp) as last_interaction
                    FROM conversation_history
                    WHERE customer_id = %s
                """, (customer_id,))

                result = cur.fetchone()

                if result and result['last_interaction']:
                    return result['last_interaction'].isoformat()
                else:
                    return None
        except psycopg2.Error:
            return None
        finally:
            conn.close()


# ============================================================================
# COMO USAR ESTE TOOLKIT
# ============================================================================

if __name__ == "__main__":
    # Exemplo de uso
    toolkit = CRMMemoryTools()

    # Testar get_conversation_history
    print("=" * 70)
    print("TESTE: get_conversation_history")
    print("=" * 70)
    history = toolkit.get_conversation_history(customer_id=17, limit=5)
    print(f"Encontradas {len(history)} conversas")
    if history:
        print(f"Última conversa: {history[0]}")

    # Testar get_important_memories
    print("\n" + "=" * 70)
    print("TESTE: get_important_memories")
    print("=" * 70)
    memories = toolkit.get_important_memories(customer_id=17)
    print(f"Memórias encontradas: {len(memories)}")
    for key, value in memories.items():
        print(f"  - {key}: {value['value']}")

    # Testar save_important_memory
    print("\n" + "=" * 70)
    print("TESTE: save_important_memory")
    print("=" * 70)
    result = toolkit.save_important_memory(
        customer_id=17,
        memory_key="teste_exemplo",
        memory_value="Valor de teste"
    )
    print(f"Resultado: {result}")

    # Testar get_customer_full_context
    print("\n" + "=" * 70)
    print("TESTE: get_customer_full_context")
    print("=" * 70)
    context = toolkit.get_customer_full_context(customer_id=17)
    print(f"Contexto completo:")
    print(f"  - Histórico: {len(context['conversation_history'])} conversas")
    print(f"  - Memórias: {len(context['memories'])} itens")
    print(f"  - Total interações: {context['stats']['total_interactions']}")
```

---

## 2. Toolkit de API REST

### Caso de Uso: Integração com API de Pagamentos

```python
import requests
from agno.tools import Toolkit
from typing import Dict, Any, Optional, List
import os
from datetime import datetime

class PaymentAPITools(Toolkit):
    """
    Toolkit para integração com API de pagamentos (ex: Kiwify, Stripe, PagSeguro).

    Funcionalidades:
    - Criar links de pagamento
    - Verificar status de pagamento
    - Listar transações
    - Processar webhooks
    """

    def __init__(self):
        # Configuração da API
        self.api_key = os.getenv("PAYMENT_API_KEY")
        self.api_secret = os.getenv("PAYMENT_API_SECRET")
        self.base_url = os.getenv("PAYMENT_API_URL", "https://api.kiwify.com.br")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Lista de ferramentas
        tools = [
            self.create_payment_link,
            self.check_payment_status,
            self.list_customer_transactions,
            self.get_product_info,
            self.validate_coupon
        ]

        super().__init__(name="payment_api", tools=tools)

    def create_payment_link(
        self,
        product_id: str,
        customer_email: str,
        customer_name: str,
        coupon_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        CREATE a personalized payment link for a customer.

        Use this when the customer wants to purchase a product/plan.

        Args:
            product_id: ID of the product/plan (e.g., "prod_mensal_123")
            customer_email: Customer's email address
            customer_name: Customer's full name
            coupon_code: Optional discount coupon code

        Returns:
            Dict containing:
                - payment_link: URL for the customer to complete payment
                - order_id: Unique order identifier
                - amount: Total amount
                - expires_at: When the link expires

        Example:
            >>> create_payment_link(
                    product_id="prod_semestral",
                    customer_email="paulo@example.com",
                    customer_name="Paulo Silva",
                    coupon_code="BLACK2024"
                )
            {
                "success": True,
                "payment_link": "https://pay.kiwify.com.br/ABC123",
                "order_id": "ord_456",
                "amount": 447.00,
                "discount": 50.00,
                "final_amount": 397.00
            }
        """
        try:
            payload = {
                "product_id": product_id,
                "customer": {
                    "email": customer_email,
                    "name": customer_name
                }
            }

            if coupon_code:
                payload["coupon_code"] = coupon_code

            response = requests.post(
                f"{self.base_url}/v1/checkout/create",
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "payment_link": data.get("checkout_url"),
                    "order_id": data.get("order_id"),
                    "amount": data.get("amount"),
                    "discount": data.get("discount", 0),
                    "final_amount": data.get("final_amount"),
                    "expires_at": data.get("expires_at")
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def check_payment_status(self, order_id: str) -> Dict[str, Any]:
        """
        CHECK the current status of a payment/order.

        Use this to verify if a customer has completed payment.

        Args:
            order_id: Unique order identifier

        Returns:
            Dict with payment status information

        Possible statuses:
            - pending: Payment not completed yet
            - paid: Payment successful
            - cancelled: Payment cancelled
            - refunded: Payment was refunded
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/orders/{order_id}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "order_id": order_id,
                    "status": data.get("status"),
                    "paid_at": data.get("paid_at"),
                    "amount": data.get("amount"),
                    "customer_email": data.get("customer", {}).get("email")
                }
            else:
                return {
                    "success": False,
                    "error": "Order not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_customer_transactions(
        self,
        customer_email: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        LIST all transactions for a specific customer.

        Use this to see purchase history.

        Args:
            customer_email: Customer's email
            limit: Maximum number of transactions to return

        Returns:
            Dict with list of transactions
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/transactions",
                headers=self.headers,
                params={
                    "customer_email": customer_email,
                    "limit": limit
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total": len(data.get("transactions", [])),
                    "transactions": data.get("transactions", [])
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to fetch transactions"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_product_info(self, product_id: str) -> Dict[str, Any]:
        """
        GET detailed information about a product/plan.

        Returns pricing, description, availability, etc.

        Args:
            product_id: Product identifier

        Returns:
            Dict with product information
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/products/{product_id}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "product_id": product_id,
                    "name": data.get("name"),
                    "price": data.get("price"),
                    "description": data.get("description"),
                    "available": data.get("available", True)
                }
            else:
                return {
                    "success": False,
                    "error": "Product not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def validate_coupon(
        self,
        coupon_code: str,
        product_id: str
    ) -> Dict[str, Any]:
        """
        VALIDATE if a coupon code is valid for a product.

        Args:
            coupon_code: Coupon code to validate
            product_id: Product the coupon will be used on

        Returns:
            Dict with validation result and discount info
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/coupons/validate",
                headers=self.headers,
                json={
                    "coupon_code": coupon_code,
                    "product_id": product_id
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "valid": data.get("valid", False),
                    "discount_type": data.get("discount_type"),  # "percentage" or "fixed"
                    "discount_value": data.get("discount_value"),
                    "expires_at": data.get("expires_at")
                }
            else:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Invalid coupon"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Exemplo de uso
if __name__ == "__main__":
    toolkit = PaymentAPITools()

    # Criar link de pagamento
    result = toolkit.create_payment_link(
        product_id="prod_semestral",
        customer_email="paulo@example.com",
        customer_name="Paulo Silva",
        coupon_code="BLACK2024"
    )
    print(result)
```

---

## 3. Toolkit de Arquivos (CSV/JSON)

```python
import csv
import json
import os
from agno.tools import Toolkit
from typing import Dict, Any, List
from difflib import SequenceMatcher

class FileDataTools(Toolkit):
    """
    Toolkit para trabalhar com dados em arquivos CSV e JSON.

    Útil para:
    - FAQs
    - Catálogos de produtos
    - Bases de conhecimento
    """

    def __init__(self, data_dir: str = "data"):
        # Configurar diretórios
        self.data_dir = data_dir
        self.faq_file = os.path.join(data_dir, "faq.csv")
        self.products_file = os.path.join(data_dir, "products.json")

        # Carregar dados em memória
        self.faqs = self._load_csv(self.faq_file)
        self.products = self._load_json(self.products_file)

        # Ferramentas
        tools = [
            self.search_faq,
            self.search_product,
            self.list_all_products,
            self.get_product_by_category
        ]

        super().__init__(name="file_data", tools=tools)

    def _load_csv(self, filepath: str) -> List[Dict]:
        """Carrega arquivo CSV"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except:
            return []

    def _load_json(self, filepath: str) -> List[Dict]:
        """Carrega arquivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def _similarity(self, a: str, b: str) -> float:
        """Calcula similaridade entre strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def search_faq(self, question: str, threshold: float = 0.3) -> Dict[str, Any]:
        """
        SEARCH for FAQ entries similar to the customer's question.

        Args:
            question: Customer's question
            threshold: Minimum similarity score (0-1)

        Returns:
            Dict with best matching FAQ
        """
        if not self.faqs:
            return {"found": False, "error": "No FAQ data loaded"}

        best_match = None
        best_score = 0

        for faq in self.faqs:
            score = self._similarity(question, faq.get('question', ''))
            if score > best_score:
                best_score = score
                best_match = faq

        if best_score >= threshold and best_match:
            return {
                "found": True,
                "question": best_match.get('question'),
                "answer": best_match.get('answer'),
                "confidence": round(best_score * 100, 1)
            }
        else:
            return {
                "found": False,
                "message": "No similar FAQ found"
            }

    def search_product(self, query: str) -> List[Dict[str, Any]]:
        """
        SEARCH products by name or description.

        Args:
            query: Search term

        Returns:
            List of matching products
        """
        results = []
        query_lower = query.lower()

        for product in self.products:
            name = product.get('name', '').lower()
            desc = product.get('description', '').lower()

            if query_lower in name or query_lower in desc:
                results.append({
                    "id": product.get('id'),
                    "name": product.get('name'),
                    "price": product.get('price'),
                    "category": product.get('category')
                })

        return results

    def list_all_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        LIST all available products.

        Args:
            limit: Maximum number of products to return

        Returns:
            List of products
        """
        return self.products[:limit]

    def get_product_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        GET all products in a specific category.

        Args:
            category: Product category

        Returns:
            List of products in that category
        """
        return [
            p for p in self.products
            if p.get('category', '').lower() == category.lower()
        ]
```

Continua em `EXEMPLOS_COMPLETOS.md`...

---

**Este arquivo contém 5 exemplos completos. Veja os arquivos restantes para mais casos de uso.**
