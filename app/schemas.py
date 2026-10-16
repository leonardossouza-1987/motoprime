# ============================================================
# schemas.py — Esquemas Pydantic (validação de entrada/saída)
# ============================================================
# Cada schema define o "contrato" JSON dos endpoints.
# - *Create: campos aceitos ao criar
# - *Update: campos opcionais ao atualizar
# - *Out: campos retornados na resposta
# ============================================================

from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from app.models import (CargoEnum, CategoriaVeiculo, SituacaoVeiculo,
                        TipoTransacao, StatusOS)


# ---------- AUTENTICAÇÃO ----------

class Token(BaseModel):
    """Resposta do endpoint /auth/login."""
    access_token: str
    token_type: str = "bearer"
    cargo: CargoEnum
    nome: str


# ---------- FUNCIONÁRIOS ----------

class FuncionarioBase(BaseModel):
    """Campos comuns a Create e Out."""
    cpf: str = Field(..., min_length=11, max_length=11)   # CPF exatamente 11 dígitos
    nome: str
    sobrenome: str
    data_nascimento: date
    email: EmailStr                                        # Validação automática
    telefone: str
    cargo: CargoEnum


class FuncionarioCreate(FuncionarioBase):
    """Payload para criar funcionário (inclui senha em texto puro)."""
    senha: str = Field(..., min_length=6)


class FuncionarioUpdate(BaseModel):
    """Payload de atualização (todos opcionais)."""
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    data_nascimento: Optional[date] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    senha: Optional[str] = None
    cargo: Optional[CargoEnum] = None


class FuncionarioOut(FuncionarioBase):
    """Resposta (sem senha)."""
    data_cadastro: datetime
    class Config: from_attributes = True


# ---------- CLIENTES ----------

class ClienteBase(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=11)
    nome: str
    sobrenome: str
    data_nascimento: date
    email: EmailStr
    telefone: str


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    data_nascimento: Optional[date] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None


class ClienteOut(ClienteBase):
    data_cadastro: datetime
    class Config: from_attributes = True


# ---------- VEÍCULOS ----------

class VeiculoBase(BaseModel):
    chassi: str = Field(..., min_length=17, max_length=17)   # Chassi 17 chars
    marca: str
    modelo: str
    ano: int
    categoria: CategoriaVeiculo
    preco: Decimal
    placa: Optional[str] = None
    quilometragem: int = 0
    descricao: Optional[str] = None


class VeiculoCreate(VeiculoBase):
    pass


class VeiculoUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    categoria: Optional[CategoriaVeiculo] = None
    situacao: Optional[SituacaoVeiculo] = None
    preco: Optional[Decimal] = None
    placa: Optional[str] = None
    quilometragem: Optional[int] = None
    descricao: Optional[str] = None


class VeiculoOut(VeiculoBase):
    situacao: SituacaoVeiculo
    class Config: from_attributes = True


# ---------- TRANSAÇÕES ----------

class TransacaoCreate(BaseModel):
    tipo: TipoTransacao
    valor: Decimal
    descricao: Optional[str] = None
    cliente_cpf: Optional[str] = None
    veiculo_chassi: Optional[str] = None


class TransacaoOut(BaseModel):
    id: int
    tipo: TipoTransacao
    valor: Decimal
    data: datetime
    descricao: Optional[str]
    cliente_cpf: Optional[str]
    veiculo_chassi: Optional[str]
    vendedor_cpf: Optional[str]
    vendedor_nome: Optional[str] = None
    cliente_nome: Optional[str] = None
    veiculo_desc: Optional[str] = None
    class Config: from_attributes = True


# ---------- ORDENS DE SERVIÇO ----------

class OSCreate(BaseModel):
    descricao: str
    valor: Decimal = Decimal("0")
    cliente_cpf: str
    veiculo_chassi: str


class OSFechar(BaseModel):
    valor: Decimal


class OSOut(BaseModel):
    id: int
    descricao: str
    valor: Decimal
    status: StatusOS
    data_abertura: datetime
    data_fechamento: Optional[datetime]
    cliente_cpf: str
    veiculo_chassi: str
    mecanico_cpf: str
    class Config: from_attributes = True
