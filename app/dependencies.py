# ============================================================
# dependencies.py — Autorização por cargo
# ============================================================
# Dependências que garantem que apenas certos cargos
# possam acessar determinadas rotas.
# ============================================================

from fastapi import Depends, HTTPException, status
from app.auth import get_current_user
from app.models import Funcionario, CargoEnum


def require_adm(user: Funcionario = Depends(get_current_user)):
    """Só permite acesso se o funcionário for ADM."""
    if user.cargo != CargoEnum.ADM:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a ADM")
    return user


def require_vendedor(user: Funcionario = Depends(get_current_user)):
    """Permite Vendedor e ADM (ADM é superusuário)."""
    if user.cargo not in (CargoEnum.VENDEDOR, CargoEnum.ADM):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a Vendedor")
    return user


def require_oficina(user: Funcionario = Depends(get_current_user)):
    """Permite Oficina e ADM."""
    if user.cargo not in (CargoEnum.OFICINA, CargoEnum.ADM):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito à Oficina")
    return user
