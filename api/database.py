"""
Gerenciador de conexões com o banco de dados PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
import logging

logger = logging.getLogger(__name__)

# Configurações do banco
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "spdrop_db"),
    "user": os.getenv("DB_USER", "spdrop_user"),
    "password": os.getenv("DB_PASSWORD", "spdrop_password")
}


@contextmanager
def get_db_connection():
    """
    Context manager para conexões com o banco de dados

    Uso:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM customers")
                results = cur.fetchall()
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro no banco de dados: {e}")
        raise
    finally:
        if conn:
            conn.close()


@contextmanager
def get_db_cursor():
    """
    Context manager para cursor com RealDictCursor (retorna dicionários)

    Uso:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM customers")
            results = cur.fetchall()
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()


def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
    except Exception as e:
        logger.error(f"Falha ao conectar no banco: {e}")
        return False
