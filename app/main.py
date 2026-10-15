# ============================================================
# main.py — Aplicação FastAPI principal
# ============================================================
# Ponto de entrada do sistema MotoPrime.
# Responsável por:
#   1. Criar as tabelas no banco (se não existirem)
#   2. Instanciar o app FastAPI
#   3. Montar arquivos estáticos (CSS/HTML/JS)
#   4. Registrar os routers da API
#   5. Servir as páginas HTML do frontend
# ============================================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import Base, engine
from app import models  # importa para registrar todos os modelos no metadata
from app.routers import (auth_router, funcionarios, veiculos,
                         clientes, transacoes, ordens_servico)


# ---------- CRIAÇÃO DAS TABELAS ----------
# Gera as tabelas no MySQL conforme definidas em models.py.
# Se já existirem, não faz nada (idempotente).
Base.metadata.create_all(bind=engine)


# ---------- INSTÂNCIA DO APP ----------
app = FastAPI(
    title="MotoPrime API",
    version="1.0.0",
    description="Sistema de gestão para concessionária de motocicletas"
)


# ---------- ARQUIVOS ESTÁTICOS ----------
# Tudo em app/static fica acessível em /static/*
# (CSS, JS, imagens, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ---------- REGISTRO DOS ROUTERS ----------
# Cada router cuida de uma área do sistema.
app.include_router(auth_router.router)      # POST /auth/login
app.include_router(funcionarios.router)     # /funcionarios/*
app.include_router(veiculos.router)         # /veiculos/*
app.include_router(clientes.router)         # /clientes/*
app.include_router(transacoes.router)       # /transacoes/*
app.include_router(ordens_servico.router)   # /ordens-servico/*


# ---------- ROTAS DE PÁGINA (HTML) ----------
# Cada rota devolve um arquivo HTML estático.

@app.get("/", include_in_schema=False)
def root():
    """Tela de login."""
    return FileResponse("app/static/index.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    """Dashboard pós-login."""
    return FileResponse("app/static/dashboard.html")


@app.get("/funcionarios", include_in_schema=False)
def funcionarios_page():
    """Página de gestão de funcionários (ADM)."""
    return FileResponse("app/static/funcionarios.html")


@app.get("/veiculos", include_in_schema=False)
def veiculos_page():
    """Página de gestão de veículos."""
    return FileResponse("app/static/veiculos.html")


@app.get("/clientes", include_in_schema=False)
def clientes_page():
    """Página de gestão de clientes."""
    return FileResponse("app/static/clientes.html")


@app.get("/transacoes", include_in_schema=False)
def transacoes_page():
    """Página de transações (vendas/devoluções)."""
    return FileResponse("app/static/transacoes.html")


@app.get("/ordens", include_in_schema=False)
def ordens_page():
    """Página de ordens de serviço."""
    return FileResponse("app/static/ordens.html")
