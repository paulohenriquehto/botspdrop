import psycopg2
from psycopg2.extras import RealDictCursor
from agno.tools import Toolkit
from typing import List, Dict, Any
from datetime import datetime, timedelta
import os

class TrialManagementTools(Toolkit):
    """Ferramentas para gerenciar testes grátis de 7 dias"""

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
            self.create_trial_user,
            self.get_trial_users,
            self.get_active_trials,
            self.get_expired_trials,
            self.update_trial_status,
            self.convert_trial_to_paid
        ]

        super().__init__(name="trial_management", tools=tools)

    def _get_connection(self):
        """Criar conexão com o banco de dados"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            return conn
        except psycopg2.Error as e:
            return None

    def create_trial_user(self, customer_id: int, full_name: str, cpf: str,
                         phone: str, email: str, notes: str = None) -> Dict[str, Any]:
        """
        Cria um novo usuário em teste grátis de 7 dias

        ⚠️ IMPORTANTE: SÓ CHAME esta função quando tiver TODOS os 4 dados REAIS do cliente!

        NUNCA crie trial com dados vazios, genéricos ou placeholders!

        Args:
            customer_id: ID do cliente no sistema
            full_name: Nome completo REAL (ex: "João Silva")
            cpf: CPF válido (ex: "123.456.789-00")
            phone: Telefone/WhatsApp REAL (ex: "11 98765-4321")
            email: E-mail válido REAL (ex: "joao@email.com")
            notes: Observações adicionais (opcional)

        Antes de chamar, você DEVE ter perguntado e recebido:
        1. Nome completo
        2. CPF
        3. Telefone
        4. E-mail

        Returns:
            Dict com informações do teste criado ou erro se dados inválidos
        """
        # VALIDAÇÃO RIGOROSA: Rejeitar dados vazios, genéricos ou placeholders
        placeholders = ['cliente', 'usuario', 'teste', 'example', '00000', '11111', 'nenhum', 'indefinido']

        # Validar full_name
        if not full_name or len(full_name.strip()) < 3:
            return {"error": "Nome completo inválido ou muito curto. Peça o nome REAL do cliente."}

        if any(p in full_name.lower() for p in placeholders):
            return {"error": f"Nome '{full_name}' parece ser placeholder. Peça o nome REAL do cliente."}

        # Validar CPF
        if not cpf or len(cpf.replace('.', '').replace('-', '').strip()) < 11:
            return {"error": "CPF inválido. Peça o CPF completo do cliente (11 dígitos)."}

        if any(p in cpf for p in ['00000', '11111']):
            return {"error": f"CPF '{cpf}' parece ser placeholder. Peça o CPF REAL do cliente."}

        # Validar phone
        if not phone or len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
            return {"error": "Telefone inválido. Peça o telefone completo do cliente (DDD + número)."}

        if '0000' in phone or phone == '00000000000':
            return {"error": f"Telefone '{phone}' parece ser placeholder. Peça o telefone REAL do cliente."}

        # Validar email
        if not email or '@' not in email or '.' not in email:
            return {"error": "E-mail inválido. Peça o e-mail completo do cliente."}

        if any(p in email.lower() for p in placeholders):
            return {"error": f"E-mail '{email}' parece ser placeholder. Peça o e-mail REAL do cliente."}

        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Calcular data de término (7 dias)
                trial_end = datetime.now() + timedelta(days=7)

                # Inserir novo teste
                cur.execute("""
                    INSERT INTO trial_users
                    (customer_id, full_name, cpf, phone, email, trial_end_date, notes, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
                    RETURNING id, full_name, email, trial_start_date, trial_end_date, status
                """, (customer_id, full_name, cpf, phone, email, trial_end, notes))

                conn.commit()
                trial = cur.fetchone()

                return {
                    "success": True,
                    "trial_id": trial['id'],
                    "message": f"Teste de 7 dias criado para {full_name}!",
                    "trial_start": str(trial['trial_start_date']),
                    "trial_end": str(trial['trial_end_date']),
                    "status": trial['status']
                }
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": f"Erro ao criar teste: {str(e)}"}
        finally:
            conn.close()

    def get_trial_users(self, customer_id: int = None) -> Dict[str, Any]:
        """
        Busca usuários em teste

        Args:
            customer_id: ID do cliente (opcional, busca todos se não informado)

        Returns:
            Lista de usuários em teste
        """
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if customer_id:
                    cur.execute("""
                        SELECT * FROM trial_users
                        WHERE customer_id = %s
                        ORDER BY created_at DESC
                    """, (customer_id,))
                else:
                    cur.execute("""
                        SELECT * FROM trial_users
                        ORDER BY created_at DESC
                        LIMIT 50
                    """)

                trials = cur.fetchall()
                return {
                    "success": True,
                    "count": len(trials),
                    "trials": [dict(trial) for trial in trials]
                }
        except psycopg2.Error as e:
            return {"error": f"Erro ao buscar testes: {str(e)}"}
        finally:
            conn.close()

    def get_active_trials(self) -> Dict[str, Any]:
        """
        Busca todos os testes ativos (ainda não expirados)

        Returns:
            Lista de testes ativos
        """
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM trial_users
                    WHERE status = 'active'
                    AND trial_end_date > CURRENT_TIMESTAMP
                    ORDER BY trial_end_date ASC
                """)

                trials = cur.fetchall()
                return {
                    "success": True,
                    "count": len(trials),
                    "trials": [dict(trial) for trial in trials]
                }
        except psycopg2.Error as e:
            return {"error": f"Erro ao buscar testes ativos: {str(e)}"}
        finally:
            conn.close()

    def get_expired_trials(self) -> Dict[str, Any]:
        """
        Busca testes que expiraram e precisam de follow-up

        Returns:
            Lista de testes expirados que não foram convertidos
        """
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT t.*, c.phone, c.name
                    FROM trial_users t
                    JOIN customers c ON t.customer_id = c.id
                    WHERE t.trial_end_date < CURRENT_TIMESTAMP
                    AND t.status = 'active'
                    ORDER BY t.trial_end_date DESC
                """)

                trials = cur.fetchall()
                return {
                    "success": True,
                    "count": len(trials),
                    "message": f"{len(trials)} testes expirados precisam de follow-up",
                    "trials": [dict(trial) for trial in trials]
                }
        except psycopg2.Error as e:
            return {"error": f"Erro ao buscar testes expirados: {str(e)}"}
        finally:
            conn.close()

    def update_trial_status(self, trial_id: int, status: str, notes: str = None) -> Dict[str, Any]:
        """
        Atualiza o status de um teste

        Args:
            trial_id: ID do teste
            status: Novo status ('active', 'expired', 'converted', 'cancelled')
            notes: Observações sobre a mudança (opcional)

        Returns:
            Informações atualizadas do teste
        """
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    UPDATE trial_users
                    SET status = %s,
                        notes = COALESCE(%s, notes),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, full_name, status, updated_at
                """, (status, notes, trial_id))

                conn.commit()
                trial = cur.fetchone()

                if trial:
                    return {
                        "success": True,
                        "message": f"Status atualizado para '{status}'",
                        "trial": dict(trial)
                    }
                else:
                    return {"error": "Teste não encontrado"}
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": f"Erro ao atualizar status: {str(e)}"}
        finally:
            conn.close()

    def convert_trial_to_paid(self, trial_id: int, plan_name: str) -> Dict[str, Any]:
        """
        Marca um teste como convertido para plano pago

        Args:
            trial_id: ID do teste
            plan_name: Nome do plano que o usuário assinou

        Returns:
            Confirmação da conversão
        """
        conn = self._get_connection()
        if not conn:
            return {"error": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    UPDATE trial_users
                    SET status = 'converted',
                        converted_to_plan = %s,
                        conversion_date = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, full_name, converted_to_plan, conversion_date
                """, (plan_name, trial_id))

                conn.commit()
                trial = cur.fetchone()

                if trial:
                    return {
                        "success": True,
                        "message": f"🎉 {trial['full_name']} converteu para {plan_name}!",
                        "trial": dict(trial)
                    }
                else:
                    return {"error": "Teste não encontrado"}
        except psycopg2.Error as e:
            conn.rollback()
            return {"error": f"Erro ao converter teste: {str(e)}"}
        finally:
            conn.close()
