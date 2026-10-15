# ============================================================
# routers/ordens_servico.py — Ordens de serviço da oficina
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import OrdemServico, StatusOS, Veiculo, Cliente
from app.schemas import OSCreate, OSFechar, OSOut
from app.dependencies import require_oficina

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])


@router.post("/", response_model=OSOut, status_code=201)
def abrir(dados: OSCreate, db: Session = Depends(get_db), user=Depends(require_oficina)):
    """Abre uma nova OS. Verifica cliente e veículo."""
    if not db.query(Cliente).filter(Cliente.cpf == dados.cliente_cpf).first():
        raise HTTPException(404, "Cliente não encontrado")
    if not db.query(Veiculo).filter(Veiculo.chassi == dados.veiculo_chassi).first():
        raise HTTPException(404, "Veículo não encontrado")

    os = OrdemServico(descricao=dados.descricao, valor=dados.valor,
                      cliente_cpf=dados.cliente_cpf,
                      veiculo_chassi=dados.veiculo_chassi,
                      mecanico_cpf=user.cpf)
    db.add(os); db.commit(); db.refresh(os)
    return os


@router.get("/", response_model=List[OSOut])
def listar(db: Session = Depends(get_db), _=Depends(require_oficina)):
    """Lista todas as OS."""
    return db.query(OrdemServico).order_by(OrdemServico.data_abertura.desc()).all()


@router.get("/minhas", response_model=List[OSOut])
def minhas(db: Session = Depends(get_db), user=Depends(require_oficina)):
    """Lista apenas as OS do mecânico logado."""
    return (db.query(OrdemServico)
            .filter(OrdemServico.mecanico_cpf == user.cpf)
            .order_by(OrdemServico.data_abertura.desc())
            .all())


@router.put("/{os_id}/fechar", response_model=OSOut)
def fechar(os_id: int, dados: OSFechar,
           db: Session = Depends(get_db), _=Depends(require_oficina)):
    """Fecha uma OS. Define valor final e data_fechamento."""
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(404, "OS não encontrada")
    if os.status == StatusOS.FECHADA:
        raise HTTPException(400, "OS já fechada")

    os.valor = dados.valor
    os.status = StatusOS.FECHADA
    os.data_fechamento = datetime.utcnow()
    db.commit(); db.refresh(os)
    return os
