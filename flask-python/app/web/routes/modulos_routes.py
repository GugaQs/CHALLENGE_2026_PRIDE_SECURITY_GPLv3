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

"""Rotas web para modulos em evolucao (paridade com menus CLI)."""

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.web.services.modulos_service import (
    configurar_api_key,
    configurar_provedor,
    executar_scan_docker,
    executar_varredura_ia_api,
    iniciar_scan_docker_assincrono,
    listar_programas_instalados,
    obter_config_ia_api,
    obter_provedores_ia_api,
    obter_status_scan_docker,
)


modulos_bp = Blueprint("modulos", __name__, url_prefix="/modulos")


@modulos_bp.route("/scan-software", methods=["GET", "POST"])
def scan_software():
    """Scan de software instalado."""
    programas = []
    mensagem = None
    if request.method == "POST":
        programas, mensagem = listar_programas_instalados(
            limite=request.form.get("limite", default=50, type=int) or 50
        )
        flash(mensagem or "Listagem concluida.", "success" if programas else "error")

    return render_template(
        "scan_git_hub/modulo_scan_software.html",
        programas=programas,
    )


@modulos_bp.route("/ia-api", methods=["GET", "POST"])
def scan_ia_api():
    """Configuracao e varredura IA via API."""
    config = obter_config_ia_api()

    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "provedor":
            ok, msg = configurar_provedor(request.form.get("provedor"))
            flash(msg, "success" if ok else "error")
        elif acao == "api_key":
            ok, msg = configurar_api_key(request.form.get("api_key"))
            flash(msg, "success" if ok else "error")
        elif acao == "varredura":
            ok, msg = executar_varredura_ia_api(request.form.get("caminho"))
            flash(msg, "success" if ok else "error")
        return redirect(url_for("modulos.scan_ia_api"))

    return render_template(
        "ia_api/modulo_ia_api.html",
        config=obter_config_ia_api(),
        provedores=obter_provedores_ia_api(),
    )


@modulos_bp.route("/containers/executar-assincrono", methods=["POST"])
def executar_containers_assincrono():
    """Inicia scan Docker com barra de progresso (JSON)."""
    payload = request.get_json(silent=True) or {}
    ok, mensagem, job_id = iniciar_scan_docker_assincrono(payload.get("caminho"))
    status_http = 200 if ok else 400
    return jsonify({"ok": ok, "mensagem": mensagem, "job_id": job_id}), status_http


@modulos_bp.route("/containers/status/<job_id>", methods=["GET"])
def status_scan_containers(job_id):
    """Status do job de scan Docker."""
    status = obter_status_scan_docker(job_id)
    if not status:
        return jsonify({"ok": False, "mensagem": "Job nao encontrado."}), 404
    return jsonify({"ok": True, "dados": status}), 200


@modulos_bp.route("/containers", methods=["GET", "POST"])
def scan_containers():
    """Scan de artefatos Docker."""
    artefatos = None
    if request.method == "POST":
        ok, msg, artefatos = executar_scan_docker(request.form.get("caminho"))
        flash(msg, "success" if ok else "error")

    return render_template(
        "containers/modulo_containers.html",
        artefatos=artefatos,
    )


@modulos_bp.route("/scan-github-problema", methods=["GET"])
def scan_github_problema():
    """Pagina explicativa sobre limitacoes de scans automaticos no GitHub."""
    return render_template("scan_git_hub/modulo_scan_github_problema.html")
