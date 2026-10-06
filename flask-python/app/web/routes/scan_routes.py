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

"""Rotas web para scan de projeto, logs e filtros avancados."""

import json
import unicodedata

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.web.services.scan_filtro_service import (
    aplicar_filtro_relatorio,
    montar_filtros_do_formulario,
    obter_agrupamentos,
    obter_opcoes_filtro,
)
from app.ui.scan_projeto.listar_falhas import enriquecer_falhas_para_web
from app.web.services.log_sistema_service import classificar_linhas_log
from app.web.services.scan_service import (
    abrir_arquivo_por_falha,
    calcular_score_risco,
    executar_scan,
    iniciar_scan_assincrono,
    ler_log_sistema,
    limpar_logs,
    listar_logs,
    listar_logs_sistema,
    obter_log,
    obter_status_scan,
    selecionar_pasta_sistema,
)


scan_bp = Blueprint("scan", __name__, url_prefix="/scan")


def _classificar_severidade(texto):
    """Classifica severidade textual para filtro web (trata acentos)."""
    valor = unicodedata.normalize("NFD", str(texto or ""))
    valor = valor.encode("ascii", "ignore").decode("ascii").upper()
    if "CRIT" in valor:
        return "CRITICO"
    if "ALTO" in valor or "ALTA" in valor:
        return "ALTO"
    if "MED" in valor:
        return "MEDIO"
    return "BAIXO"


def _filtrar_falhas_pagina(falhas, args):
    """Aplica filtros simples da URL e paginacao."""
    filtro_severidade = (args.get("severidade") or "").strip().upper()
    filtro_tipo = (args.get("tipo") or "").strip()
    filtro_arquivo = (args.get("arquivo") or "").strip().lower()

    filtradas = []
    for falha in falhas:
        if filtro_severidade and _classificar_severidade(falha.get("severidade")) != filtro_severidade:
            continue
        if filtro_tipo and str(falha.get("tipo", "")).strip() != filtro_tipo:
            continue
        if filtro_arquivo and filtro_arquivo not in str(falha.get("arquivo", "")).lower():
            continue
        filtradas.append(falha)

    pagina = args.get("pagina", default=1, type=int) or 1
    por_pagina = args.get("por_pagina", default=50, type=int) or 50
    por_pagina = max(1, min(por_pagina, 50))

    total = len(filtradas)
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    pagina = max(1, min(pagina, total_paginas))
    inicio = (pagina - 1) * por_pagina
    fim = min(inicio + por_pagina, total)

    return filtradas, filtradas[inicio:fim], pagina, por_pagina, total, total_paginas, inicio, fim


@scan_bp.route("/", methods=["GET"])
def pagina_scan():
    """Formulario de scan de projeto."""
    return render_template("scan/scan.html")


@scan_bp.route("/executar", methods=["POST"])
def executar_scan_rota():
    """Executa scan sincrono."""
    ok, mensagem, nome_log = executar_scan(request.form.get("caminho"))
    flash(mensagem, "success" if ok else "error")
    if ok and nome_log:
        return redirect(url_for("scan.detalhe_log", nome_log=nome_log))
    return redirect(url_for("scan.pagina_scan"))


@scan_bp.route("/executar-assincrono", methods=["POST"])
def executar_scan_assincrono_rota():
    """Inicia scan assincrono (JSON)."""
    payload = request.get_json(silent=True) or {}
    ok, mensagem, job_id = iniciar_scan_assincrono(payload.get("caminho"))
    status_http = 200 if ok else 400
    return jsonify({"ok": ok, "mensagem": mensagem, "job_id": job_id}), status_http


@scan_bp.route("/status/<job_id>", methods=["GET"])
def status_scan(job_id):
    """Status do job de scan."""
    status = obter_status_scan(job_id)
    if not status:
        return jsonify({"ok": False, "mensagem": "Job nao encontrado."}), 404
    return jsonify({"ok": True, "dados": status}), 200


@scan_bp.route("/logs", methods=["GET"])
def pagina_logs():
    """Lista relatorios e logs de sistema."""
    secao = request.args.get("secao", "scan")
    if secao not in {"sistema", "scan"}:
        secao = "scan"
    return render_template(
        "scan_logs/scan_logs.html",
        logs_scan=listar_logs(),
        logs_sistema=listar_logs_sistema(),
        secao_ativa=secao,
    )


@scan_bp.route("/logs/estado", methods=["GET"])
def estado_logs():
    """Estado dos logs para polling AJAX."""
    return jsonify(
        {
            "ok": True,
            "logs_sistema": listar_logs_sistema(),
            "logs_scan": listar_logs(),
        }
    )


@scan_bp.route("/logs/sistema/<path:nome_log>", methods=["GET"])
def visualizar_log_sistema(nome_log):
    """Visualiza log tecnico (via scan/logs)."""
    conteudo = ler_log_sistema(nome_log)
    if conteudo is None:
        flash("Log de sistema nao encontrado.", "error")
        return redirect(url_for("scan.pagina_logs"))
    return render_template(
        "log/log_sistema_detalhe.html",
        nome_log=nome_log,
        linhas_log=classificar_linhas_log(conteudo),
        voltar_url=url_for("scan.pagina_logs", secao="sistema"),
    )


