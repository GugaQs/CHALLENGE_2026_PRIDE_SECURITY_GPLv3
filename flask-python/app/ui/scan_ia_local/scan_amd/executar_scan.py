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

"""Motor de varredura OTIMIZADO PARA AMD RADEON.
Captura completa de metadados (CWE, CVE, Descrição).
"""

import os
import json
import datetime
from colorama import Fore, Style
from app.utils.log_sistema import get_logger, get_hardware_logger
from app.utils.progresso_scan import notificar_progresso
from app.utils.tempo import obter_timestamp, obter_timestamp_utc_brasil, obter_timestamp_sistema

# Importando regras locais do pacote AMD
from .filtros.regras_seguranca import (
    obter_assinaturas_vulnerabilidade, 
    obter_extensoes_permitidas,
    obter_diretorios_ignorados,
    ordenar_por_severidade,
)

_log = get_hardware_logger("amd")

def exibir_progresso_amd(atual, total):
    if total == 0: return
    largura = 40
    prog = int((atual / total) * largura)
    perc = int((atual / total) * 100)
    barra = "█" * prog + "-" * (largura - prog)
    print(f"\r{Fore.RED}Progresso AMD: |{barra}| {perc}% ({atual}/{total})", end="", flush=True)

def salvar_log_json_amd(dados_scan):
    # Agora salvando na pasta central de logs/amd/reports conforme pedido
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    pasta_logs = os.path.join(base, "logs", "amd", "reports")
    
    if not os.path.exists(pasta_logs): 
        os.makedirs(pasta_logs, exist_ok=True)
        
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    nome = os.path.join(pasta_logs, f"amd_report_{timestamp}.json")
    with open(nome, "w", encoding="utf-8") as f:
        json.dump(dados_scan, f, indent=4, ensure_ascii=False)
    _log.info(f"Relatório AMD JSON salvo em: {nome}")
    return nome

def rodar_engine_scan_amd(caminho_alvo, progress_callback=None, silent=False):
    assinaturas = obter_assinaturas_vulnerabilidade()
    extensoes = obter_extensoes_permitidas()
    ignorados = obter_diretorios_ignorados()

    todos_arquivos = []
    for r, p, f in os.walk(caminho_alvo):
        p[:] = [d for d in p if d not in ignorados]
        for arq in f:
            if any(arq.endswith(ext) for ext in extensoes):
                todos_arquivos.append(os.path.join(r, arq))

    total = len(todos_arquivos)
    if not silent:
        print(Fore.RED + f"\n🔍 [AMD RADEON MODE] Escaneando {total} arquivos...\n")
    notificar_progresso(progress_callback, 0, total, "Iniciando scan AMD...")

    vulnerabilidades_temp = []

    for i, caminho_file in enumerate(todos_arquivos, 1):
        try:
            with open(caminho_file, "r", encoding="utf-8", errors="ignore") as f:
                for num_linha, linha in enumerate(f, 1):
                    linha_texto = linha.strip()
                    for tipo, regra in assinaturas.items():
                        padroes = regra[0]
                        severidade = regra[1]
                        descricao = regra[2] if len(regra) > 2 else ""
                        confianca = regra[3] if len(regra) > 3 else "-"
                        referencias = regra[4] if len(regra) > 4 else []
                        
                        for padrao in padroes:
                            if padrao.lower() in linha_texto.lower():
                                vulnerabilidades_temp.append({
                                    "tipo": tipo,
                                    "severidade": severidade,
                                    "descricao": descricao,
                                    "confianca": confianca,
                                    "referencias": referencias,
                                    "arquivo": os.path.basename(caminho_file),
                                    "caminho_completo": caminho_file,
                                    "linha": num_linha,
                                    "codigo": linha_texto[:150],
                                    "padrao_detectado": padrao,
                                    "timestamp_utc_global": obter_timestamp(),
                                    "timestamp_utc_brasil": obter_timestamp_utc_brasil(),
                                    "timestamp_sistema": obter_timestamp_sistema(),
                                })
        except Exception:
            pass
        if not silent:
            exibir_progresso_amd(i, total)
        notificar_progresso(progress_callback, i, total)

    if not silent:
        print("\n")
    vulnerabilidades_temp = ordenar_por_severidade(vulnerabilidades_temp)
    for idx, falha in enumerate(vulnerabilidades_temp, 1):
        falha["indice"] = idx

    relatorio = {
        "schema_version": "ASPM-2026.1",
        "motor_relatorio": "scan_ia_local_amd",
        "projeto": os.path.basename(caminho_alvo),
        "caminho_total": os.path.abspath(caminho_alvo),
        "hardware": "AMD Radeon RX 7800",
        "timestamp_utc_global": obter_timestamp(),
        "timestamp_utc_brasil": obter_timestamp_utc_brasil(),
        "timestamp_sistema": obter_timestamp_sistema(),
        "total_arquivos_analisados": total,
        "vulnerabilidades": vulnerabilidades_temp,
    }

    caminho_log = salvar_log_json_amd(relatorio)
    if progress_callback:
        progress_callback(
            {
                "status": "em_andamento",
                "mensagem": "Scan AMD concluido.",
                "percentual": 100,
                "atual": total,
                "total": total,
                "caminho_log": caminho_log,
            }
        )
    return caminho_log
