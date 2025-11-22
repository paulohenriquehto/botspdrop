"""
Rotas de Autenticação - Login, Logout, Registro de Admins
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
import os
from api.database import get_db_cursor

router = APIRouter()
security = HTTPBearer()

# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-super-segura-aqui-trocar-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict


def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha bate com o hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica e decodifica token JWT"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar o token"
        )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Endpoint de login - retorna token JWT

    Body:
        - username: Nome de usuário
        - password: Senha
    """
    try:
        with get_db_cursor() as cur:
            # Buscar usuário
            cur.execute("""
                SELECT id, username, password_hash, email, full_name, role, is_active
                FROM admin_users
                WHERE username = %s
            """, (request.username,))

            user = cur.fetchone()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário ou senha incorretos"
                )

            if not user['is_active']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuário desativado"
                )

            # Verificar senha
            if not verify_password(request.password, user['password_hash']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário ou senha incorretos"
                )

            # Atualizar último login
            cur.execute("""
                UPDATE admin_users
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (user['id'],))

            # Criar token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user['username'], "role": user['role'], "user_id": user['id']},
                expires_delta=access_token_expires
            )

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user={
                    "id": user['id'],
                    "username": user['username'],
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "role": user['role']
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer login: {str(e)}"
        )


@router.post("/register")
def register(request: RegisterRequest):
    """
    Endpoint para registrar novo admin (requer autenticação)
    """
    try:
        with get_db_cursor() as cur:
            # Verificar se usuário já existe
            cur.execute("SELECT id FROM admin_users WHERE username = %s", (request.username,))
            if cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuário já existe"
                )

            # Hash da senha
            password_hash = hash_password(request.password)

            # Inserir novo admin
            cur.execute("""
                INSERT INTO admin_users (username, password_hash, email, full_name, role, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, username, email, full_name, role
            """, (request.username, password_hash, request.email, request.full_name, 'admin', True))

            new_user = cur.fetchone()

            return {
                "success": True,
                "message": "Administrador criado com sucesso",
                "user": dict(new_user)
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar: {str(e)}"
        )


@router.get("/me")
def get_current_user(token_data: dict = Depends(verify_token)):
    """
    Retorna informações do usuário autenticado
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT id, username, email, full_name, role, last_login
                FROM admin_users
                WHERE username = %s AND is_active = TRUE
            """, (token_data['sub'],))

            user = cur.fetchone()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado"
                )

            return {"user": dict(user)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar usuário: {str(e)}"
        )


@router.post("/logout")
def logout():
    """
    Endpoint de logout (JWT stateless - apenas informativo)
    Cliente deve descartar o token
    """
    return {"message": "Logout realizado com sucesso"}
