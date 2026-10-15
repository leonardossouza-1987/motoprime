# ============================================================
# routers/auth_router.py — Endpoint de login
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Funcionario
from app.schemas import Token
from app.auth import verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Recebe CPF (username) + senha via form-urlencoded.
    Retorna JWT + cargo + nome do funcionário.
    """
    # Busca funcionário pelo CPF
    user = db.query(Funcionario).filter(Funcionario.cpf == form.username).first()

    # Valida existência e senha (bcrypt)
    if not user or not verificar_senha(form.password, user.senha_hash):
        raise HTTPException(401, "CPF ou senha inválidos")

    # Gera token JWT com CPF (sub) e cargo
    token = criar_token({"sub": user.cpf, "cargo": user.cargo.value})
    return Token(access_token=token, cargo=user.cargo, nome=f"{user.nome} {user.sobrenome}")
