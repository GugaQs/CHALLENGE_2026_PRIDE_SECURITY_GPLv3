# 🧩 09 - Módulos e Responsabilidades

<p align="left">
  <img src="https://img.shields.io/badge/Doc-M%C3%B3dulos-8A2BE2?style=flat&logo=files&logoColor=white" alt="Modulos">
  <img src="https://img.shields.io/badge/Foco-Responsabilidades-F59E0B?style=flat&logo=task&logoColor=white" alt="Responsabilidades">
  <img src="https://img.shields.io/badge/Status-Atualizado-success?style=flat&logo=github&logoColor=white" alt="Status atualizado">
</p>

**Navegação:** [📚 Dicionário](./README.md) • [🏗️ Anterior: Arquitetura](./03-arquitetura-tecnica.md) • [🛠️ Próximo: Operação](./05-operacao-manutencao.md)

---

## 🐍 `api_python` (núcleo funcional CLI)

Módulo base do projeto, orientado à execução em terminal e definição das regras funcionais.

Responsável por:

- inicialização da aplicação via `main.py`;
- navegação por menus CLI com 7 opções funcionais;
- regras de scan, cadastro, auditoria e persistência;
- logs técnicos do motor de análise.

### 📁 Estrutura de pastas (api_python)

```
api_python/
├── main.py                        # Ponto de entrada CLI
├── app/
│   ├── ui/                        # Menus e fluxos funcionais
│   │   ├── menu.py                # Menu principal
│   │   ├── cadastro/              # Cadastro de usuários
│   │   ├── scan_projeto/          # Scan por assinaturas
│   │   ├── scan_ia_local/         # Scan com IA local (AMD/NVIDIA)
│   │   ├── scan_ia_api/           # Scan com IA via API externa
│   │   └── sobre/                 # Tela sobre / equipe
│   ├── utils/                     # Logger, helpers, tempo, validação
│   └── data/                      # Persistência em arquivo
└── logs/
    ├── erro_sistema.log           # Logger raiz (todos os módulos)
    ├── amd/system/ + reports/     # Logs motor AMD
    └── nvidia/system/ + reports/  # Logs motor NVIDIA
```

### 🤖 Submódulo `app/ui/scan_ia_local`

Fluxo **Scan de Projeto - IA Local** (opção **4** do menu):

- roteador `menu_ia_local.py`: detecta `nvidia-smi`, pré-seleciona AMD ou NVIDIA;
- motores `scan_amd` e `scan_nvidia`: geram JSON de vulnerabilidades por fabricante;
- cliente HTTP `executar_scan_ia.py`: envia prompt ao LM Studio em `localhost:1234`;
- logs por fabricante: `get_hardware_logger("amd"|"nvidia")` grava em `logs/<fabricante>/system/`.

Documentação detalhada: [13 - IA local com GPU](./08-ia-local-amd-nvidia.md).

### 🌐 Submódulo `app/ui/scan_ia_api`

Fluxo **Scan de Projeto - IA API** (opção **5**) — integração com provedor de modelo remoto; configuração de chave API e execução de varredura via HTTP externo.

---

## 🌐 `flask-python` (camada web + paridade funcional)

Módulo web que espelha o comportamento funcional do `api_python`, adicionando UX HTTP completa.

### 📁 Estrutura de pastas (flask-python)

```
flask-python/
├── app.py                         # Ponto de entrada web (chama create_app)
├── app/
│   ├── web/
│   │   ├── app.py                 # Factory Flask + registro de blueprints
│   │   ├── routes/                # Blueprints HTTP (um arquivo por domínio)
│   │   ├── services/              # Adaptadores web → lógica funcional + jobs assíncronos
│   │   ├── templates/             # HTML Jinja2 organizado por módulo
│   │   └── static/                # CSS, JS, imagens
│   ├── ui/                        # Regras funcionais (paridade com api_python)
│   └── utils/                     # Logger, helpers, tempo, validação
```

### 🔀 Blueprints registrados

| Blueprint | URL prefix | Responsabilidade |
|-----------|-----------|-----------------|
| `main_bp` | `/` | Página inicial, navegação raiz |
| `scan_bp` | `/scan` | Scan de projeto, logs JSON, filtros avançados |
| `ia_local_bp` | `/ia-local` | Scan IA local AMD/NVIDIA + parecer Markdown |
| `modulos_bp` | `/modulos` | Containers, software, IA API, GitHub |
| `log_bp` | `/logs` | Visualização centralizada de logs de sistema |
| `documentacao_bp` | `/documentacao` | Documentação renderizada Markdown + Mermaid |
| `sobre_bp` | `/sobre` | Tela Sobre / equipe |

### 🧱 Separação interna do `flask-python`

- **`app/web/routes`**: transporte HTTP — request/response, status code, redirects.
- **`app/web/services`**: adaptadores — orquestram jobs assíncronos, convertem dados para template.
- **`app/ui`**: regras funcionais reaproveitadas (paridade com o módulo CLI de origem).
- **`app/utils`**: utilitários transversais (logger, validação, helpers).

### 📦 Submódulos do `flask-python`

#### scan_bp — Scan de Projeto

- Formulário de caminho, scan síncrono e assíncrono com barra de progresso.
- Listagem paginada de relatórios JSON com filtros por severidade, tipo e arquivo.
- Filtros avançados com agrupamento por tipo e severidade.
- Visualização do JSON bruto e abertura de arquivo no SO.
- Limpeza de logs.

#### ia_local_bp — IA Local AMD/NVIDIA

- Painel com detecção automática de GPU (nvidia-smi).
- Scan GPU assíncrono e scan cognitivo (scan + análise IA em um passo) com barra de progresso.
- Re-análise do último relatório JSON.
- Auditoria de falhas com filtro por severidade.
- Detalhe individual de falha.
- Visualização de parecer Markdown.
- Impressão do parecer (Windows: Notepad).

#### modulos_bp — Módulos em Evolução

- **Scan de containers Docker**: análise de Dockerfiles, docker-compose e imagens.
- **Scan de software instalado**: lista programas do SO com limite configurável.
- **IA API**: configuração de provedor externo, API key e varredura via HTTP.
- **GitHub**: página explicativa sobre limitações de scan automático.

#### log_bp — Logs Centralizados

- Listagem de logs de sistema e relatórios scan.
- Visualização com classificação de severidade por linha.

### 🤝 Contrato entre os módulos

- `api_python` define a lógica de domínio funcional (sem classes, apenas funções).
- `flask-python` consome e adapta essa lógica para web sem duplicar regras.
- Ambos podem evoluir em paralelo mantendo compatibilidade de relatórios e formatos JSON.

---

## 🔎 `scanner_arquivo`

Módulo auxiliar para evolução de capacidades de scanner.

Responsável por:

- exploração de análise de estrutura de arquivos;
- base para futuras regras de verificação estática.

---

## 📚 `documentacao`

Módulo de conhecimento do projeto.

Responsável por:

- onboarding de novos integrantes;
- documentação operacional e arquitetural;
- índice navegável com 18 documentos (00–17);
- servido via rota `/documentacao/` com renderização Markdown + Mermaid.

---

**Próxima leitura recomendada:** [🛠️ 10 - Operação e Manutenção](./05-operacao-manutencao.md)
