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

"""Servicos de listagem e filtros para logs de scan."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, timezone

from app.utils.tempo import (
    obter_timestamp,
    obter_timestamp_sistema,
    obter_timestamp_utc_brasil,
)
from app.utils.log_sistema import get_logger

_log = get_logger("scan_listar_service")

SEVERIDADE_PESO = {
    "CRÍTICO": 4,
    "ALTO": 3,
    "MÉDIO": 2,
    "BAIXO": 1,
}


def carregar_falhas(dados_log):
    """Extrai lista de falhas do json de scan com fallback de chaves."""
    return dados_log.get("vulnerabilidades", []) or dados_log.get("falhas_encontradas", [])


def agrupar_por_campo(falhas, campo):
    """Retorna dicionario com agrupamento por campo informado."""
    grupos = defaultdict(list)
    for falha in falhas:
        chave = falha.get(campo, "N/A")
        grupos[chave].append(falha)
    return dict(grupos)


def filtrar_falhas(falhas, filtros):
    """Aplica filtros combinados em formato de dicionario."""
    resultado = []
    for falha in falhas:
        if filtros.get("tipo") and falha.get("tipo") not in filtros["tipo"]:
            continue
        if filtros.get("severidade") and falha.get("severidade") not in filtros["severidade"]:
            continue
        if filtros.get("confianca") and falha.get("confianca") not in filtros["confianca"]:
            continue
        if filtros.get("arquivo_contem"):
            if filtros["arquivo_contem"].lower() not in str(falha.get("arquivo", "")).lower():
                continue
        if filtros.get("linha_min") is not None and int(falha.get("linha", 0)) < filtros["linha_min"]:
            continue
        if filtros.get("linha_max") is not None and int(falha.get("linha", 0)) > filtros["linha_max"]:
            continue
        if filtros.get("codigo_contem"):
            if filtros["codigo_contem"].lower() not in str(falha.get("codigo", "")).lower():
                continue
        resultado.append(falha)
    return resultado


def ranking_arquivos_criticos(falhas, top_n=10):
    """Calcula score por arquivo para priorizacao de correcao."""
    score_por_arquivo = defaultdict(int)
    qtd_por_arquivo = defaultdict(int)

    for falha in falhas:
        arquivo = falha.get("arquivo", "N/A")
        sev = str(falha.get("severidade", "BAIXO")).upper()
        peso = SEVERIDADE_PESO.get(sev, 1)
        score_por_arquivo[arquivo] += peso
        qtd_por_arquivo[arquivo] += 1

    ranking = []
    for arquivo, score in score_por_arquivo.items():
        ranking.append(
            {
                "arquivo": arquivo,
                "score": score,
                "qtd_falhas": qtd_por_arquivo[arquivo],
            }
        )

    ranking.sort(key=lambda item: (item["score"], item["qtd_falhas"]), reverse=True)
    return ranking[:top_n]


def _pasta_logs_scan():
    """Pasta de logs do scan (mesma de `executar_scan.salvar_log_json`)."""
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    return os.path.join(base, "logs", "generic", "reports")


def serializar_filtros(filtros):
    """Converte filtros (incl. sets) para dict JSON-serializavel."""
    out = {}
    for chave, valor in filtros.items():
        if isinstance(valor, set):
            out[chave] = sorted(valor)
        else:
            out[chave] = valor
    return out


def salvar_relatorio_filtrado(
    dados_originais: dict,
    filtros: dict,
    vulnerabilidades: list,
    caminho_log_origem: str,
    top_ranking: int = 50,
) -> str:
    """
    Grava JSON com falhas filtradas e metadados de auditoria.

    Nome: report_filtrado_YYYYMMDD_HHMMSS.json (UTC) em app/ui/scan_projeto/logs/
    """
    pasta = _pasta_logs_scan()
    os.makedirs(pasta, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"report_filtrado_{ts}.json"
    caminho_completo = os.path.join(pasta, nome_arquivo)

    payload = {
        "origem_relatorio": os.path.abspath(caminho_log_origem),
        "projeto": dados_originais.get("projeto"),
        "caminho_total": dados_originais.get("caminho_total"),
        "timestamp_geracao_utc_global": obter_timestamp(),
        "timestamp_geracao_utc_brasil": obter_timestamp_utc_brasil(),
        "timestamp_geracao_sistema": obter_timestamp_sistema(),
        "timestamp_relatorio_origem_utc": dados_originais.get("timestamp_utc_global"),
        "filtros_aplicados": serializar_filtros(filtros),
        "total_falhas_filtradas": len(vulnerabilidades),
        "ranking_arquivos": ranking_arquivos_criticos(
            vulnerabilidades, top_n=top_ranking
        ),
        "vulnerabilidades": vulnerabilidades,
    }

    try:
        with open(caminho_completo, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)
    except OSError:
        _log.exception(
            "Falha ao gravar relatorio filtrado: %s", caminho_completo
        )
        raise
    _log.info(
        "Relatorio filtrado gravado (%s falhas): %s",
        len(vulnerabilidades),
        caminho_completo,
    )
    return caminho_completo
