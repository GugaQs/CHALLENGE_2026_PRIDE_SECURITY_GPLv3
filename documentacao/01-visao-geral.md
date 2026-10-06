# 🧭 06 - Visão Geral do Projeto

<p align="left">
  <img src="https://img.shields.io/badge/Doc-Visao_Geral-0A66C2?style=flat&logo=bookstack&logoColor=white" alt="Visao geral">
  <img src="https://img.shields.io/badge/Nivel-Fundacional-blueviolet?style=flat&logo=target&logoColor=white" alt="Nivel">
  <img src="https://img.shields.io/badge/Status-Atualizado-success?style=flat&logo=github&logoColor=white" alt="Status atualizado">
</p>

**Navegação:** [📚 Dicionário](./README.md) • [⚙️ Próximo: Instalação](./02-instalacao-execucao.md) • [🏠 README raiz](../README.md)

## 📌 O que é o projeto

O **ASPM IA FIAP** é um sistema de **Application Security Posture Management** desenvolvido no Challenge FIAP 2026. Combina um núcleo CLI em Python (`api_python`) com uma interface web completa (`flask-python`), permitindo escanear projetos em busca de vulnerabilidades, analisar resultados com IA local e auditar artefatos Docker.

## 🎯 Problema que resolve

- Centralizar fluxos de segurança (scan, auditoria, análise com IA) em uma única plataforma.
- Oferecer interface web responsiva para uso em laboratório e apresentações FIAP.
- Demonstrar uso de IA local (LM Studio) com GPU AMD e NVIDIA sem dependência de nuvem.
- Facilitar onboarding de novos integrantes com documentação integrada à própria aplicação.

## 👥 Público-alvo

- Alunos e equipe técnica da FIAP (turma 1TDCPV).
- Usuários que precisam de fluxos de segurança com IA local e interface web.

## ✅ Escopo atual (estado em 2026-05-26)

### Módulo `api_python` — núcleo funcional CLI

- Menu principal CLI com 7 opções funcionais.
- Cadastro e listagem de usuários (persistência em arquivo).
- Scan de projeto por assinaturas (detecção de padrões de vulnerabilidade).
- Scan IA local com GPU: motores AMD (`scan_amd`) e NVIDIA (`scan_nvidia`), análise via LM Studio.
- Scan IA API: integração com provedor externo (em evolução).
- Logs separados por fabricante GPU (`logs/amd/`, `logs/nvidia/`).
- 48 testes pytest OK (cobertura unitária e de integração).

### Módulo `flask-python` — camada web

- Interface web responsiva (Flask + Jinja2 + CSS/JS próprio).
- Paridade funcional completa com `api_python`.
- **Scan de projeto** assíncrono com barra de progresso e paginação de resultados.
- **Scan IA local** assíncrono (AMD/NVIDIA): scan + análise cognitiva + visualização de parecer Markdown.
- **Scan de containers Docker**: detecção de artefatos e vulnerabilidades em `Dockerfile`/`docker-compose`.
- **Scan de software instalado**: lista programas do sistema.
- **Scan IA API**: configuração de provedor externo e varredura.
- **Logs**: visualização de logs de sistema e relatórios JSON com filtros avançados.
- **Documentação integrada**: rota `/documentacao/` com renderização Markdown + Mermaid.
- Scan GitHub: página explicativa + diagramas PNG/SVG.

## 🚀 Escopo futuro

- Persistência de cadastros em banco relacional (PostgreSQL / SQLite).
- Dashboard de postura de segurança com gráficos históricos.
- Pipeline CI/CD com scan automático em PRs.
- Integração com SIEM e exportação SARIF/CycloneDX.
- Autenticação e controle de acesso por perfil.

---

**Próxima leitura recomendada:** [⚙️ 02 - Instalação e Execução](./02-instalacao-execucao.md)
