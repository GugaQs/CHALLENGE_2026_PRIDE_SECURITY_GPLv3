# Copyright (C) 2026 Equipe ASPM IA FIAP - Challenge 2026
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See LICENSE.md
# for the full GNU General Public License.

"""
Motor de análise de vulnerabilidades usando IA Local (LLM).
Versão 3.2: Cabeçalho de relatório alinhado ao JSON de scan (metadados + contexto ASPM).
"""

import os
import json
import requests
import subprocess
from colorama import Fore, Style
from app.utils.log_sistema import get_logger
from app.utils.tempo import (
    obter_timestamp,
    obter_timestamp_sistema,
    obter_timestamp_utc_brasil,
)

_log = get_logger("scan_ia_engine")
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

_ASPM_CONTEXTO_PRODUTO = (
    "Stack atual do projeto (referência para o relatório): "
    "CLI ASPM PRIDE 2026; scan por assinaturas com metadados UTC global, UTC-03 fixo e hora do sistema; "
    "scan clássico: `logs/` + `report_*` e `report_filtrado_*` em `scan_projeto/logs/`; "
    "IA local AMD/NVIDIA: JSON e pareceres em `logs/amd/reports/` e `logs/nvidia/reports/`, "
    "com trilha por GPU em `logs/amd/system/sistema_amd.log` e `logs/nvidia/system/sistema_nvidia.log`; "
    "logger central `logs/erro_sistema.log`; LM Studio em localhost:1234."
)


def testar_conexao_gpu():
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code == 200:
            return True, response.json()["data"][0]["id"]
    except Exception:
        pass
    return False, None

def analisar_com_ia_local(prompt, sistema):
    model_id = "local-model"
    try:
        res_models = requests.get("http://localhost:1234/v1/models", timeout=2)
        if res_models.status_code == 200:
            model_data = res_models.json().get("data", [])
            if model_data:
                model_id = model_data[0]["id"]
    except Exception as e:
        _log.warning("Falha ao buscar ID do modelo, tentando fallback: %s", e)

    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": sistema},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    try:
        response = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            _log.error("Erro da IA (HTTP %s): %s", response.status_code, response.text)
            return f"Falha na resposta da IA: HTTP {response.status_code} - {response.text}"
    except Exception as e:
        _log.exception("Excecao na conexao com IA local.")
        return f"Falha na resposta da IA: {str(e)}"


def _montar_cabecalho_markdown(caminho_json: str, dados: dict | None) -> str:
    """Bloco inicial do .md com metadados do scan e instante de geração do parecer."""
    dados = dados or {}
    agora_utc = obter_timestamp()
    agora_br = obter_timestamp_utc_brasil()
    agora_sys = obter_timestamp_sistema()
    projeto = dados.get("projeto", "—")
    caminho_total = dados.get("caminho_total", "—")
    hardware = dados.get("hardware", "—")
    motor = dados.get("motor_relatorio", dados.get("schema_version", "—"))
    ts_scan = dados.get("timestamp_utc_global", "—")
    ts_br_scan = dados.get("timestamp_utc_brasil", "—")
    ts_sys_scan = dados.get("timestamp_sistema", "—")
    total_arq = dados.get("total_arquivos_analisados", "—")
    n_falhas = len(dados.get("vulnerabilidades") or [])

    return f"""# 🛡️ Relatório cognitivo ASPM — PRIDE Security 2026

---

## Metadados do scan (fonte JSON)

| Campo | Valor |
| :--- | :--- |
| Arquivo fonte | `{os.path.basename(caminho_json)}` |
| Projeto | {projeto} |
| Caminho analisado | `{caminho_total}` |
| Hardware / perfil | {hardware} |
| Motor / versão schema | {motor} |
| Timestamp scan (UTC) | {ts_scan} |
| Timestamp scan (UTC-03) | {ts_br_scan} |
| Timestamp scan (sistema) | {ts_sys_scan} |
| Total arquivos analisados | {total_arq} |
| Total de achados (lista) | {n_falhas} |

## Geração deste parecer (IA local)

| Campo | Valor |
| :--- | :--- |
| Parecer gerado em (UTC) | {agora_utc} |
| Parecer gerado em (UTC-03) | {agora_br} |
| Parecer gerado (sistema) | {agora_sys} |

## Contexto do produto

{_ASPM_CONTEXTO_PRODUTO}

---

## Parecer técnico (LLM)

"""


