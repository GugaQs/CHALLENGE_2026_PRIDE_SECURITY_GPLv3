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

"""Rotas web para scan com IA local (AMD/NVIDIA)."""

import os
import unicodedata

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.web.services.ia_local_service import (
    _caminho_relatorio,
    analisar_relatorio_ia,
    executar_scan_cognitivo,
    executar_scan_gpu,
    iniciar_scan_cognitivo_assincrono,
    iniciar_scan_gpu_assincrono,
    imprimir_ultimo_parecer,
    obter_status_job_ia,
    ler_parecer_markdown,
    listar_relatorios_gpu,
    obter_dados_auditoria,
    obter_falha_auditoria,
    obter_gpu_padrao,
    obter_ultimo_parecer_md,
    reanalisar_ultimo_relatorio,
    status_lm_studio,
)


ia_local_bp = Blueprint("ia_local", __name__, url_prefix="/ia-local")


def _hardware_valido(valor):
    """Normaliza hardware para amd ou nvidia."""
    return "nvidia" if (valor or "").lower() == "nvidia" else "amd"


def _classificar_severidade(texto):
    """Normaliza severidade para filtros da UI (trata acentos)."""
    valor = unicodedata.normalize("NFD", str(texto or ""))
    valor = valor.encode("ascii", "ignore").decode("ascii").upper()
    if "CRIT" in valor:
        return "CRITICO"
    if "ALTO" in valor or "ALTA" in valor:
        return "ALTO"
    if "MED" in valor:
        return "MEDIO"
    return "BAIXO"


@ia_local_bp.route("/", methods=["GET"])
def pagina_ia_local():
    """Painel IA local."""
    hardware = _hardware_valido(request.args.get("hw") or obter_gpu_padrao())
    return render_template(
        "ia/ia_local.html",
        hardware=hardware,
        status_lm=status_lm_studio(),
        relatorios=listar_relatorios_gpu(hardware),
    )


@ia_local_bp.route("/executar-assincrono", methods=["POST"])
def executar_scan_ia_local_assincrono():
    """Inicia scan GPU com barra de progresso (JSON)."""
    payload = request.get_json(silent=True) or {}
    hardware = _hardware_valido(payload.get("hardware"))
    ok, mensagem, job_id = iniciar_scan_gpu_assincrono(
        hardware,
        payload.get("caminho"),
    )
    status_http = 200 if ok else 400
    return jsonify({"ok": ok, "mensagem": mensagem, "job_id": job_id}), status_http


@ia_local_bp.route("/cognitivo-assincrono", methods=["POST"])
def scan_cognitivo_assincrono():
    """Scan + IA com barra de progresso (JSON)."""
    payload = request.get_json(silent=True) or {}
    hardware = _hardware_valido(payload.get("hardware"))
    ok, mensagem, job_id = iniciar_scan_cognitivo_assincrono(
        hardware,
        payload.get("caminho"),
    )
    status_http = 200 if ok else 400
    return jsonify({"ok": ok, "mensagem": mensagem, "job_id": job_id}), status_http


@ia_local_bp.route("/status/<job_id>", methods=["GET"])
def status_job_ia_local(job_id):
    """Status de job assincrono IA local."""
    status = obter_status_job_ia(job_id)
    if not status:
        return jsonify({"ok": False, "mensagem": "Job nao encontrado."}), 404
    return jsonify({"ok": True, "dados": status}), 200


@ia_local_bp.route("/executar", methods=["POST"])
def executar_scan_ia_local():
    """Executa scan GPU."""
    hardware = _hardware_valido(request.form.get("hardware"))
    ok, mensagem, nome_log = executar_scan_gpu(hardware, request.form.get("caminho"))
    flash(mensagem, "success" if ok else "error")
    if ok and nome_log:
        return redirect(
            url_for("ia_local.auditoria_relatorio", hw=hardware, nome_log=nome_log)
        )
    return redirect(url_for("ia_local.pagina_ia_local", hw=hardware))


@ia_local_bp.route("/cognitivo", methods=["POST"])
def scan_cognitivo():
    """Scan + analise IA em um passo."""
    hardware = _hardware_valido(request.form.get("hardware"))
    ok, mensagem, nome_log, caminho_md, _ = executar_scan_cognitivo(
        hardware,
        request.form.get("caminho"),
    )
    flash(mensagem, "success" if ok else "error")
    if ok and caminho_md:
        return redirect(
            url_for(
                "ia_local.ver_parecer",
                hw=hardware,
                arquivo=os.path.basename(caminho_md),
            )
        )
    if ok and nome_log:
        return redirect(
            url_for("ia_local.auditoria_relatorio", hw=hardware, nome_log=nome_log)
        )
    return redirect(url_for("ia_local.pagina_ia_local", hw=hardware))


@ia_local_bp.route("/reanalisar", methods=["POST"])
def reanalisar_relatorio():
    """Re-analisa ultimo relatorio JSON da GPU."""
    hardware = _hardware_valido(request.form.get("hardware"))
    ok, mensagem, caminho_md, _ = reanalisar_ultimo_relatorio(hardware)
    flash(mensagem, "success" if ok else "error")
    if ok and caminho_md:
        return redirect(
            url_for(
                "ia_local.ver_parecer",
                hw=hardware,
                arquivo=os.path.basename(caminho_md),
            )
        )
    return redirect(url_for("ia_local.pagina_ia_local", hw=hardware))


