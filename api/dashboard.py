"""
Rotas do Dashboard - Métricas, Analytics, Estatísticas
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from api.database import get_db_cursor
from api.auth import verify_token

router = APIRouter()


@router.get("/metrics/today")
def get_today_metrics(token_data: dict = Depends(verify_token)):
    """
    Retorna métricas do dia atual

    Requer autenticação JWT
    """
    try:
        with get_db_cursor() as cur:
            today = datetime.now().date()

            # Buscar ou criar registro do dia
            cur.execute("""
                INSERT INTO attendance_metrics (date)
                VALUES (%s)
                ON CONFLICT (date) DO NOTHING
            """, (today,))

            # Buscar métricas
            cur.execute("""
                SELECT
                    date,
                    total_conversations,
                    total_trials_requested,
                    total_conversions,
                    total_messages_sent,
                    total_messages_received
                FROM attendance_metrics
                WHERE date = %s
            """, (today,))

            metrics = cur.fetchone()

            # Buscar conversas ativas agora
            cur.execute("""
                SELECT COUNT(*) as active_sessions
                FROM sessions
                WHERE status = 'active'
                AND started_at::date = %s
            """, (today,))

            active = cur.fetchone()

            return {
                "date": str(today),
                "metrics": dict(metrics) if metrics else {},
                "active_sessions": active['active_sessions'] if active else 0
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar métricas: {str(e)}"
        )


@router.get("/metrics/period")
def get_period_metrics(
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    token_data: dict = Depends(verify_token)
):
    """
    Retorna métricas de um período

    Query Params:
        - start_date: Data inicial (default: 7 dias atrás)
        - end_date: Data final (default: hoje)
    """
    try:
        # Datas padrão
        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if not start_date:
            start_date = end_date - timedelta(days=7)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    date,
                    total_conversations,
                    total_trials_requested,
                    total_conversions,
                    total_messages_sent,
                    total_messages_received
                FROM attendance_metrics
                WHERE date BETWEEN %s AND %s
                ORDER BY date DESC
            """, (start_date, end_date))

            metrics = cur.fetchall()

            # Calcular totais
            totals = {
                "total_conversations": sum(m['total_conversations'] for m in metrics),
                "total_trials": sum(m['total_trials_requested'] for m in metrics),
                "total_conversions": sum(m['total_conversions'] for m in metrics),
                "total_messages_sent": sum(m['total_messages_sent'] for m in metrics),
                "total_messages_received": sum(m['total_messages_received'] for m in metrics),
            }

            # Taxa de conversão
            conversion_rate = 0
            if totals['total_trials'] > 0:
                conversion_rate = (totals['total_conversions'] / totals['total_trials']) * 100

            return {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "daily_metrics": [dict(m) for m in metrics],
                "totals": totals,
                "conversion_rate": round(conversion_rate, 2)
            }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar métricas: {str(e)}"
        )


@router.get("/stats/summary")
def get_summary_stats(token_data: dict = Depends(verify_token)):
    """
    Retorna resumo geral de estatísticas do sistema
    """
    try:
        with get_db_cursor() as cur:
            # Total de clientes
            cur.execute("SELECT COUNT(*) as total FROM customers")
            total_customers = cur.fetchone()['total']

            # Total de testes ativos
            cur.execute("""
                SELECT COUNT(*) as total FROM trial_users
                WHERE status = 'active' AND trial_end_date > CURRENT_TIMESTAMP
            """)
            active_trials = cur.fetchone()['total']

            # Total de conversões
            cur.execute("""
                SELECT COUNT(*) as total FROM trial_users
                WHERE status = 'converted'
            """)
            conversions = cur.fetchone()['total']

            # Mensagens últimas 24h
            cur.execute("""
                SELECT COUNT(*) as total FROM message_logs
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            messages_24h = cur.fetchone()['total']

            # Sessões ativas
            cur.execute("""
                SELECT COUNT(*) as total FROM sessions
                WHERE status = 'active'
            """)
            active_sessions = cur.fetchone()['total']

            return {
                "total_customers": total_customers,
                "active_trials": active_trials,
                "total_conversions": conversions,
                "messages_last_24h": messages_24h,
                "active_sessions": active_sessions
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )


@router.get("/customers/recent")
def get_recent_customers(
    limit: int = Query(10, ge=1, le=100),
    token_data: dict = Depends(verify_token)
):
    """
    Retorna clientes mais recentes

    Query Params:
        - limit: Quantidade de registros (default: 10, max: 100)
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.name,
                    c.phone,
                    c.email,
                    c.created_at,
                    cc.business_niche,
                    cc.experience_level,
                    up.conversation_count
                FROM customers c
                LEFT JOIN customer_context cc ON c.id = cc.customer_id
                LEFT JOIN user_preferences up ON c.id = up.customer_id
                ORDER BY c.created_at DESC
                LIMIT %s
            """, (limit,))

            customers = cur.fetchall()

            return {
                "count": len(customers),
                "customers": [dict(c) for c in customers]
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar clientes: {str(e)}"
        )


@router.post("/metrics/update")
def update_metrics(token_data: dict = Depends(verify_token)):
    """
    Atualiza manualmente as métricas do dia
    (Normalmente atualizado automaticamente pelo bot)
    """
    try:
        with get_db_cursor() as cur:
            today = datetime.now().date()

            # Contar conversas do dia
            cur.execute("""
                SELECT COUNT(DISTINCT session_id) as count
                FROM conversation_history
                WHERE timestamp::date = %s
            """, (today,))
            conversations = cur.fetchone()['count']

            # Contar trials do dia
            cur.execute("""
                SELECT COUNT(*) as count
                FROM trial_users
                WHERE trial_start_date::date = %s
            """, (today,))
            trials = cur.fetchone()['count']

            # Contar conversões do dia
            cur.execute("""
                SELECT COUNT(*) as count
                FROM trial_users
                WHERE conversion_date::date = %s
            """, (today,))
            conversions = cur.fetchone()['count']

            # Contar mensagens
            cur.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE direction = 'outbound') as sent,
                    COUNT(*) FILTER (WHERE direction = 'inbound') as received
                FROM message_logs
                WHERE timestamp::date = %s
            """, (today,))
            messages = cur.fetchone()

            # Atualizar ou inserir
            cur.execute("""
                INSERT INTO attendance_metrics
                (date, total_conversations, total_trials_requested, total_conversions,
                 total_messages_sent, total_messages_received, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (date)
                DO UPDATE SET
                    total_conversations = EXCLUDED.total_conversations,
                    total_trials_requested = EXCLUDED.total_trials_requested,
                    total_conversions = EXCLUDED.total_conversions,
                    total_messages_sent = EXCLUDED.total_messages_sent,
                    total_messages_received = EXCLUDED.total_messages_received,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING *
            """, (today, conversations, trials, conversions,
                  messages['sent'], messages['received']))

            updated = cur.fetchone()

            return {
                "success": True,
                "message": "Métricas atualizadas com sucesso",
                "metrics": dict(updated)
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar métricas: {str(e)}"
        )
