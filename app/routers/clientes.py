# ============================================================
# routers/clientes.py — CRUD de clientes (ADM e Vendedor)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Cliente
from app.schemas import ClienteCreate, ClienteUpdate, ClienteOut
from app.dependencies import require_vendedor

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/", response_model=ClienteOut, status_code=201)
def criar(dados: ClienteCreate, db: Session = Depends(get_db), user=Depends(require_vendedor)):
    """Cadastra cliente e registra qual vendedor o cadastrou."""
    if db.query(Cliente).filter(Cliente.cpf == dados.cpf).first():
        raise HTTPException(400, "CPF já cadastrado")
    c = Cliente(**dados.model_dump(), vendedor_cpf=user.cpf)
    db.add(c); db.commit(); db.refresh(c)
    return c


@router.get("/", response_model=List[ClienteOut])
def listar(db: Session = Depends(get_db), _=Depends(require_vendedor)):
    """Lista todos os clientes."""
    return db.query(Cliente).all()


@router.put("/{cpf}", response_model=ClienteOut)
def atualizar(cpf: str, dados: ClienteUpdate,
              db: Session = Depends(get_db), _=Depends(require_vendedor)):
    """Atualiza cliente pelo CPF."""
    c = db.query(Cliente).filter(Cliente.cpf == cpf).first()
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    for k, val in dados.model_dump(exclude_unset=True).items():
        setattr(c, k, val)
    db.commit(); db.refresh(c)
    return c


@router.delete("/{cpf}", status_code=204)
def excluir(cpf: str, db: Session = Depends(get_db), _=Depends(require_vendedor)):
    """Remove cliente pelo CPF."""
    c = db.query(Cliente).filter(Cliente.cpf == cpf).first()
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    db.delete(c); db.commit()
