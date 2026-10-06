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

"""Servicos web de filtros avancados — delega para app.ui.scan_projeto.listar.service."""

import os

from app.ui.scan_projeto.listar.service import (
    agrupar_por_campo,
    carregar_falhas,
    filtrar_falhas,
    ranking_arquivos_criticos,
    salvar_relatorio_filtrado,
)
from app.web.services.scan_service import obter_caminho_log, obter_log


def montar_filtros_do_formulario(form):
    """Converte formulario HTTP em dict de filtros do motor."""
    filtros = {}

    tipo = (form.get("tipo") or "").strip()
    if tipo:
        filtros["tipo"] = {tipo}

    severidade = (form.get("severidade") or "").strip()
    if severidade:
        filtros["severidade"] = {severidade}

    confianca = (form.get("confianca") or "").strip()
    if confianca:
        filtros["confianca"] = {confianca}

    arquivo_contem = (form.get("arquivo_contem") or "").strip()
    if arquivo_contem:
        filtros["arquivo_contem"] = arquivo_contem

    codigo_contem = (form.get("codigo_contem") or "").strip()
    if codigo_contem:
        filtros["codigo_contem"] = codigo_contem

    linha_min = (form.get("linha_min") or "").strip()
    if linha_min.isdigit():
        filtros["linha_min"] = int(linha_min)

    linha_max = (form.get("linha_max") or "").strip()
    if linha_max.isdigit():
        filtros["linha_max"] = int(linha_max)

    return filtros


def aplicar_filtro_relatorio(nome_log, filtros):
    """Aplica filtros e grava report_filtrado_*.json."""
    dados = obter_log(nome_log)
    if not dados:
        return False, "Relatorio nao encontrado.", None, []

    caminho_origem = obter_caminho_log(nome_log)
    falhas = carregar_falhas(dados)
    filtradas = filtrar_falhas(falhas, filtros)

    if not filtradas:
        return False, "Nenhuma falha corresponde aos filtros informados.", None, []

    caminho_novo = salvar_relatorio_filtrado(
        dados,
        filtros,
        filtradas,
        caminho_origem,
    )
    return (
        True,
        f"Relatorio filtrado salvo ({len(filtradas)} falhas).",
        os.path.basename(caminho_novo),
        ranking_arquivos_criticos(filtradas),
    )


def obter_opcoes_filtro(nome_log):
    """Lista valores unicos para selects do formulario de filtro."""
    dados = obter_log(nome_log)
    if not dados:
        return {"tipos": [], "severidades": [], "confiancas": []}

    falhas = carregar_falhas(dados)
    tipos = sorted({str(f.get("tipo", "")).strip() for f in falhas if f.get("tipo")})
    severidades = sorted(
        {str(f.get("severidade", "")).strip() for f in falhas if f.get("severidade")}
    )
    confiancas = sorted(
        {str(f.get("confianca", "")).strip() for f in falhas if f.get("confianca")}
    )
    return {"tipos": tipos, "severidades": severidades, "confiancas": confiancas}


def obter_agrupamentos(nome_log, campo):
    """Retorna agrupamento por campo para painel analitico."""
    dados = obter_log(nome_log)
    if not dados:
        return {}
    return agrupar_por_campo(carregar_falhas(dados), campo)
