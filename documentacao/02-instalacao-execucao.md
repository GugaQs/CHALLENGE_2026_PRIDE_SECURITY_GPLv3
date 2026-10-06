# ⚙️ 07 - Instalação e Execução

<p align="left">
  <img src="https://img.shields.io/badge/Doc-Instalacao-3776AB?style=flat&logo=python&logoColor=white" alt="Instalacao">
  <img src="https://img.shields.io/badge/Suporte-Docker_+_Local-2496ED?style=flat&logo=docker&logoColor=white" alt="Suporte">
</p>

**Navegação:** [📚 Dicionário](./README.md) • [🧭 Anterior: Visão Geral](./01-visao-geral.md) • [🏗️ Próximo: Arquitetura](./03-arquitetura-tecnica.md)

## ✅ Pré-requisitos

- Python 3.11+
- pip atualizado
- Git
- (Opcional) Docker Desktop + Docker Compose
- (Opcional) LM Studio — para scans com IA local

---

## 🌐 flask-python — interface web (uso principal)

Este é o módulo principal para uso em laboratório e apresentações.

### Execução local

```powershell
git clone https://github.com/carmipa/CHALLENGE_2026_PRIDE_SECURITY.git
cd CHALLENGE_2026_PRIDE_SECURITY/flask-python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000` e abre o navegador automaticamente.

### Execução com Docker

```bash
cd CHALLENGE_2026_PRIDE_SECURITY/flask-python
docker compose up --build
```

Acesse `http://localhost:5000` no navegador.

Para parar:

```bash
docker compose down
```

### Como validar que subiu corretamente

- Navegador abre em `http://127.0.0.1:5000`.
- Menu superior exibe: Inicio, Scan, IA Local, Logs, Relatorios, Documentacao, Sobre.
- Rota `/documentacao/` renderiza os docs em Markdown com diagramas Mermaid.

---

## 🐍 api_python — núcleo CLI (referência funcional)

Módulo de referência funcional, executado em terminal. Usado para desenvolvimento e como origem das regras de negócio.

### Execução local

```powershell
cd CHALLENGE_2026_PRIDE_SECURITY/api_python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

### Execução com Docker

```bash
cd CHALLENGE_2026_PRIDE_SECURITY/api_python
docker compose up --build
```

Para parar:

```bash
docker compose down
```

### Como validar que subiu corretamente

- O menu principal deve aparecer no terminal.
- As opções de navegação devem responder sem erro.

---

## 🧪 Rodar testes (pytest)

Para `flask-python`:

```powershell
cd flask-python
python -m pytest tests/ -q
```

Para `api_python`:

```powershell
cd api_python
python -m pytest tests/ -q
```

Resultado esperado: todos os testes passando (48 testes OK).

---

**Próxima leitura recomendada:** [🏗️ 03 - Arquitetura Técnica](./03-arquitetura-tecnica.md)
