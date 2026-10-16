# ============================================================
# routers/transacoes.py — Vendas, devoluções e financeiro
# ============================================================
# Regra: ao vender, veículo vira 'vendido'.
#        ao devolver, veículo volta para 'disponivel'.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Transacao, Veiculo, Cliente, Funcionario, TipoTransacao, SituacaoVeiculo
from app.schemas import TransacaoCreate, TransacaoOut
from app.dependencies import require_vendedor, require_adm


def _to_out(t, db):
    """Converte Transacao em dict com nomes amigáveis."""
    vendedor = db.query(Funcionario).filter(Funcionario.cpf == t.vendedor_cpf).first() if t.vendedor_cpf else None
    cliente = db.query(Cliente).filter(Cliente.cpf == t.cliente_cpf).first() if t.cliente_cpf else None
    veiculo = db.query(Veiculo).filter(Veiculo.chassi == t.veiculo_chassi).first() if t.veiculo_chassi else None
    return {
        "id": t.id,
        "tipo": t.tipo,
        "valor": t.valor,
        "data": t.data,
        "descricao": t.descricao,
        "cliente_cpf": t.cliente_cpf,
        "veiculo_chassi": t.veiculo_chassi,
        "vendedor_cpf": t.vendedor_cpf,
        "vendedor_nome": f"{vendedor.nome} {vendedor.sobrenome}" if vendedor else None,
        "cliente_nome": f"{cliente.nome} {cliente.sobrenome}" if cliente else None,
        "veiculo_desc": f"{veiculo.marca} {veiculo.modelo}" if veiculo else None,
    }


router = APIRouter(prefix="/transacoes", tags=["Transações"])


@router.post("/venda", response_model=TransacaoOut, status_code=201)
def venda(dados: TransacaoCreate, db: Session = Depends(get_db), user=Depends(require_vendedor)):
    """Registra uma venda. Veículo precisa estar 'disponivel'."""
    if not dados.cliente_cpf or not dados.veiculo_chassi:
        raise HTTPException(400, "Cliente e veículo são obrigatórios")
    if not db.query(Cliente).filter(Cliente.cpf == dados.cliente_cpf).first():
        raise HTTPException(404, "Cliente não encontrado")
    v = db.query(Veiculo).filter(Veiculo.chassi == dados.veiculo_chassi).first()
    if not v:
        raise HTTPException(404, "Veículo não encontrado")
    if v.situacao == SituacaoVeiculo.VENDIDO:
        raise HTTPException(400, "Veículo já vendido")

    # Cria a transação
    t = Transacao(tipo=TipoTransacao.VENDA, valor=dados.valor or v.preco,
                  descricao=dados.descricao, cliente_cpf=dados.cliente_cpf,
                  veiculo_chassi=dados.veiculo_chassi, vendedor_cpf=user.cpf)

    # Marca o veículo como vendido
    v.situacao = SituacaoVeiculo.VENDIDO

    db.add(t); db.commit(); db.refresh(t)
    return _to_out(t, db)


@router.post("/devolucao", response_model=TransacaoOut, status_code=201)
def devolucao(dados: TransacaoCreate, db: Session = Depends(get_db), user=Depends(require_vendedor)):
    """Registra devolução. Veículo volta a 'disponivel'."""
    v = db.query(Veiculo).filter(Veiculo.chassi == dados.veiculo_chassi).first()
    if not v:
        raise HTTPException(404, "Veículo não encontrado")

    t = Transacao(tipo=TipoTransacao.DEVOLUCAO, valor=dados.valor or v.preco,
                  descricao=dados.descricao or "Devolução",
                  cliente_cpf=dados.cliente_cpf,
                  veiculo_chassi=dados.veiculo_chassi, vendedor_cpf=user.cpf)
    v.situacao = SituacaoVeiculo.DISPONIVEL

    db.add(t); db.commit(); db.refresh(t)
    return _to_out(t, db)


@router.post("/financeiro", response_model=TransacaoOut, status_code=201)
def lancar_financeiro(dados: TransacaoCreate, db: Session = Depends(get_db), _=Depends(require_adm)):
    """Lançamento avulso de receita ou despesa. Apenas ADM."""
    if dados.tipo not in (TipoTransacao.RECEITA, TipoTransacao.DESPESA):
        raise HTTPException(400, "Tipo deve ser receita ou despesa")
    t = Transacao(**dados.model_dump())
    db.add(t); db.commit(); db.refresh(t)
    return _to_out(t, db)


@router.get("/", response_model=List[TransacaoOut])
def historico_geral(db: Session = Depends(get_db), _=Depends(require_adm)):
    """Histórico completo (ADM)."""
    rows = db.query(Transacao).order_by(Transacao.data.desc()).all()
    return [_to_out(t, db) for t in rows]


@router.get("/minhas", response_model=List[TransacaoOut])
def minhas_vendas(db: Session = Depends(get_db), user=Depends(require_vendedor)):
    """Histórico do próprio vendedor (vendas + devoluções)."""
    rows = (db.query(Transacao)
            .filter(Transacao.vendedor_cpf == user.cpf,
                    Transacao.tipo.in_([TipoTransacao.VENDA, TipoTransacao.DEVOLUCAO]))
            .order_by(Transacao.data.desc())
            .all())
    return [_to_out(t, db) for t in rows]
