# 🧯 11 - Troubleshooting e FAQ

<p align="left">
  <img src="https://img.shields.io/badge/Doc-Suporte-red?style=flat&logo=sentry&logoColor=white" alt="Suporte">
  <img src="https://img.shields.io/badge/Foco-Resolucao_de_Problemas-orange?style=flat&logo=helpdesk&logoColor=white" alt="Resolucao">
</p>

**Navegação:** [📚 Dicionário](./README.md) • [🛠️ Anterior: Operação](./05-operacao-manutencao.md) • [🚀 Próximo: Roadmap](./07-roadmap.md)

---

## ❗ Problemas comuns

### `python` não reconhecido

- Verificar versão com `python --version`.
- Tentar `python3 --version`.
- No Windows, validar Python no PATH.

### Falha ao ativar `.venv` no PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Erro ao instalar dependências

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Docker não inicia corretamente

```bash
docker compose version
docker compose down
docker compose up --build
```

---

## 🌐 Problemas específicos do flask-python

### Porta 5000 ocupada

```powershell
# Verificar o que está usando a porta
netstat -ano | findstr :5000
# Encerrar o processo (substitua <PID> pelo ID encontrado)
taskkill /PID <PID> /F
```

Ou altere a porta em `flask-python/app.py`:

```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

### Mermaid não renderiza nos documentos

- Verifique se a biblioteca `mermaid.js` está carregada no template `base.html`.
- Abra o DevTools do navegador (F12) e verifique erros no console.
- Tente forçar reload sem cache: `Ctrl+Shift+R`.

### Scan assíncrono trava na barra de progresso

- O job pode ter falhado silenciosamente. Verifique `flask-python/logs/erro_sistema.log`.
- Certifique-se de que o caminho informado existe e tem permissão de leitura.
- Reinicie o servidor Flask e tente novamente.

### Relatório JSON não aparece na lista de logs

- O scan pode ter falhado antes de gravar o arquivo. Veja o log de sistema (`/scan/logs?secao=sistema`).
- O arquivo é gravado em `flask-python/logs/scan_projeto/`. Verifique permissão de escrita.

---

## 🤖 Problemas específicos da IA local (LM Studio)

### `DESCONECTADO (LM Studio offline)`

- Verifique se o LM Studio está aberto e o servidor iniciado na porta **1234**.
- Teste diretamente: `curl http://localhost:1234/v1/models`

### Timeout / lentidão na análise

- Use um modelo com quantização mais agressiva (ex.: Q4_K_M em vez de Q8).
- Feche outros apps que usam GPU.
- O timeout padrão é 60 s por requisição (`executar_scan_ia.py`).

### Parecer vazio ou erro HTTP

- Verifique `api_python/logs/erro_sistema.log`.
- Verifique o log do motor: `logs/amd/system/sistema_amd.log` ou `logs/nvidia/system/sistema_nvidia.log`.

---

## ❓ FAQ

**Qual é o módulo principal para usar?**
`flask-python` — tem interface web completa. Execute `python app.py` na pasta `flask-python/`.

**Preciso usar Docker?**
Não. O modo local (`python app.py`) funciona bem para desenvolvimento e laboratório.

**Qual arquivo é o ponto de entrada do flask-python?**
`flask-python/app.py` (chama `create_app` de `flask-python/app/web/app.py`).

**Qual arquivo é o ponto de entrada do api_python?**
`api_python/main.py`.

**Onde fica a equipe do projeto?**
Na tela `/sobre` da interface web ou em `api_python/app/ui/sobre/sobre.py`. Ver também: [👥 14 - Equipe](./09-equipe.md).

**Onde ficam os relatórios de scan?**
- Scan de projeto: `flask-python/logs/scan_projeto/` (JSON).
- Scan IA AMD: `api_python/logs/amd/reports/` (JSON + MD + TXT).
- Scan IA NVIDIA: `api_python/logs/nvidia/reports/` (JSON + MD + TXT).

**Os testes passam todos?**
Sim — 48 testes pytest OK. Execute `python -m pytest tests/ -q` em cada módulo.

---

**Próxima leitura recomendada:** [🚀 07 - Roadmap e Próximos Passos](./07-roadmap.md)