@scan_bp.route("/logs/<nome_log>", methods=["GET"])
def detalhe_log(nome_log):
    """Detalhe de relatorio JSON com filtros e paginacao."""
    dados = obter_log(nome_log)
    if not dados:
        flash("Log nao encontrado.", "error")
        return redirect(url_for("scan.pagina_logs"))

    falhas = dados.get("vulnerabilidades", [])
    tipos = sorted({str(f.get("tipo", "")).strip() for f in falhas if f.get("tipo")})
    severidades = ["CRITICO", "ALTO", "MEDIO", "BAIXO"]

    filtradas, pagina_falhas, pagina, por_pagina, total, total_paginas, inicio, fim = (
        _filtrar_falhas_pagina(falhas, request.args)
    )
    enriquecer_falhas_para_web(pagina_falhas)

    resumo = {"critico": 0, "alto": 0, "medio": 0, "baixo": 0}
    for falha in falhas:
        cat = _classificar_severidade(falha.get("severidade"))
        resumo[cat.lower()] = resumo.get(cat.lower(), 0) + 1

    score_risco = calcular_score_risco(
        resumo["critico"], resumo["alto"], resumo["medio"], resumo["baixo"]
    )

    return render_template(
        "scan_logs/scan_log_detalhe.html",
        dados=dados,
        falhas=filtradas,
        falhas_pagina=pagina_falhas,
        nome_log=nome_log,
        resumo_severidade=resumo,
        score_risco=score_risco,
        pagina=pagina,
        por_pagina=por_pagina,
        total_paginas=total_paginas,
        inicio_exibicao=(inicio + 1 if total > 0 else 0),
        fim_exibicao=fim,
        total_falhas=total,
        total_falhas_geral=len(falhas),
        opcoes_por_pagina=[10, 20, 30, 40, 50],
        filtro_severidade=(request.args.get("severidade") or "").strip().upper(),
        filtro_tipo=(request.args.get("tipo") or "").strip(),
        filtro_arquivo=(request.args.get("arquivo") or "").strip().lower(),
        tipos_disponiveis=tipos,
        severidades_disponiveis=severidades,
    )


@scan_bp.route("/logs/<nome_log>/filtros", methods=["GET", "POST"])
def filtros_avancados(nome_log):
    """Filtros avancados (paridade com listar/menu_listar CLI)."""
    dados = obter_log(nome_log)
    if not dados:
        flash("Relatorio nao encontrado.", "error")
        return redirect(url_for("scan.pagina_logs"))

    opcoes = obter_opcoes_filtro(nome_log)
    ranking = []
    nome_filtrado = None

    if request.method == "POST":
        filtros = montar_filtros_do_formulario(request.form)
        ok, mensagem, nome_filtrado, ranking = aplicar_filtro_relatorio(nome_log, filtros)
        flash(mensagem, "success" if ok else "error")
        if ok and nome_filtrado:
            return redirect(url_for("scan.detalhe_log", nome_log=nome_filtrado))

    return render_template(
        "filtros/scan_filtros.html",
        nome_log=nome_log,
        dados=dados,
        opcoes=opcoes,
        agrupamento_tipo=obter_agrupamentos(nome_log, "tipo"),
        agrupamento_severidade=obter_agrupamentos(nome_log, "severidade"),
    )


@scan_bp.route("/logs/<nome_log>/json", methods=["GET"])
def visualizar_log_json(nome_log):
    """JSON bruto do relatorio."""
    dados = obter_log(nome_log)
    if not dados:
        flash("Log JSON nao encontrado.", "error")
        return redirect(url_for("scan.pagina_logs", secao="scan"))
    conteudo_json = json.dumps(dados, ensure_ascii=False, indent=4)
    return render_template(
        "scan_git_hub/scan_log_json_detalhe.html",
        nome_log=nome_log,
        conteudo_json=conteudo_json,
    )


@scan_bp.route("/logs/limpar", methods=["POST"])
def limpar_logs_rota():
    """Remove todos os relatorios JSON de scan generico."""
    ok, mensagem = limpar_logs()
    flash(mensagem, "success" if ok else "error")
    return redirect(url_for("scan.pagina_logs", secao="scan"))


@scan_bp.route("/selecionar-pasta", methods=["POST"])
def selecionar_pasta():
    """Seletor de pasta nativo (JSON)."""
    ok, mensagem, caminho = selecionar_pasta_sistema()
    status_http = 200 if ok else 400
    return jsonify({"ok": ok, "mensagem": mensagem, "caminho": caminho}), status_http


@scan_bp.route("/logs/<nome_log>/abrir-falha", methods=["POST"])
def abrir_arquivo_falha(nome_log):
    """Abre arquivo da falha no SO (JSON)."""
    payload = request.get_json(silent=True) or {}
    ok, mensagem = abrir_arquivo_por_falha(nome_log, payload.get("falha_id"))
    status_http = 200 if ok else 400
    return jsonify({"ok": ok, "mensagem": mensagem}), status_http
