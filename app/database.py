# ============================================================
# database.py — Configuração da conexão com o banco de dados
# ============================================================
# Este módulo é responsável por:
#   1. Ler as variáveis de ambiente (.env)
#   2. Criar a engine SQLAlchemy
#   3. Fornecer sessões para as rotas (via get_db)
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Carrega configurações do arquivo .env automaticamente."""
    DATABASE_URL: str                                    # URL do MySQL (mysql+pymysql://...)
    SECRET_KEY: str                                      # Chave usada para assinar JWTs
    ALGORITHM: str = "HS256"                             # Algoritmo de assinatura do JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480               # Validade do token (8 horas)

    class Config:
        env_file = ".env"                                # Lê variáveis desse arquivo


# Instância única de configurações do sistema
settings = Settings()

# Engine do SQLAlchemy — mantém o pool de conexões com o MySQL.
# pool_pre_ping=True verifica se a conexão está viva antes de usar.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Fábrica de sessões. Cada requisição HTTP terá sua própria sessão.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa: todos os modelos ORM herdam dessa classe.
Base = declarative_base()


def get_db():
    """
    Dependência do FastAPI que fornece uma sessão de banco.
    Abre a sessão, entrega para a rota, e fecha ao final (mesmo em caso de erro).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
