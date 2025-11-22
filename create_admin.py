"""
Script para criar o primeiro usuário admin

Uso:
    python create_admin.py
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "spdrop_db"),
    "user": os.getenv("DB_USER", "spdrop_user"),
    "password": os.getenv("DB_PASSWORD", "spdrop_password")
}


def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_admin_user():
    """Cria o primeiro usuário admin"""
    print("=" * 60)
    print("  CRIAÇÃO DE USUÁRIO ADMINISTRADOR - SPDrop Dashboard")
    print("=" * 60)
    print()

    # Coletar informações
    username = input("Username (login): ").strip()
    if not username:
        print("❌ Username não pode ser vazio!")
        return

    password = input("Senha: ").strip()
    if not password:
        print("❌ Senha não pode ser vazia!")
        return

    email = input("E-mail (opcional): ").strip() or None
    full_name = input("Nome completo (opcional): ").strip() or None

    print("\n⏳ Criando usuário...")

    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Verificar se usuário já existe
        cur.execute("SELECT id FROM admin_users WHERE username = %s", (username,))
        if cur.fetchone():
            print(f"❌ Erro: Usuário '{username}' já existe!")
            conn.close()
            return

        # Hash da senha
        password_hash = hash_password(password)

        # Inserir novo admin
        cur.execute("""
            INSERT INTO admin_users (username, password_hash, email, full_name, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, username, email, full_name, role, created_at
        """, (username, password_hash, email, full_name, 'admin', True))

        user = cur.fetchone()
        conn.commit()

        print("\n" + "=" * 60)
        print("  ✅ USUÁRIO CRIADO COM SUCESSO!")
        print("=" * 60)
        print(f"  ID:           {user['id']}")
        print(f"  Username:     {user['username']}")
        print(f"  E-mail:       {user['email'] or 'N/A'}")
        print(f"  Nome:         {user['full_name'] or 'N/A'}")
        print(f"  Role:         {user['role']}")
        print(f"  Criado em:    {user['created_at']}")
        print("=" * 60)
        print()
        print("🚀 Você já pode fazer login no dashboard com essas credenciais!")
        print()

        conn.close()

    except psycopg2.Error as e:
        print(f"\n❌ Erro no banco de dados: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