@ia_local_bp.route("/imprimir-parecer", methods=["POST"])
def imprimir_parecer():
    """Envia ultimo parecer para impressora."""
    hardware = _hardware_valido(request.form.get("hardware"))
    ok, mensagem = imprimir_ultimo_parecer(hardware)
    flash(mensagem, "success" if ok else "error")
    if ok:
        caminho = obter_ultimo_parecer_md(hardware)
        if caminho:
            return redirect(
                url_for(
                    "ia_local.ver_parecer",
                    hw=hardware,
                    arquivo=os.path.basename(caminho),
                )
            )
    return redirect(url_for("ia_local.pagina_ia_local", hw=hardware))


@ia_local_bp.route("/analisar", methods=["POST"])
def analisar_com_ia():
    """Analise cognitiva via LM Studio."""
    hardware = _hardware_valido(request.form.get("hardware"))
    nome = os.path.basename(request.form.get("relatorio") or "")
    caminho_json = _caminho_relatorio(hardware, nome)
    ok, mensagem, caminho_md, _ = analisar_relatorio_ia(caminho_json)
    flash(mensagem, "success" if ok else "error")
    if ok and caminho_md:
        return redirect(
            url_for(
                "ia_local.ver_parecer",
                hw=hardware,
                arquivo=os.path.basename(caminho_md),
            )
        )
    return redirect(url_for("ia_local.pagina_ia_local", hw=hardware))


@ia_local_bp.route("/auditoria/<hw>/<nome_log>", methods=["GET"])
def auditoria_relatorio(hw, nome_log):
    """Lista falhas do relatorio GPU para auditoria."""
    hardware = _hardware_valido(hw)
    auditoria = obter_dados_auditoria(hardware, nome_log)
    if not auditoria:
        flash("Relatorio nao encontrado.", "error")
        return redirect(url_for("ia_local.pagina_ia_local", hw=hardware))

    filtro_severidade = (request.args.get("severidade") or "").strip().upper()
    filtro_tipo = (request.args.get("tipo") or "").strip()
    filtro_arquivo = (request.args.get("arquivo") or "").strip().lower()

    todas_falhas = auditoria["falhas"]
    tipos_disponiveis = sorted({str(f.get("tipo", "")).strip() for f in todas_falhas if f.get("tipo")})

    filtradas = []
    for falha in todas_falhas:
        if filtro_severidade and _classificar_severidade(falha.get("severidade")) != filtro_severidade:
            continue
        if filtro_tipo and str(falha.get("tipo", "")).strip() != filtro_tipo:
            continue
        if filtro_arquivo and filtro_arquivo not in str(falha.get("arquivo", "")).lower():
            continue
        filtradas.append(falha)

    pagina = request.args.get("pagina", default=1, type=int) or 1
    por_pagina = request.args.get("por_pagina", default=50, type=int) or 50
    por_pagina = max(1, min(por_pagina, 50))

    total = len(filtradas)
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    pagina = max(1, min(pagina, total_paginas))
    inicio = (pagina - 1) * por_pagina
    fim = min(inicio + por_pagina, total)
    falhas_pagina = filtradas[inicio:fim]

    resumo = {"critico": 0, "alto": 0, "medio": 0, "baixo": 0}
    for falha in todas_falhas:
        categoria = _classificar_severidade(falha.get("severidade")).lower()
        resumo[categoria] = resumo.get(categoria, 0) + 1

    return render_template(
        "ia/ia_local_auditoria.html",
        hardware=hardware,
        dados=auditoria["dados"],
        falhas_pagina=falhas_pagina,
        nome_log=auditoria["nome_arquivo"],
        resumo_severidade=resumo,
        total_falhas_geral=len(todas_falhas),
        total_falhas=total,
        pagina=pagina,
        por_pagina=por_pagina,
        total_paginas=total_paginas,
        inicio_exibicao=(inicio + 1 if total > 0 else 0),
        fim_exibicao=fim,
        filtro_severidade=filtro_severidade,
        filtro_tipo=filtro_tipo,
        filtro_arquivo=filtro_arquivo,
        severidades_disponiveis=["CRITICO", "ALTO", "MEDIO", "BAIXO"],
        tipos_disponiveis=tipos_disponiveis,
        opcoes_por_pagina=[10, 20, 30, 40, 50],
    )


@ia_local_bp.route("/auditoria/<hw>/<nome_log>/<falha_id>", methods=["GET"])
def detalhe_falha_auditoria(hw, nome_log, falha_id):
    """Detalhe de uma falha na auditoria GPU."""
    hardware = _hardware_valido(hw)
    auditoria, falha = obter_falha_auditoria(hardware, nome_log, falha_id)
    if not auditoria or not falha:
        flash("Falha nao encontrada.", "error")
        return redirect(
            url_for("ia_local.auditoria_relatorio", hw=hardware, nome_log=nome_log)
        )

    return render_template(
        "ia/ia_local_falha_detalhe.html",
        hardware=hardware,
        dados=auditoria["dados"],
        falha=falha,
        nome_log=auditoria["nome_arquivo"],
    )


@ia_local_bp.route("/parecer/<hw>/<arquivo>", methods=["GET"])
def ver_parecer(hw, arquivo):
    """Exibe parecer Markdown."""
    hardware = _hardware_valido(hw)
    from app.web.services.ia_local_service import _pasta_relatorios

    pasta = _pasta_relatorios(hardware)
    caminho = os.path.join(pasta, os.path.basename(arquivo))
    conteudo = ler_parecer_markdown(caminho)
    if conteudo is None:
        flash("Parecer nao encontrado.", "error")
        return redirect(url_for("ia_local.pagina_ia_local", hw=hardware))
    return render_template(
        "ia/ia_local_parecer.html",
        hardware=hardware,
        nome_arquivo=os.path.basename(arquivo),
        conteudo=conteudo,
    )
