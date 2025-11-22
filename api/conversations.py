"""
Rotas de Conversas, Histórico e Trials
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from api.database import get_db_cursor
from api.auth import verify_token

router = APIRouter()


class TrialUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class TrialConversionRequest(BaseModel):
    plan_name: str


@router.get("/history/{customer_id}")
def get_customer_conversation_history(
    customer_id: int,
    limit: int = Query(50, ge=1, le=200),
    token_data: dict = Depends(verify_token)
):
    """
    Retorna histórico de conversas de um cliente específico

    Path Params:
        - customer_id: ID do cliente

    Query Params:
        - limit: Quantidade de mensagens (default: 50, max: 200)
    """
    try:
        with get_db_cursor() as cur:
            # Buscar informações do cliente
            cur.execute("""
                SELECT c.id, c.name, c.phone, c.email, c.created_at
                FROM customers c
                WHERE c.id = %s
            """, (customer_id,))

            customer = cur.fetchone()

            if not customer:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente não encontrado"
                )

            # Buscar histórico de conversas
            cur.execute("""
                SELECT
                    id,
                    session_id,
                    user_message,
                    agent_response,
                    timestamp,
                    message_type
                FROM conversation_history
                WHERE customer_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (customer_id, limit))

            history = cur.fetchall()

            return {
                "customer": dict(customer),
                "conversation_count": len(history),
                "conversations": [dict(h) for h in history]
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )


@router.get("/recent")
def get_recent_conversations(
    limit: int = Query(20, ge=1, le=100),
    token_data: dict = Depends(verify_token)
):
    """
    Retorna conversas mais recentes de todos os clientes

    Query Params:
        - limit: Quantidade de conversas (default: 20, max: 100)
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    ch.id,
                    ch.session_id,
                    ch.customer_id,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    ch.user_message,
                    ch.agent_response,
                    ch.timestamp
                FROM conversation_history ch
                JOIN customers c ON ch.customer_id = c.id
                ORDER BY ch.timestamp DESC
                LIMIT %s
            """, (limit,))

            conversations = cur.fetchall()

            return {
                "count": len(conversations),
                "conversations": [dict(c) for c in conversations]
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar conversas: {str(e)}"
        )


@router.get("/grouped")
def get_grouped_conversations(
    limit: int = Query(20, ge=1, le=100),
    token_data: dict = Depends(verify_token)
):
    """
    Retorna conversas agrupadas por cliente (estilo WhatsApp)
    Cada cliente tem seu bloco com todo o histórico de mensagens

    Query Params:
        - limit: Quantidade de clientes (default: 20, max: 100)
    """
    try:
        with get_db_cursor() as cur:
            # Buscar clientes que têm conversas
            cur.execute("""
                SELECT DISTINCT
                    c.id,
                    c.name,
                    c.phone,
                    c.email,
                    MAX(ch.timestamp) as last_message_time,
                    COUNT(ch.id) as message_count
                FROM customers c
                INNER JOIN conversation_history ch ON c.id = ch.customer_id
                GROUP BY c.id, c.name, c.phone, c.email
                ORDER BY last_message_time DESC
                LIMIT %s
            """, (limit,))

            customers = cur.fetchall()

            result = []

            # Para cada cliente, buscar todas as mensagens
            for customer in customers:
                cur.execute("""
                    SELECT
                        id,
                        user_message,
                        agent_response,
                        timestamp,
                        message_type
                    FROM conversation_history
                    WHERE customer_id = %s
                    ORDER BY timestamp ASC
                """, (customer['id'],))

                messages = cur.fetchall()

                # Criar lista de mensagens no formato de chat
                chat_messages = []
                for msg in messages:
                    # Adicionar mensagem do usuário
                    chat_messages.append({
                        'id': f"{msg['id']}_user",
                        'sender': 'user',
                        'text': msg['user_message'],
                        'timestamp': msg['timestamp']
                    })
                    # Adicionar resposta do agente
                    chat_messages.append({
                        'id': f"{msg['id']}_agent",
                        'sender': 'agent',
                        'text': msg['agent_response'],
                        'timestamp': msg['timestamp']
                    })

                result.append({
                    'customer': {
                        'id': customer['id'],
                        'name': customer['name'],
                        'phone': customer['phone'],
                        'email': customer['email']
                    },
                    'message_count': customer['message_count'],
                    'last_message_time': customer['last_message_time'],
                    'messages': chat_messages
                })

            return {
                "count": len(result),
                "conversations": result
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar conversas agrupadas: {str(e)}"
        )


@router.get("/trials/active")
def get_active_trials(token_data: dict = Depends(verify_token)):
    """
    Retorna todos os testes de 7 dias ativos
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    t.*,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    EXTRACT(DAY FROM (t.trial_end_date - CURRENT_TIMESTAMP)) as days_remaining
                FROM trial_users t
                JOIN customers c ON t.customer_id = c.id
                WHERE t.status = 'active'
                AND t.trial_end_date > CURRENT_TIMESTAMP
                ORDER BY t.trial_end_date ASC
            """)

            trials = cur.fetchall()

            return {
                "count": len(trials),
                "trials": [dict(t) for t in trials]
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar testes ativos: {str(e)}"
        )


@router.get("/trials/expired")
def get_expired_trials(token_data: dict = Depends(verify_token)):
    """
    Retorna testes expirados que precisam de follow-up
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    t.*,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - t.trial_end_date)) as days_expired
                FROM trial_users t
                JOIN customers c ON t.customer_id = c.id
                WHERE t.trial_end_date < CURRENT_TIMESTAMP
                AND t.status = 'active'
                ORDER BY t.trial_end_date DESC
            """)

            trials = cur.fetchall()

            return {
                "count": len(trials),
                "message": f"{len(trials)} testes expirados precisam de follow-up",
                "trials": [dict(t) for t in trials]
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar testes expirados: {str(e)}"
        )


