# 🛠️ 10 - Operacao e Manutencao

<p align="left">
  <img src="https://img.shields.io/badge/Doc-Operacao-1f6feb?style=flat&logo=opsgenie&logoColor=white" alt="Operacao">
  <img src="https://img.shields.io/badge/Foco-Runbook-2ea44f?style=flat&logo=bookstack&logoColor=white" alt="Runbook">
</p>

**Navegacao:** [📚 Dicionario](./README.md) • [🧩 Anterior: Modulos](./04-modulos-responsabilidades.md) • [🧯 Proximo: Troubleshooting](./06-troubleshooting-faq.md)

## 🔁 Rotina recomendada de desenvolvimento

1. Atualizar branch local.
2. Ativar ambiente virtual.
3. Instalar dependencias se necessario.
4. Rodar aplicacao localmente.
5. Validar fluxo alterado.
6. Atualizar documentacao quando houver mudanca funcional.

## ⌨️ Comandos uteis

Atualizar dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Recriar ambiente virtual:

```bash
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## ✅ Boas praticas

- Evitar hardcode de caminho absoluto.
- Manter nomes de funcoes descritivos.
- Revisar README e docs a cada funcionalidade nova.

---

**Proxima leitura recomendada:** [🧯 06 - Troubleshooting e FAQ](./06-troubleshooting-faq.md)
