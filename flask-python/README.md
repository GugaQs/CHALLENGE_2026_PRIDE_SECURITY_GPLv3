# 🌐 03 - ASPM IA - Flask Web + CLI

<p align="left">
  <img src="https://img.shields.io/badge/Modulo-Flask_Python-0E7490?style=flat&logo=flask&logoColor=white" alt="Modulo Flask">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Testes-Pytest-success?style=flat&logo=pytest&logoColor=white" alt="Testes">
  <img src="https://img.shields.io/badge/Deploy-Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker">
</p>

**Navegação:** [📚 05 - Dicionário da documentação](../documentacao/README.md) • [🐍 01 - API Python](../api_python/README.md) • [🧪 04 - Testes Flask](./tests/README_TESTES.md)

Módulo `flask-python` do Challenge Pride Security 2026.  
Camada web Flask completa, escrita somente com funções (sem classes de domínio), reaproveitando o núcleo funcional de `api_python`.

> **Divergência declarada em relação ao `api_python`:** o módulo de **cadastro de usuários foi removido desta camada web**. As rotas `/cadastro/*`, o `cadastro_service`, o pacote `app/ui/cadastro/` e o `app/utils/validacao_cadastro.py` não existem mais aqui. O CLI `api_python` continua com o cadastro. Portanto a paridade entre os dois módulos é **parcial e intencional**, não total.

---

## 📌 Visão geral

- Entrada web **única** em `app.py` (com abertura automática do navegador em ambiente local). Este módulo **não tem entrypoint CLI próprio** — o CLI é o `api_python`.
- Camada web separada por `routes` + `services` + `templates`.
- Interface responsiva com menu, cards, formulários, tabelas e logs coloridos.
- Tooltips didáticos em links/botões para orientar a navegação.
- Scans assíncronos com barra de progresso para projeto, IA local e containers.
- Documentação do repositório renderizada dentro da própria aplicação, em `/documentacao/`, com diagramas Mermaid.

---

## 🧱 Estrutura do módulo

```text
flask-python/
├── app/
│   ├── ui/                          # Nucleo funcional (scan, IA local, containers, software)
│   ├── utils/                       # Logger, tempo, helpers, progresso
│   └── web/
│       ├── app.py                   # Fabrica Flask (create_app) + cabecalhos de seguranca
│       ├── routes/                  # Endpoints HTTP (8 blueprints)
│       ├── services/                # Orquestracao da camada web
│       ├── templates/               # HTML/Jinja2 por modulo
│       └── static/
│           ├── css/style.css        # Sistema de design (tokens, sem px)
│           ├── js/app.js            # Progresso, toasts, tooltips, seletor de pasta
│           ├── js/docs-mermaid.js   # Inicializa Mermaid em /documentacao/
│           ├── js/log-terminal.js   # Rolagem e dicas do terminal de log
│           ├── js/mermaid.min.js    # Mermaid servido LOCAL (exigencia da CSP)
│           ├── js/model-viewer.min.js
│           ├── img/                 # Imagens da interface
│           └── models/              # Animacao 3D do rodape
├── logs/                            # Logs de sistema e relatorios (generic/amd/nvidia)
├── app.py                           # Entrypoint web — unico deste modulo
├── requirements.txt
└── tests/                           # Unitarios e integracao (pytest)
```

---

## 🧭 Módulos da interface web

| Modulo | URL | Descricao |
|---|---|---|
| Dashboard | `/` | Entrada principal com atalhos para todos os modulos |
| Scan Projeto | `/scan` | Scan assincrono com barra de progresso |
| IA Local | `/ia-local` | Scan GPU (AMD/NVIDIA), cognitivo e auditoria |
| IA API | `/modulos/ia-api` | Configuracao de provedor/chave para varredura remota |
| Logs Sistema | `/logs` | Atalhos e leitura de logs tecnicos |
| Relatorios Scan | `/scan/logs?secao=scan` | Lista de relatorios, filtros e detalhes |
| Containers | `/modulos/containers` | Busca de Dockerfile/compose com progresso |
| Scan Software | `/modulos/scan-software` | Lista programas instalados no sistema operacional |
| Scan GitHub - Problema? | `/modulos/scan-github-problema` | Explicacao arquitetural sobre limites de esteiras GitHub |
| Documentacao | `/documentacao` | README e docs do repositorio renderizados com Mermaid |
| Sobre | `/sobre` | Contexto institucional e equipe |

---

## ✅ Recursos implementados

### 1) 🚀 Scans assíncronos com progresso

- Scan de projeto: inicio em `/scan/executar-assincrono`, polling em `/scan/status/<job_id>`.
- IA local GPU e cognitivo: endpoints assincronos dedicados em `/ia-local/...`.
- Containers: inicio e status em `/modulos/containers/...`.
- Painel de progresso reutilizavel via template `_painel_progresso.html`.