@router.get("/trials/all")
def get_all_trials(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    limit: int = Query(50, ge=1, le=200),
    token_data: dict = Depends(verify_token)
):
    """
    Retorna todos os testes com filtros opcionais

    Query Params:
        - status: Filtrar por status (active, expired, converted, cancelled)
        - limit: Quantidade de registros (default: 50, max: 200)
    """
    try:
        with get_db_cursor() as cur:
            if status:
                cur.execute("""
                    SELECT
                        t.*,
                        c.name as customer_name,
                        c.phone as customer_phone
                    FROM trial_users t
                    JOIN customers c ON t.customer_id = c.id
                    WHERE t.status = %s
                    ORDER BY t.created_at DESC
                    LIMIT %s
                """, (status, limit))
            else:
                cur.execute("""
                    SELECT
                        t.*,
                        c.name as customer_name,
                        c.phone as customer_phone
                    FROM trial_users t
                    JOIN customers c ON t.customer_id = c.id
                    ORDER BY t.created_at DESC
                    LIMIT %s
                """, (limit,))

            trials = cur.fetchall()

            return {
                "count": len(trials),
                "trials": [dict(t) for t in trials]
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar testes: {str(e)}"
        )


@router.get("/trials/{trial_id}")
def get_trial_details(trial_id: int, token_data: dict = Depends(verify_token)):
    """
    Retorna detalhes de um teste específico

    Path Params:
        - trial_id: ID do teste
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    t.*,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.email as customer_email
                FROM trial_users t
                JOIN customers c ON t.customer_id = c.id
                WHERE t.id = %s
            """, (trial_id,))

            trial = cur.fetchone()

            if not trial:
                raise HTTPException(
                    status_code=404,
                    detail="Teste não encontrado"
                )

            return {"trial": dict(trial)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar teste: {str(e)}"
        )


@router.patch("/trials/{trial_id}/status")
def update_trial_status(
    trial_id: int,
    request: TrialUpdateRequest,
    token_data: dict = Depends(verify_token)
):
    """
    Atualiza o status de um teste

    Path Params:
        - trial_id: ID do teste

    Body:
        - status: Novo status (active, expired, converted, cancelled)
        - notes: Observações opcionais
    """
    try:
        valid_statuses = ['active', 'expired', 'converted', 'cancelled']
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Status inválido. Use: {', '.join(valid_statuses)}"
            )

        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE trial_users
                SET status = %s,
                    notes = COALESCE(%s, notes),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *
            """, (request.status, request.notes, trial_id))

            trial = cur.fetchone()

            if not trial:
                raise HTTPException(
                    status_code=404,
                    detail="Teste não encontrado"
                )

            # Registrar auditoria
            cur.execute("""
                INSERT INTO audit_log (admin_id, action, details)
                VALUES (%s, %s, %s)
            """, (
                token_data['user_id'],
                f"update_trial_status",
                f"Trial ID {trial_id} status alterado para {request.status}"
            ))

            return {
                "success": True,
                "message": f"Status atualizado para '{request.status}'",
                "trial": dict(trial)
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar status: {str(e)}"
        )


@router.post("/trials/{trial_id}/convert")
def convert_trial_to_paid(
    trial_id: int,
    request: TrialConversionRequest,
    token_data: dict = Depends(verify_token)
):
    """
    Marca um teste como convertido para plano pago

    Path Params:
        - trial_id: ID do teste

    Body:
        - plan_name: Nome do plano que o usuário assinou
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE trial_users
                SET status = 'converted',
                    converted_to_plan = %s,
                    conversion_date = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, full_name, converted_to_plan, conversion_date
            """, (request.plan_name, trial_id))

            trial = cur.fetchone()

            if not trial:
                raise HTTPException(
                    status_code=404,
                    detail="Teste não encontrado"
                )

            # Registrar auditoria
            cur.execute("""
                INSERT INTO audit_log (admin_id, action, details)
                VALUES (%s, %s, %s)
            """, (
                token_data['user_id'],
                "convert_trial",
                f"Trial ID {trial_id} convertido para plano {request.plan_name}"
            ))

            return {
                "success": True,
                "message": f"🎉 {trial['full_name']} converteu para {request.plan_name}!",
                "trial": dict(trial)
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao converter teste: {str(e)}"
        )


@router.get("/messages/recent")
def get_recent_messages(
    limit: int = Query(50, ge=1, le=200),
    direction: Optional[str] = Query(None, description="inbound ou outbound"),
    token_data: dict = Depends(verify_token)
):
    """
    Retorna mensagens mais recentes do log completo

    Query Params:
        - limit: Quantidade de mensagens (default: 50, max: 200)
        - direction: Filtrar por direção (inbound/outbound)
    """
    try:
        with get_db_cursor() as cur:
            if direction:
                cur.execute("""
                    SELECT
                        ml.*,
                        c.name as customer_name
                    FROM message_logs ml
                    LEFT JOIN customers c ON ml.customer_id = c.id
                    WHERE ml.direction = %s
                    ORDER BY ml.timestamp DESC
                    LIMIT %s
                """, (direction, limit))
            else:
                cur.execute("""
                    SELECT
                        ml.*,
                        c.name as customer_name
                    FROM message_logs ml
                    LEFT JOIN customers c ON ml.customer_id = c.id
                    ORDER BY ml.timestamp DESC
                    LIMIT %s
                """, (limit,))

            messages = cur.fetchall()

            return {
                "count": len(messages),
                "messages": [dict(m) for m in messages]
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar mensagens: {str(e)}"
        )
