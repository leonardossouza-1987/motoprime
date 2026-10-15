# ============================================================
# auth.py — Autenticação e geração de JWT
# ============================================================
# Responsável por:
#   1. Hashear senhas (bcrypt)
#   2. Verificar senhas no login
#   3. Gerar tokens JWT
#   4. Extrair o usuário autenticado de um token
# ============================================================

from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db, settings
from app.models import Funcionario


# Contexto de hashing com bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Indica ao FastAPI onde o cliente obtém o token (usado no Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_senha(senha: str) -> str:
    """Transforma senha em hash bcrypt (armazenado no banco)."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara senha em texto puro com o hash salvo."""
    return pwd_context.verify(senha, senha_hash)


def criar_token(data: dict) -> str:
    """
    Cria um JWT assinado.
    O dict `data` deve conter pelo menos {"sub": <cpf>, "cargo": <cargo>}.
    Adiciona automaticamente a expiração (exp).
    """
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> Funcionario:
    """
    Dependência do FastAPI que:
      1. Lê o token JWT do header Authorization: Bearer <token>
      2. Decodifica e valida assinatura + expiração
      3. Busca o funcionário pelo CPF (sub)
      4. Retorna o objeto Funcionario OU levanta 401
    """
    credencial_invalida = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        cpf = payload.get("sub")
        if not cpf:
            raise credencial_invalida
    except JWTError:
        raise credencial_invalida

    user = db.query(Funcionario).filter(Funcionario.cpf == cpf).first()
    if not user:
        raise credencial_invalida
    return user
