# ============================================================
# models.py — Modelos ORM (tabelas do banco de dados)
# ============================================================
# Cada classe representa uma tabela no MySQL.
# Enums abaixo definem os valores válidos para campos específicos.
# ============================================================

from sqlalchemy import (Column, String, Integer, Date, DateTime, Numeric,
                        Enum, ForeignKey, Text, func)
from app.database import Base
import enum


# ---------- ENUMS (valores fixos aceitos pelo banco) ----------

class CargoEnum(str, enum.Enum):
    """Cargos possíveis de um funcionário."""
    ADM = "adm"           # Acesso total
    VENDEDOR = "vendedor" # Clientes e transações
    OFICINA = "oficina"   # Ordens de serviço


class CategoriaVeiculo(str, enum.Enum):
    """Classificação do veículo."""
    NOVO = "novo"
    USADO = "usado"


class SituacaoVeiculo(str, enum.Enum):
    """Estado atual do veículo no estoque."""
    DISPONIVEL = "disponivel"   # Pode ser vendido
    VENDIDO = "vendido"         # Já vendido
    RESERVADO = "reservado"     # Reservado para um cliente


class TipoTransacao(str, enum.Enum):
    """Tipos de movimentação financeira."""
    VENDA = "venda"           # Saída de veículo (receita)
    DEVOLUCAO = "devolucao"   # Retorno do veículo
    RECEITA = "receita"       # Entrada financeira avulsa
    DESPESA = "despesa"       # Saída financeira avulsa


class StatusOS(str, enum.Enum):
    """Status de uma ordem de serviço."""
    ABERTA = "aberta"         # Em andamento
    FECHADA = "fechada"       # Finalizada


# ---------- TABELA: funcionarios ----------

class Funcionario(Base):
    """
    Representa um funcionário da concessionária (ADM, Vendedor ou Oficina).
    A chave primária é o CPF (11 dígitos, sem pontuação).
    """
    __tablename__ = "funcionarios"

    cpf = Column(String(11), primary_key=True, index=True)       # PK: CPF
    nome = Column(String(80), nullable=False)
    sobrenome = Column(String(80), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(120), unique=True, nullable=False)     # Único
    telefone = Column(String(20), nullable=False)
    senha_hash = Column(String(255), nullable=False)             # Hash bcrypt
    cargo = Column(Enum(CargoEnum), nullable=False)
    data_cadastro = Column(DateTime, server_default=func.now())  # Preenchido pelo MySQL


# ---------- TABELA: clientes ----------

class Cliente(Base):
    """
    Cliente da concessionária. PK = CPF.
    Guarda referência ao vendedor que o cadastrou.
    """
    __tablename__ = "clientes"

    cpf = Column(String(11), primary_key=True, index=True)
    nome = Column(String(80), nullable=False)
    sobrenome = Column(String(80), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(120), nullable=False)
    telefone = Column(String(20), nullable=False)
    data_cadastro = Column(DateTime, server_default=func.now())
    vendedor_cpf = Column(String(11), ForeignKey("funcionarios.cpf"))  # FK


# ---------- TABELA: veiculos ----------

class Veiculo(Base):
    """
    Veículo do estoque. PK = chassi (17 caracteres).
    Campos placa e quilometragem foram adicionados para melhor gestão.
    """
    __tablename__ = "veiculos"

    chassi = Column(String(17), primary_key=True, index=True)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(80), nullable=False)
    ano = Column(Integer, nullable=False)
    categoria = Column(Enum(CategoriaVeiculo), nullable=False)
    situacao = Column(Enum(SituacaoVeiculo), default=SituacaoVeiculo.DISPONIVEL)
    preco = Column(Numeric(12, 2), nullable=False)               # Valor de venda
    placa = Column(String(8), nullable=True)                     # Placa (opcional)
    quilometragem = Column(Integer, default=0)                   # KM rodados
    descricao = Column(Text)                                     # Observações livres


# ---------- TABELA: transacoes ----------

class Transacao(Base):
    """
    Registra vendas, devoluções e movimentações financeiras.
    Liga cliente + veículo + vendedor.
    """
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(Enum(TipoTransacao), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    data = Column(DateTime, server_default=func.now())
    descricao = Column(Text)
    cliente_cpf = Column(String(11), ForeignKey("clientes.cpf"), nullable=True)
    veiculo_chassi = Column(String(17), ForeignKey("veiculos.chassi"), nullable=True)
    vendedor_cpf = Column(String(11), ForeignKey("funcionarios.cpf"), nullable=True)


# ---------- TABELA: ordens_servico ----------

class OrdemServico(Base):
    """
    Ordem de serviço da oficina.
    Nasce aberta, e ao ser fechada recebe data_fechamento e valor final.
    """
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(Text, nullable=False)
    valor = Column(Numeric(12, 2), default=0)
    status = Column(Enum(StatusOS), default=StatusOS.ABERTA)
    data_abertura = Column(DateTime, server_default=func.now())
    data_fechamento = Column(DateTime, nullable=True)
    cliente_cpf = Column(String(11), ForeignKey("clientes.cpf"), nullable=False)
    veiculo_chassi = Column(String(17), ForeignKey("veiculos.chassi"), nullable=False)
    mecanico_cpf = Column(String(11), ForeignKey("funcionarios.cpf"), nullable=False)
