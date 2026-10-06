# 🚀 12 - Roadmap e Próximos Passos

<p align="left">
  <img src="https://img.shields.io/badge/Doc-Roadmap-6f42c1?style=flat&logo=githubprojects&logoColor=white" alt="Roadmap">
  <img src="https://img.shields.io/badge/Foco-Evolucao_do_Projeto-2ea44f?style=flat&logo=rocket&logoColor=white" alt="Evolucao">
</p>

**Navegação:** [📚 Dicionário](./README.md) • [🧯 Anterior: Troubleshooting](./06-troubleshooting-faq.md) • [🏠 README raiz](../README.md)

---

## ✅ Já concluído

- Interface web Flask completa com paridade funcional ao núcleo CLI.
- Scan de projeto por assinaturas com barra de progresso assíncrona.
- Scan IA local AMD e NVIDIA via LM Studio com detecção automática de GPU.
- Scan cognitivo (scan + análise IA em um passo) com parecer Markdown.
- Scan de containers Docker (Dockerfile, docker-compose, imagens).
- Scan de software instalado no SO.
- Scan IA API com configuração de provedor externo.
- Logs por fabricante GPU separados (`logs/amd/`, `logs/nvidia/`).
- Filtros avançados de relatório (severidade, tipo, arquivo, agrupamento).
- Paginação de resultados de scan.
- Documentação integrada na web (`/documentacao/`) com Markdown + Mermaid.
- 48 testes pytest OK (api_python + flask-python).
- Deploy via Docker Compose para ambos os módulos.

---

## 🧩 Curto prazo

- Aumentar cobertura de testes (e2e e integração para os scans assíncronos).
- Melhorar feedback de erro ao usuário quando scan falha com exceção.
- Adicionar validação de caminho no front-end antes de disparar o scan.
- Persistência de configuração de IA API (provedor + key) entre sessões.

---

## 🛠️ Médio prazo

- Substituir persistência de arquivo (`app/data/`) por banco relacional (SQLite ou PostgreSQL).
- Histórico de scans: listar todos os relatórios passados com metadados (data, módulo, total de falhas).
- Dashboard de postura: gráfico de evolução de severidade ao longo do tempo.
- Websockets ou SSE para substituir o polling de progresso (mais eficiente).
- Autenticação básica (login/logout) para acesso à interface web.

---

## 🌍 Longo prazo

- Pipeline CI/CD com scan automático em PRs (GitHub Actions + webhook).
- Exportação de relatórios em SARIF e CycloneDX (compatível com ferramentas de SAST).
- Integração com SIEM (Splunk, Elastic) via log estruturado (JSON lines).
- Análise com múltiplos modelos de IA em paralelo (comparativo de pareceres).
- Controle de acesso por perfil (analista, gestor, somente leitura).

---

**Voltar ao menu:** [📚 Dicionário de Documentação](./README.md)
