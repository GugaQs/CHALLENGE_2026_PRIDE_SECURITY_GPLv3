# 🏗️ 08 - Arquitetura Técnica

<p align="left">
  <img src="https://img.shields.io/badge/Doc-Arquitetura-black?style=flat&logo=architecture&logoColor=white" alt="Arquitetura">
  <img src="https://img.shields.io/badge/Foco-Modularidade-2ea44f?style=flat&logo=dependabot&logoColor=white" alt="Modularidade">
</p>

**Navegação:** [📚 Dicionário](./README.md) • [⚙️ Anterior: Instalação](./02-instalacao-execucao.md) • [🧩 Próximo: Módulos](./04-modulos-responsabilidades.md)

## 🧭 Menu de Diagramas

- [Arquitetura completa (api_python + flask-python)](#arquitetura-completa-api_python--flask-python)
- [Ciclo de vida de requisição HTTP (flask-python)](#ciclo-de-vida-de-requisição-http-flask-python)
- [Fluxo de scan assíncrono com barra de progresso](#fluxo-de-scan-assíncrono-com-barra-de-progresso)
- [Fluxo geral do menu CLI (api_python)](#fluxo-geral-do-menu-cli-api_python)
- [Arquitetura por camadas](#arquitetura-por-camadas)
- [Scan de containers Docker](#scan-de-containers-docker)
- [IA local, GPU e servidor LM Studio](#ia-local-gpu-e-servidor-lm-studio)
- [Execução local e container](#execução-local-e-container)
- [Estrutura de blueprints Flask](#estrutura-de-blueprints-flask)

---

## 📌 Visão da arquitetura

A arquitetura prioriza simplicidade, separação por responsabilidade e facilidade de manutenção. `api_python` define a lógica funcional; `flask-python` adiciona camada web sem duplicar regras.

---

## 🗺️ Diagramas (Mermaid)

### Arquitetura completa (api_python + flask-python)

```mermaid
flowchart LR
    U[Usuário]

    subgraph WEB["Módulo flask-python (web + CLI espelho)"]
        W_ENTRY[app.py]
        W_BP[Blueprints\nscan / ia_local\nmodulos / log / docs]
        W_SERV[app/web/services]
        W_UI[app/ui — regras funcionais]
        W_UTILS[app/utils]
        W_TMPL[templates Jinja2]
        W_LOGS[(flask-python/logs)]
    end

    subgraph CLI["Módulo api_python (núcleo CLI)"]
        A_ENTRY[main.py]
        A_UI[app/ui — menus CLI]
        A_UTILS[app/utils]
        A_DATA[app/data]
        A_LOGS[(api_python/logs)]
    end

    U -->|Navegador HTTP| W_ENTRY
    U -->|Terminal| W_ENTRY
    U -->|Terminal| A_ENTRY

    W_ENTRY --> W_BP --> W_SERV --> W_UI
    W_UI --> W_UTILS
    W_BP --> W_TMPL
    W_SERV --> W_LOGS

    A_ENTRY --> A_UI --> A_UTILS
    A_UI --> A_DATA
    A_UI --> A_LOGS

    W_UI -. Paridade funcional .-> A_UI
```

---

### Ciclo de vida de requisição HTTP (flask-python)

Mostra como uma requisição do navegador percorre as camadas até a resposta HTML.

```mermaid
sequenceDiagram
    actor Browser as Navegador
    participant APP as app.py (create_app)
    participant BP as Blueprint (ex: scan_bp)
    participant Route as Route handler
    participant Service as Service layer
    participant UI as app/ui (regras)
    participant Tmpl as Template Jinja2

    Browser->>APP: GET /scan/
    APP->>BP: dispatch pela URL prefix
    BP->>Route: chama view function
    Route->>Service: delega lógica
    Service->>UI: chama funções funcionais
    UI-->>Service: retorna dados / relatório
    Service-->>Route: retorna resultado
    Route->>Tmpl: render_template(...)
    Tmpl-->>Browser: HTML renderizado
```

---

### Fluxo de scan assíncrono com barra de progresso

Usado em scan de projeto, IA local e scan de containers. O front-end faz polling do status via JSON.

```mermaid
sequenceDiagram
    actor U as Usuário
    participant FE as Front-end JS
    participant Route as Route /executar-assincrono
    participant Service as Service (iniciar_*_assincrono)
    participant Thread as Thread background
    participant Jobs as _JOBS dict (UUID → status)

    U->>FE: clica "Iniciar Scan"
    FE->>Route: POST /executar-assincrono {caminho}
    Route->>Service: iniciar_scan_assincrono(caminho)
    Service->>Jobs: cria job_id + status=pendente
    Service->>Thread: Thread(target=_worker).start()
    Service-->>Route: {ok, job_id}
    Route-->>FE: {ok, job_id}

    loop polling a cada 1s
        FE->>Route: GET /status/{job_id}
        Route-->>FE: {progresso, etapa, concluido}
        FE->>FE: atualiza barra de progresso
    end

    Thread->>Jobs: atualiza progresso (0→100)
    Thread->>Jobs: grava relatório JSON no disco
    Thread->>Jobs: status=concluido, nome_log=...

    FE->>FE: redireciona para /scan/logs/{nome_log}
```

---

### Fluxo geral do menu CLI (api_python)

```mermaid
flowchart TD
    U[Usuário] --> M[main.py]
    M --> MENU[Menu principal]
    MENU --> CAD[1 — Cadastro]
    MENU --> LIST[2 — Listagem]
    MENU --> SCAN[3 — Scan de Projeto]
    MENU --> IA[4 — Scan IA Local AMD/NVIDIA]
    MENU --> IAAPI[5 — Scan IA API]
    MENU --> SOBRE[6 — Sobre]
    MENU --> SAIR[0 — Sair]

    CAD --> DATA[(Arquivo usuários)]
    LIST --> DATA
    SCAN --> JSON_P[(logs/scan_projeto/)]
    IA --> ROTEADOR[menu_ia_local.py\nnvidia-smi → AMD ou NVIDIA]
    ROTEADOR --> AMD[scan_amd]
    ROTEADOR --> NV[scan_nvidia]
    AMD --> LOG_AMD[(logs/amd/)]
    NV --> LOG_NV[(logs/nvidia/)]
```

---

### Arquitetura por camadas

```mermaid
flowchart LR
    A[Camada de apresentação\napp/web/routes + templates] --> B[Camada de serviços\napp/web/services]
    B --> C[Camada funcional\napp/ui — regras e fluxos]
    C --> D[Camada utilitária\napp/utils — logger, helpers, tempo]
    C --> E[Camada de dados\napp/data — persistência em arquivo]
```

---

### Scan de containers Docker

```mermaid
flowchart TD
    U[Usuário] -->|informa caminho do projeto| FE[Front-end /modulos/containers]
    FE -->|POST /executar-assincrono| Route[modulos_bp]
    Route --> Svc[modulos_service\niniciar_scan_docker_assincrono]
    Svc --> T[Thread background\nexecutar_scan_docker]

    subgraph Scanner["Lógica de scan (app/ui)"]
        T --> DF[Lê Dockerfiles]
        T --> DC[Lê docker-compose.yml]
        T --> IMG[Verifica imagens usadas]
        T --> ENV[Verifica variáveis sensíveis]
    end

    Scanner --> Result[Lista artefatos + severidade]
    Result --> Template[containers/modulo_containers.html]
    Template --> U
```

---

### IA local, GPU e servidor LM Studio

Visão resumida do módulo `scan_ia_local` (detalhes, URLs e checklist em [13 - IA local com GPU](./08-ia-local-amd-nvidia.md)):

```mermaid
flowchart LR
    subgraph Host["Mesma máquina (laboratório)"]
        CLI[CLI ASPM Python]
        LM[LM Studio :1234]
        GPU[(GPU AMD ou NVIDIA)]
    end

    CLI -->|"assinaturas + JSON"| CLI
    CLI -->|"HTTP POST /v1/chat/completions"| LM
    LM --> GPU
    LM -.->|"texto do parecer"| CLI
```

---

### Execução local e container

```mermaid
flowchart LR
    subgraph Dev["Desenvolvimento local"]
        D1[python app.py] --> FLASK[Flask :5000]
        D2[python main.py] --> CLI_APP[CLI terminal]
    end

    subgraph Docker["Docker Compose"]
        D3[docker compose up --build] --> C1[Container flask-python :5000]
        D4[docker compose up --build] --> C2[Container api_python]
    end
```

---

### Estrutura de blueprints Flask

```mermaid
flowchart TD
    APP[create_app\napp/web/app.py] --> BP1[scan_bp\n/scan]
    APP --> BP2[ia_local_bp\n/ia-local]
    APP --> BP4[modulos_bp\n/modulos]
    APP --> BP5[log_bp\n/logs]
    APP --> BP6[documentacao_bp\n/documentacao]
    APP --> BP7[sobre_bp\n/sobre]
    APP --> BP8[main_bp\n/]

    BP1 --> R1[GET / — formulário\nPOST /executar\nPOST /executar-assincrono\nGET /status/job_id\nGET /logs\nGET /logs/nome]
    BP2 --> R2[GET / — painel IA\nPOST /executar-assincrono\nPOST /cognitivo-assincrono\nGET /status/job_id\nGET /auditoria/hw/nome\nGET /parecer/hw/arquivo]
    BP4 --> R3[GET/POST /containers\nGET/POST /scan-software\nGET/POST /ia-api\nGET /scan-github-problema]
```

---

## 🧱 Camadas principais

| Camada | Pasta | Papel |
|--------|-------|-------|
| Entrada web | `flask-python/app.py` | Factory Flask, registra blueprints |
| Roteamento | `app/web/routes/` | HTTP request → response, validação de entrada |
| Serviços | `app/web/services/` | Adaptam regras funcionais para web, jobs assíncronos |
| Lógica funcional | `app/ui/` | Regras de scan e IA (paridade com api_python) |
| Utilitários | `app/utils/` | Logger, helpers, tempo, validação |
| Dados | `app/data/` | Persistência em arquivo (configurações) |
| Templates | `app/web/templates/` | HTML Jinja2 por módulo (scan/, ia/, log/, etc.) |
| Estáticos | `app/web/static/` | CSS, JS, imagens |

## 🔒 Content-Security-Policy — restrição que molda o front-end

`create_app()` (`flask-python/app/web/app.py`) devolve, em toda resposta, a política abaixo. Ela não é detalhe de segurança: **decide como o front-end pode ser escrito.**

```text
default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
img-src 'self' data: https://img.shields.io; connect-src 'self'; worker-src blob: 'self';
```

| regra | consequência prática |
|---|---|
| `script-src 'self'` **sem** `'unsafe-inline'` | Bloco `<script>` dentro de template é **bloqueado pelo navegador**. Todo JS mora em arquivo sob `static/js/` e entra por `src`. |
| `default-src 'self'` | CDN, webfont remota e `@import` externo **não carregam**. Toda biblioteca é servida local — é por isso que `mermaid.min.js` está em `static/js/`. |
| `style-src` permite `'unsafe-inline'` | Atributo `style=` inline funciona; ainda assim o CSS fica em `style.css`. |
| `img-src` permite `https://img.shields.io` | Única exceção externa, para os badges do README. |

> **A armadilha desta política é o silêncio.** Script bloqueado não gera erro na tela: a página carrega inteira e o comportamento simplesmente não acontece. Foi assim que os diagramas Mermaid de `/documentacao/` e os botões do terminal de log ficaram inertes — ambos eram `<script>` inline, um deles importando de `cdn.jsdelivr.net`. Ao mexer no front-end, **conferir o console do navegador** é parte do teste, não zelo extra.

Assets são versionados por `?v={{ asset_version('...') }}` (mtime do arquivo, helper registrado em `create_app`). Sem esse parâmetro o navegador serve a versão em cache e a alteração parece não ter surtido efeito.

## 🎨 Sistema de design e unidades relativas

`static/css/style.css` é um sistema de design único: cor, espaçamento, raio, tipografia e movimento saem de tokens declarados em `:root`.

**Não há nenhuma medida em `px`.** A escolha de unidade segue o que cada uma resolve:

| unidade | onde | por quê |
|---|---|---|
| `rem` | tipografia, espaçamento, raio, borda | acompanha o tamanho de fonte configurado pela pessoa no navegador; `px` ignora essa preferência |
| `clamp()` + `vw` | títulos e margem lateral da página | escala contínua entre telas, sem saltos |
| `%`, `fr`, `minmax()` | largura de layout e grades | é a unidade correta para largura |
| `em` | media queries | o ponto de quebra acompanha o zoom de fonte, não só a largura física |
| `vh` | altura máxima de áreas roláveis | proporcional à janela |

`%` **não** é usado em `padding` nem em `font-size`: porcentagem de padding resolve contra a *largura* do container (padding vertical cresceria com a largura da tela) e porcentagem de fonte *acumula* a cada aninhamento.

## 🎯 Princípios adotados

- Modularidade: cada pasta atende a um papel específico.
- Paridade funcional **parcial e declarada**: `flask-python` e `api_python` compartilham regras sem duplicação, mas o **cadastro de usuários existe só no CLI `api_python`** — foi removido da camada web.
- Jobs assíncronos: scans pesados rodam em threads separadas com polling de status.
- Legibilidade: código orientado a aprendizado e evolução.

## 🚀 Evolução esperada

- Persistência em banco relacional ou NoSQL (substituir `app/data/`).
- Websockets ou SSE para substituir polling de progresso.
- Pipeline de análise com múltiplos modelos de IA.

---

**Próxima leitura recomendada:** [🧩 04 - Módulos e Responsabilidades](./04-modulos-responsabilidades.md)
