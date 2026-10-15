# ============================================================
# routers/funcionarios.py — CRUD de funcionários (somente ADM)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Funcionario
from app.schemas import FuncionarioCreate, FuncionarioUpdate, FuncionarioOut
from app.auth import hash_senha
from app.dependencies import require_adm

router = APIRouter(prefix="/funcionarios", tags=["Funcionários"])


@router.post("/", response_model=FuncionarioOut, status_code=201)
def criar(dados: FuncionarioCreate, db: Session = Depends(get_db), _=Depends(require_adm)):
    """Cadastra um novo funcionário. Apenas ADM."""
    # Verifica duplicatas
    if db.query(Funcionario).filter(Funcionario.cpf == dados.cpf).first():
        raise HTTPException(400, "CPF já cadastrado")
    if db.query(Funcionario).filter(Funcionario.email == dados.email).first():
        raise HTTPException(400, "E-mail já cadastrado")

    # Cria com senha hasheada
    func = Funcionario(**dados.model_dump(exclude={"senha"}),
                       senha_hash=hash_senha(dados.senha))
    db.add(func); db.commit(); db.refresh(func)
    return func


@router.get("/", response_model=List[FuncionarioOut])
def listar(db: Session = Depends(get_db), _=Depends(require_adm)):
    """Lista todos os funcionários. Apenas ADM."""
    return db.query(Funcionario).all()


@router.put("/{cpf}", response_model=FuncionarioOut)
def atualizar(cpf: str, dados: FuncionarioUpdate,
              db: Session = Depends(get_db), _=Depends(require_adm)):
    """Atualiza funcionário pelo CPF. Senha é opcional e sofre hash se enviada."""
    func = db.query(Funcionario).filter(Funcionario.cpf == cpf).first()
    if not func:
        raise HTTPException(404, "Funcionário não encontrado")

    payload = dados.model_dump(exclude_unset=True)
    if "senha" in payload:
        func.senha_hash = hash_senha(payload.pop("senha"))
    for k, v in payload.items():
        setattr(func, k, v)

    db.commit(); db.refresh(func)
    return func


@router.delete("/{cpf}", status_code=204)
def excluir(cpf: str, db: Session = Depends(get_db), _=Depends(require_adm)):
    """Remove funcionário pelo CPF. Apenas ADM."""
    func = db.query(Funcionario).filter(Funcionario.cpf == cpf).first()
    if not func:
        raise HTTPException(404, "Funcionário não encontrado")
    db.delete(func); db.commit()
