# ============================================================
# routers/veiculos.py — CRUD de veículos
# ============================================================
# GET (listar)     -> qualquer usuário autenticado (vendedor consulta estoque)
# POST/PUT/DELETE  -> somente ADM
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Veiculo
from app.schemas import VeiculoCreate, VeiculoUpdate, VeiculoOut
from app.dependencies import require_adm
from app.auth import get_current_user

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


def _any_authenticated(user=Depends(get_current_user)):
    """Dependência que apenas exige um usuário logado (qualquer cargo)."""
    return user


@router.post("/", response_model=VeiculoOut, status_code=201)
def criar(dados: VeiculoCreate, db: Session = Depends(get_db), _=Depends(require_adm)):
    """Cadastra veículo. Chassi deve ser único. Apenas ADM."""
    if db.query(Veiculo).filter(Veiculo.chassi == dados.chassi).first():
        raise HTTPException(400, "Chassi já cadastrado")
    v = Veiculo(**dados.model_dump())
    db.add(v); db.commit(); db.refresh(v)
    return v


@router.get("/", response_model=List[VeiculoOut])
def listar(db: Session = Depends(get_db), _=Depends(_any_authenticated)):
    """Lista todos os veículos. Qualquer usuário autenticado."""
    return db.query(Veiculo).all()


@router.get("/disponiveis", response_model=List[VeiculoOut])
def disponiveis(db: Session = Depends(get_db), _=Depends(_any_authenticated)):
    """Somente veículos com situacao='disponivel'."""
    return db.query(Veiculo).filter(Veiculo.situacao == "disponivel").all()


@router.put("/{chassi}", response_model=VeiculoOut)
def atualizar(chassi: str, dados: VeiculoUpdate,
              db: Session = Depends(get_db), _=Depends(require_adm)):
    """Atualiza veículo pelo chassi. Apenas ADM."""
    v = db.query(Veiculo).filter(Veiculo.chassi == chassi).first()
    if not v:
        raise HTTPException(404, "Veículo não encontrado")
    for k, val in dados.model_dump(exclude_unset=True).items():
        setattr(v, k, val)
    db.commit(); db.refresh(v)
    return v


@router.delete("/{chassi}", status_code=204)
def excluir(chassi: str, db: Session = Depends(get_db), _=Depends(require_adm)):
    """Remove veículo pelo chassi. Apenas ADM."""
    v = db.query(Veiculo).filter(Veiculo.chassi == chassi).first()
    if not v:
        raise HTTPException(404, "Veículo não encontrado")
    db.delete(v); db.commit()