def salvar_relatorios_ia(caminho_json, parecer, dados_fonte: dict | None = None):
    base_name = caminho_json.replace(".json", "")
    caminho_md = f"{base_name}_AI_PREMIUM.md"
    caminho_txt = f"{base_name}_AI_LEITURA.txt"

    header_md = _montar_cabecalho_markdown(caminho_json, dados_fonte)

    with open(caminho_md, "w", encoding="utf-8") as f:
        f.write(header_md + parecer)

    # Conteúdo TXT mais limpo para impressão
    txt_header = (
        f"RELATORIO PRIDE SECURITY - {obter_timestamp()} UTC\n"
        f"Fonte: {os.path.basename(caminho_json)}\n"
        + "-" * 60
        + "\n"
    )
    txt_content = parecer.replace("#", "").replace("**", "").replace("`", "")
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(txt_header)
        f.write(txt_content)

    return caminho_md, caminho_txt

def imprimir_relatorio(caminho_arquivo):
    """Imprime usando o comando de sistema para evitar erros de associação."""
    try:
        if os.name == 'nt':
            print(Fore.YELLOW + f"🖨️  Enviando '{os.path.basename(caminho_arquivo)}' para a impressora padrão...")
            # Usamos o Notepad /p que é o comando padrão de impressão do Windows
            subprocess.run(["notepad.exe", "/p", caminho_arquivo], check=True)
            return True
    except Exception as e:
        print(Fore.RED + f"❌ Erro ao imprimir: {e}")
    return False

def formatar_saida_terminal(texto):
    linhas = texto.split("\n")
    saida = []
    for linha in linhas:
        if linha.startswith("#"):
            saida.append(Fore.WHITE + Style.BRIGHT + linha.replace("#", "■") + Style.RESET_ALL)
        elif "**" in linha:
            saida.append(Fore.CYAN + linha.replace("**", "") + Style.RESET_ALL)
        else:
            saida.append(Fore.WHITE + linha)
    return "\n".join(saida)

def analisar_relatorio_existente(caminho_json):
    if not os.path.exists(caminho_json):
        return (
            Fore.RED + "Arquivo JSON não encontrado." + Style.RESET_ALL,
            None,
            None,
        )
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)
    vulnerabilidades = dados.get("vulnerabilidades", [])
    if not vulnerabilidades:
        return (
            Fore.YELLOW + "Nenhuma vulnerabilidade neste relatório para enviar à IA."
            + Style.RESET_ALL,
            None,
            None,
        )

    print(Fore.MAGENTA + "\n🧠 Processando análise cognitiva via IA...")
    linhas_ctx = [
        "Resumo do scan (use como contexto; o parecer deve citar risco, prioridade e possíveis falsos positivos):",
        f"- Projeto: {dados.get('projeto', '?')}",
        f"- Caminho: {dados.get('caminho_total', '?')}",
        f"- Hardware/perfil: {dados.get('hardware', 'n/d')}",
        f"- Total de achados: {len(vulnerabilidades)}",
        "",
        "Achados (amostra para análise):",
    ]
    amostra = vulnerabilidades[:20]
    for v in amostra:
        idx = v.get("indice", "?")
        tipo = v.get("tipo", "?")
        arq = v.get("arquivo", "?")
        linha = v.get("linha", "?")
        sev = v.get("severidade", "?")
        cod = str(v.get("codigo", ""))[:200]
        linhas_ctx.append(
            f"- ID {idx} | {sev} | {tipo} | {arq}:{linha} | trecho: {cod}"
        )

    sistema_prompt = (
        "Você é um CSO sênior. Gere relatório em Markdown com seções claras, "
        "tabela de priorização (crítico/alto/médio/baixo), riscos, falsos positivos prováveis "
        "e próximos passos técnicos. Mencione que o scan é por assinaturas (ASPM educativo) "
        "e que validação final é humana."
    )
    prompt = (
        _ASPM_CONTEXTO_PRODUTO
        + "\n\n"
        + "\n".join(linhas_ctx)
        + "\n\nElabore o relatório executivo com base na amostra acima."
    )

    parecer = analisar_com_ia_local(prompt, sistema_prompt)
    md, txt = salvar_relatorios_ia(caminho_json, parecer, dados)
    return formatar_saida_terminal(parecer), md, txt