### 2) 📊 Relatórios e filtros

- Filtro por severidade/tipo/arquivo em detalhe de log.
- Exportacao de JSON filtrado (`report_filtrado_*.json`).
- Links CVE/CWE (NVD e MITRE) nas falhas.

### 3) 🤖 IA local (AMD/NVIDIA)

- Fluxo com auditoria de falhas e pagina de detalhe por vulnerabilidade.
- Filtro por severidade na auditoria (`/ia-local/auditoria/...`).
- Reanalise e impressao de parecer IA.

### 4) 🧾 Logs coloridos e explicativos

- Parser estruturado de linhas (data/hora/ms/nivel/modulo/mensagem).
- Badges por criticidade (error/warning/info/debug/trace).
- Dica didatica por padroes de erro comuns.

### 5) 🎨 UX e front-end

- Tooltips globais e contextuais em links, botões e cards.
- Layout responsivo (desktop/tablet/mobile) em toda a interface.
- Navegação com botões de apoio e feedback visual consistente.
- Sistema de design em `static/css/style.css`: tokens de cor, espaçamento, raio e tipografia declarados em um único bloco `:root`.
- **Nenhuma medida em `px`.** A folha usa `rem` para tipografia, espaçamento e borda; `clamp()` + `vw` para títulos e margem de página; `%`, `fr` e `minmax()` para largura de layout; e `em` nos media queries. Consequência prática: quem aumenta o tamanho de fonte padrão do navegador recebe a interface inteira proporcionalmente maior, em vez de só o texto crescer dentro de caixas fixas.
- Suporte a `prefers-reduced-motion` e folha de impressão dedicada (relatório de scan sai legível no papel).

---

## ⚙️ Execução

### Web (único entrypoint deste módulo)

```bash
cd flask-python
pip install -r requirements.txt
python app.py
```

- URL: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- O navegador abre automaticamente em ambiente local.

> Este módulo **não tem CLI próprio**. Para a interface de terminal, use o módulo `api_python` (`cd api_python && python main.py`).

### Docker (web)

```bash
cd flask-python
docker compose up --build
```

---

## 🧪 Testes

```bash
cd flask-python
python -m pytest tests/ -q
```

**Estado medido: 234 testes, 215 passando e 19 `xfail`** (defeitos de auditoria
registrados executavelmente). Cobertura de `app/web` + `app/utils`: **71%**. Suíte completa em **12,8 s**.

| categoria | testes | o que cobre |
|---|---|---|
| `robustez` | 59 | tipo errado, valor de borda, método HTTP errado, concorrência |
| `integracao` | 101 | varredura automática das 43 rotas + fluxos assíncronos |
| `unidade` | 55 | filtros, tempo, progresso, jobs, logger |
| `seguranca` | 45 | path traversal, CSP, cabeçalhos, CSRF, segredos |
| `regressao` | 21 | registro executável dos achados de auditoria |
| `contrato` | 11 | CSP × templates, CSS × JS, contraste WCAG, unidades |

```bash
python -m pytest tests/ -m "not lento" -q   # ciclo rapido (~8 s)
python -m pytest tests/ -m seguranca -q     # so seguranca
```

Rodar a suíte é **operação segura**: o `conftest.py` isola todo caminho de log em
diretório temporário, bloqueia a rede e reprova a sessão se algum teste alterar
um log real. Antes disso, `pytest` deixava resíduo permanente em `logs/` e podia
sobrescrever um relatório do usuário.

Detalhes em `tests/README_TESTES.md`.

---

## 🛠️ Observações técnicas

- Projeto orientado a funções (sem classes de domínio), conforme requisito.
- Pode existir árvore Git com arquivos não versionados de logs/artefatos locais.
- `run.py` foi descontinuado: use `app.py` como entrypoint web padrão.

### 🔒 Content-Security-Policy — por que todo asset é local

`create_app()` (em `app/web/app.py`) devolve, em todas as respostas, a política:

```text
default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
img-src 'self' data: https://img.shields.io; connect-src 'self'; worker-src blob: 'self';
```

Duas consequências que **valem como regra deste módulo**:

1. **`script-src 'self'` não inclui `'unsafe-inline'`.** Bloco `<script>` escrito dentro de um template é **bloqueado pelo navegador, em silêncio** — a página carrega, o comportamento simplesmente não acontece e nada aparece na tela. Todo JavaScript vive em arquivo sob `static/js/` e é referenciado por `src`.
2. **Nenhum recurso de terceiro carrega.** CDN, webfont remota e `@import` externo são recusados. Por isso o Mermaid é servido de `static/js/mermaid.min.js`, e não de `cdn.jsdelivr.net`.

Assets são versionados por `?v={{ asset_version('...') }}` (mtime do arquivo). Sem esse parâmetro, o navegador continua servindo a versão em cache depois de um deploy e a alteração parece não ter surtido efeito.

---
