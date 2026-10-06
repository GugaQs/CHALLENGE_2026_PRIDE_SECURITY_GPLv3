# 🛡️ 00 - ASPM IA FIAP - Desafio Pride Security 2026

<p align="center">
  <img src="Gemini_Generated_Image_qpglwoqpglwoqpgl.png" alt="Banner do Projeto Pride Security" width="600">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow?style=for-the-badge&logo=rocket" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/CLI-Terminal-black?style=for-the-badge&logo=gnubash&logoColor=white" alt="CLI">
  <img src="https://img.shields.io/badge/Docker-Suportado-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <a href="#-inicio-rapido-2-minutos">⚡ Inicio Rapido</a> •
  <a href="#-guia-completo-de-execucao">🚀 Como Rodar</a> •
  <a href="./documentacao/03-arquitetura-tecnica.md#-menu-de-diagramas">🗺️ Diagramas</a> •
  <a href="#-dicionario-de-documentacao">📚 Dicionario</a> •
  <a href="#-solucao-de-problemas-troubleshooting">🧯 Troubleshooting</a> •
  <a href="#-integrantes-do-grupo">👥 Equipe</a>
</p>

---

## 📚 Sumario

- [📌 Visao Geral](#-visao-geral)
- [🎯 Objetivo do Sistema](#-objetivo-do-sistema)
- [⚡ Inicio Rapido (2 minutos)](#-inicio-rapido-2-minutos)
- [📚 Dicionario de Documentacao](#-dicionario-de-documentacao)
- [🗺️ Menu de Diagramas de Arquitetura](#-menu-de-diagramas-de-arquitetura)
- [🧱 Estrutura do Repositorio](#-estrutura-do-repositorio)
- [🧩 Modulos do Sistema](#-modulos-do-sistema)
- [⚙️ Requisitos e Compatibilidade](#-requisitos-e-compatibilidade)
- [🚀 Guia Completo de Execucao](#-guia-completo-de-execucao)
- [🧭 Fluxo Funcional da Aplicacao](#-fluxo-funcional-da-aplicacao-fase-atual)
- [🛠️ Comandos Rapidos de Manutencao](#-comandos-rapidos-de-manutencao)
- [🧯 Solucao de Problemas (Troubleshooting)](#-solucao-de-problemas-troubleshooting)
- [👥 Integrantes do Grupo](#-integrantes-do-grupo)
- [📚 Referencias Internas](#-referencias-internas)

---

## 📌 Visao Geral

O projeto **ASPM IA FIAP** foi desenvolvido no contexto do desafio da **Pride Security** em parceria com a **FIAP**, com foco em **Application Security Posture Management (ASPM)**.

Nesta fase, o repositorio entrega uma base CLI em Python, modular, pronta para evoluir para capacidades mais completas de seguranca, como:

- analise de ativos;
- cadastro e controle basico de usuarios;
- rotinas de scanner e auditoria;
- trilha de logs para rastreabilidade.

---

## 🎯 Objetivo do Sistema

Criar uma aplicacao de linha de comando que sirva como plataforma de evolucao para um ecossistema de seguranca, permitindo:

- 🛡️ centralizar funcionalidades de defesa e postura;
- 🧩 facilitar manutencao com estrutura modular;
- 🚀 preparar o terreno para novos modulos de analise.

---

## ⚡ Inicio Rapido (2 minutos)

### 🐍 Quero rodar localmente

```bash
git clone https://github.com/carmipa/CHALLENGE_2026_PRIDE_SECURITY.git
cd CHALLENGE_2026_PRIDE_SECURITY/api_python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

### 🐳 Quero rodar com Docker

```bash
git clone https://github.com/carmipa/CHALLENGE_2026_PRIDE_SECURITY.git
cd CHALLENGE_2026_PRIDE_SECURITY/api_python
docker compose up --build
```

> Dica UX: se for seu primeiro acesso, use o Inicio Rapido; se quiser entender cada passo, siga o Guia Completo abaixo.

---

## 📚 Dicionario de Documentacao

Para transformar este repositorio em um guia tecnico completo, a documentacao detalhada foi organizada em arquivos separados dentro de `documentacao/`.

### 🔎 Acesso rapido por tema

- [📘 Menu central da documentacao](./documentacao/README.md)
- [🧭 01 - Visao Geral do Projeto](./documentacao/01-visao-geral.md)
- [⚙️ 02 - Instalacao e Execucao](./documentacao/02-instalacao-execucao.md)
- [🏗️ 03 - Arquitetura Tecnica](./documentacao/03-arquitetura-tecnica.md)
- [🧩 04 - Modulos e Responsabilidades](./documentacao/04-modulos-responsabilidades.md)
- [🛠️ 05 - Operacao e Manutencao](./documentacao/05-operacao-manutencao.md)
- [🧯 06 - Troubleshooting e FAQ](./documentacao/06-troubleshooting-faq.md)
- [🚀 07 - Roadmap e Proximos Passos](./documentacao/07-roadmap.md)
- [🤖 08 - IA local com GPU (AMD e NVIDIA)](./documentacao/08-ia-local-amd-nvidia.md)

> 📈 Os diagramas de arquitetura em Mermaid (compatveis com GitHub) estao em [03 - Arquitetura Tecnica](./documentacao/03-arquitetura-tecnica.md). O fluxo completo de **IA local + GPU** (LM Studio, AMD/NVIDIA, pastas de relatorio) esta em [08 - IA local com GPU](./documentacao/08-ia-local-amd-nvidia.md).

## 🗺️ Menu de Diagramas de Arquitetura

- [📌 Abrir pagina de arquitetura](./documentacao/03-arquitetura-tecnica.md)
- [Fluxo geral da aplicacao](./documentacao/03-arquitetura-tecnica.md#fluxo-geral-da-aplicacao)
- [Arquitetura por camadas](./documentacao/03-arquitetura-tecnica.md#arquitetura-por-camadas)
- [Execucao local e container](./documentacao/03-arquitetura-tecnica.md#execucao-local-e-container)
- [IA local, GPU e LM Studio](./documentacao/08-ia-local-amd-nvidia.md)

---

## 🧱 Estrutura do Repositorio

```text
CHALLENGE_2026_PRIDE_SECURITY/
├── api_python/                      # Nucleo funcional CLI (referencia)
│   ├── app/
│   │   ├── ui/                      # Menus e interfaces CLI
│   │   │   ├── cadastro/            # Fluxos de cadastro/listagem
│   │   │   └── sobre/               # Tela "Sobre" com equipe e repo
│   │   ├── data/                    # Persistencia simples (arquivos)
│   │   └── utils/                   # Helpers (tempo, limpeza, etc.)
│   ├── main.py                      # Ponto de entrada da aplicacao
│   ├── requirements.txt             # Dependencias Python
│   ├── Dockerfile                   # Build da imagem
│   └── docker-compose.yml           # Orquestracao local com Docker
├── flask-python/                    # Camada web Flask (paridade parcial: sem cadastro)
│   ├── app/
│   │   ├── ui/                      # Regras funcionais reaproveitadas
│   │   ├── utils/                   # Utilitarios compartilhados
│   │   └── web/                     # routes/services/templates/static
│   ├── app.py                       # Entrypoint web — unico deste modulo
│   └── tests/                       # Suite pytest (unit + integracao), 38 testes
├── scanner_arquivo/                 # Modulo auxiliar de scanner (evolucao)
└── README.md                        # Documentacao principal
```

---

## 🧩 Modulos do Sistema

Hoje o projeto possui dois modulos principais, com papeis complementares:

- **`api_python`**: motor funcional CLI de referencia (regras de negocio e fluxos base).
- **`flask-python`**: camada web Flask com paridade funcional, UX HTML e operacao assincrona.

Arquitetura detalhada e diagrama completo:

- [🏗️ 03 - Arquitetura Tecnica](./documentacao/03-arquitetura-tecnica.md)
- [🧩 04 - Modulos e Responsabilidades](./documentacao/04-modulos-responsabilidades.md)

---

## ⚙️ Requisitos e Compatibilidade

<p align="left">
  <img src="https://img.shields.io/badge/OS-Windows_10%2F11-0078D6?style=flat&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/OS-Linux-FCC624?style=flat&logo=linux&logoColor=black" alt="Linux">
  <img src="https://img.shields.io/badge/OS-macOS-000000?style=flat&logo=apple&logoColor=white" alt="macOS">
  <img src="https://img.shields.io/badge/Gerenciador-pip-3775A9?style=flat&logo=pypi&logoColor=white" alt="pip">
</p>

### 💻 Requisitos para rodar localmente

- 🐍 Python **3.11 ou superior**;
- 📦 `pip` instalado e atualizado;
- 🖥️ terminal PowerShell, CMD, Git Bash, Bash ou Zsh;
- 🌐 acesso ao Git para clonagem.

### 🐳 Requisitos para rodar com Docker

- 🧱 Docker Desktop instalado;
- 🔧 Docker Compose habilitado (`docker compose version`);
- ⚡ virtualizacao ativa no sistema operacional.

### 🧭 Sistemas operacionais suportados

- 🪟 Windows 10/11;
- 🐧 Linux (Ubuntu, Debian, Fedora e similares);
- 🍎 macOS.

---

## 🚀 Guia Completo de Execucao

<p align="left">
  <img src="https://img.shields.io/badge/Modo-Local-2ea44f?style=flat&logo=python&logoColor=white" alt="Modo local">
  <img src="https://img.shields.io/badge/Modo-Container-0db7ed?style=flat&logo=docker&logoColor=white" alt="Modo container">
</p>

### 🧠 Qual modo devo escolher?

| Cenario | Recomendacao |
| :--- | :--- |
| Quero comecar rapido sem instalar Python | 🐳 Docker |
| Quero desenvolver e depurar no editor | 🐍 Local (venv) |
| Quero ambiente isolado e reproduzivel | 🐳 Docker |
| Quero controle total das libs e versoes | 🐍 Local (venv) |

### 1) 🐍 Execucao Local (Python) - passo a passo detalhado

#### 1.1 📥 Clonar o projeto

```bash
git clone https://github.com/carmipa/CHALLENGE_2026_PRIDE_SECURITY.git
```

#### 1.2 📂 Entrar na pasta correta

```bash
cd CHALLENGE_2026_PRIDE_SECURITY/api_python
```

#### 1.3 🧪 Criar ambiente virtual

O ambiente virtual isola as dependencias do projeto para evitar conflitos com outros projetos Python.

**Windows (PowerShell)**
```bash
python -m venv .venv
```

**Linux/macOS (Bash/Zsh)**
```bash
python3 -m venv .venv
```

#### 1.4 ▶️ Ativar ambiente virtual

**Windows (PowerShell)**
```bash
.\.venv\Scripts\Activate.ps1
```

Se houver erro de politica de execucao no PowerShell:

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD)**
```bash
.venv\Scripts\activate.bat
```

**Linux/macOS (Bash/Zsh)**
```bash
source .venv/bin/activate
```

#### 1.5 📦 Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 1.6 ▶️ Executar a aplicacao

```bash
python main.py
```

✅ Quando a execucao iniciar, o menu principal da CLI deve aparecer no terminal.

#### 1.7 ⏹️ Encerrar execucao

- Use a opcao de saida no menu; ou
- pressione `Ctrl + C` no terminal.

#### 1.8 📴 Desativar ambiente virtual (opcional ao finalizar)

```bash
deactivate
```

---

### 2) 🐳 Execucao com Docker - passo a passo detalhado

#### 2.1 📂 Entrar na pasta do modulo Python

```bash
cd CHALLENGE_2026_PRIDE_SECURITY/api_python
```

#### 2.2 🏗️ Construir e subir container

```bash
docker compose up --build
```

Esse comando:
- constroi a imagem com base no `Dockerfile`;
- instala dependencias no ambiente containerizado;
- inicia a aplicacao conforme configuracao do `docker-compose.yml`.

✅ O menu da CLI deve aparecer no terminal do container.

#### 2.3 🌙 Rodar em segundo plano (opcional)

```bash
docker compose up --build -d
```

#### 2.4 📜 Ver logs em tempo real

```bash
docker compose logs -f
```

#### 2.5 🛑 Parar e remover containers

```bash
docker compose down
```

#### 2.6 🧹 Limpeza completa de imagens/volumes (opcional)

```bash
docker compose down --rmi all --volumes --remove-orphans
```

> Use esse comando apenas quando quiser recriar tudo do zero.

---

## 🧭 Fluxo Funcional da Aplicacao (fase atual)

Na versao atual, o comportamento geral segue este fluxo:

1. ⚙️ `main.py` inicializa a CLI;
2. 📋 menu principal exibe opcoes (cadastro, scans classicos, **IA local** opcao 4, **IA API** opcao 5, logs, sobre);
3. 👤 usuario navega pelos modulos escolhidos; **IA local** detecta **NVIDIA** via `nvidia-smi` quando disponivel, oferece **AMD / NVIDIA** e pode chamar **LM Studio** na GPU;
4. 💾 dados de cadastro sao persistidos em arquivo; scans classicos e **IA local** gravam relatorios em pastas proprias (**incluindo `logs/amd/` e `logs/nvidia/` por placa**);
5. 🕒 logs e metadados de auditoria usam UTC global como referencia principal;
6. ✅ validacoes de cadastro e testes automatizados ajudam a manter qualidade.

Documentacao dedicada ao fluxo de GPU: [documentacao/08-ia-local-amd-nvidia.md](./documentacao/08-ia-local-amd-nvidia.md).

---

## 🛠️ Comandos Rapidos de Manutencao

### 🔁 Reinstalar dependencias no ambiente local

```bash
pip install -r requirements.txt --force-reinstall
```

### 🧪 Executar testes automatizados

```bash
pytest tests/ -q
```

Ou, para focar por tema:

```bash
pytest tests/test_validacao_cadastro.py -v
pytest tests/test_exemplo_scan.py -v
```

### ♻️ Recriar ambiente virtual do zero

**Windows (PowerShell)**
```bash
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/macOS**
```bash
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🧯 Solucao de Problemas (Troubleshooting)

### ❌ `python` nao reconhecido

- tente `python3 main.py`;
- valide instalacao com `python --version` ou `python3 --version`;
- no Windows, confira se o Python foi adicionado ao `PATH`.

### ⚠️ Erro ao ativar `.venv` no PowerShell

- rode:
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
- ative novamente:
```bash
.\.venv\Scripts\Activate.ps1
```

### 📦 Dependencias nao instalam

- atualize o pip:
```bash
python -m pip install --upgrade pip
```
- reinstale:
```bash
pip install -r requirements.txt --force-reinstall
```

### 🐳 Docker nao sobe

- confirme status do Docker Desktop;
- valide comando:
```bash
docker compose version
```
- tente rebuild:
```bash
docker compose down
docker compose up --build
```

---

## ⚖️ Licença

Este projeto é distribuído sob a **GNU General Public License v3.0 (GPL-3.0)**.
Consulte [LICENSE.md](LICENSE.md) para ler os termos completos.

---

## 👥 Integrantes do Grupo

**Turma:** 1TDCPV

<p align="left">
  <img src="https://img.shields.io/badge/Turma-1TDCPV-blueviolet?style=flat&logo=googleclassroom&logoColor=white" alt="Turma">
  <img src="https://img.shields.io/badge/FIAP-Challenge_2026-cc0000?style=flat&logo=academia&logoColor=white" alt="FIAP Challenge">
</p>

| Nome | RM |
| :--- | :--- |
| Paulo Andre Carminati | RM570877 |
| Gustavo Quental Scorsi | RM569862 |
| Andre Archanjo dos Santos Torres | RM570458 |
| Luiz Carlos da Paixao dos Santos | RM573009 |
| Victor Henrique de Barros Oliveira | RM570012 |

## 🔗 Repositorio oficial

- https://github.com/GugaQs/CHALLENGE_2026_PRIDE_SECURITY_GPLv3

---

## 📚 Referencias Internas

- 🧾 O menu `Sobre` da aplicacao le os dados da equipe no arquivo `api_python/app/ui/sobre/sobre.py`.
- 📘 A documentacao especifica do modulo Python tambem esta em `api_python/README.md`.

---

<p align="center">
  Feito com carinho por alunos da FIAP.
</p>
