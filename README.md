# 🏍️ MotoPrime

### Sistema de Gestão para Concessionária de Motocicletas


**Trabalho final — Disciplina de Integração de Competências · Curso Back-end**

---

## 📖 Sobre o Projeto

**MotoPrime** é um sistema web completo para gestão de concessionárias de motocicletas. Desenvolvido com **FastAPI** e **MySQL**, atende **três perfis de usuários** com permissões distintas.

**Aluno:** Leonardo S. Souza · RA 88389823
**Curso:** Back-end
**Disciplina:** Integração de Competências
**Data:** Outubro / 2026

---

## ✨ Funcionalidades

### 🧑‍💼 Administrador
- Gerenciar funcionários (CRUD)
- Gerenciar veículos (CRUD)
- Gerenciar clientes (CRUD)
- Ver todas as transações
- Ver todas as ordens de serviço

### 🧑‍💻 Vendedor
- Gerenciar clientes (CRUD)
- Consultar estoque
- Realizar vendas e devoluções
- Ver apenas suas próprias vendas

### 🔧 Oficina
- Abrir e fechar ordens de serviço
- Consultar estoque
- Ver apenas suas próprias OS

---

## 🛠️ Tecnologias

**Backend:** Python 3.12 · FastAPI · SQLAlchemy · Pydantic · JWT · bcrypt
**Banco:** MySQL 8.0
**Frontend:** HTML5 · CSS3 · JavaScript
**Design:** Dark mode inspirado em Tesla, BYD e NIO

---

## 🏗️ Arquitetura

Frontend (HTML/CSS/JS) → FastAPI (Routers + Auth + Schemas + Models) → MySQL 8.0

---

## 📁 Estrutura

app/ · routers/ · static/ · docs/ · README.md · requirements.txt · .env.example

---

## 🚀 Instalação

git clone https://github.com/leonardossouza-1987/motoprime.git
cd motoprime
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite o .env com suas credenciais
uvicorn app.main:app --reload

Acesse: http://localhost:8000
Docs: http://localhost:8000/docs

---

## 🔐 Credenciais de Teste

| Perfil | CPF | Senha |
|:------:|:---:|:-----:|
| ADM | 00000000000 | admin123 |
| Vendedor | 11111111111 | venda123 |
| Oficina | 22222222222 | mec123 |

---

## 🔒 Segurança

- JWT com HS256 e expiração de 8h
- bcrypt para hash de senhas
- RBAC (permissões por cargo)
- 401 = não autenticado · 403 = sem permissão

---

## 👨‍💻 Autor

**Leonardo S. Souza** · 
Curso Back-end · SENAI · 2026

---

## 📄 Licença

Projeto acadêmico para fins educacionais.
