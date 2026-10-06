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

"""Rotas web para log de sistema central."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.ui.log_sistema.menu_log_sistema import LOG_ERRO_PADRAO
from app.web.services.log_sistema_service import (
    abrir_pasta_logs_explorador,
    classificar_linhas_log,
    ler_arquivo_log,
    ler_erro_sistema,
    ler_log_amd_sistema,
    ler_log_nvidia_sistema,
    listar_arquivos_log,
    listar_relatorios_generic,
)


log_bp = Blueprint("logs", __name__, url_prefix="/logs")


@log_bp.route("/", methods=["GET"])
def pagina_logs_sistema():
    """Lista arquivos e atalhos rapidos do menu CLI."""
    pasta_base, arquivos = listar_arquivos_log()
    por_pagina = 15
    pagina = max(1, request.args.get("pagina", default=1, type=int) or 1)
    total = len(arquivos)
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    pagina = min(pagina, total_paginas)
    inicio = (pagina - 1) * por_pagina
    arquivos_pagina = arquivos[inicio:inicio + por_pagina]
    return render_template(
        "log/logs_sistema.html",
        pasta_base=pasta_base,
        arquivos=arquivos_pagina,
        relatorios_generic=listar_relatorios_generic(),
        log_erro_padrao=LOG_ERRO_PADRAO,
        pagina=pagina,
        total_paginas=total_paginas,
        total_arquivos=total,
    )


def _renderizar_log(nome_log, conteudo, voltar_url):
    """Helper: classifica linhas e renderiza template de log colorido."""
    return render_template(
        "log/log_sistema_detalhe.html",
        nome_log=nome_log,
        linhas_log=classificar_linhas_log(conteudo),
        voltar_url=voltar_url,
    )


@log_bp.route("/ver/<path:caminho_relativo>", methods=["GET"])
def ver_log(caminho_relativo):
    """Visualiza conteudo de log."""
    limite = request.args.get("linhas", type=int) or 400
    conteudo = ler_arquivo_log(caminho_relativo, limite=limite)
    if conteudo is None:
        flash("Arquivo de log nao encontrado.", "error")
        return redirect(url_for("logs.pagina_logs_sistema"))
    return _renderizar_log(caminho_relativo, conteudo, url_for("logs.pagina_logs_sistema"))


@log_bp.route("/atalho/erro-sistema", methods=["GET"])
def atalho_erro_sistema():
    """Ultimas linhas de erro_sistema.log."""
    linhas = request.args.get("linhas", default=80, type=int)
    conteudo = ler_erro_sistema(linhas)
    if conteudo is None:
        flash(f"{LOG_ERRO_PADRAO} ainda nao existe ou esta vazio.", "error")
        return redirect(url_for("logs.pagina_logs_sistema"))
    return _renderizar_log(LOG_ERRO_PADRAO, conteudo, url_for("logs.pagina_logs_sistema"))


@log_bp.route("/atalho/amd-sistema", methods=["GET"])
def atalho_amd_sistema():
    """Log de sistema AMD."""
    linhas = request.args.get("linhas", default=100, type=int)
    conteudo = ler_log_amd_sistema(linhas)
    if conteudo is None:
        flash("Log de sistema AMD ainda nao gerado.", "error")
        return redirect(url_for("logs.pagina_logs_sistema"))
    return _renderizar_log(
        "amd/system/sistema_amd.log", conteudo, url_for("logs.pagina_logs_sistema")
    )


@log_bp.route("/atalho/nvidia-sistema", methods=["GET"])
def atalho_nvidia_sistema():
    """Log de sistema NVIDIA."""
    linhas = request.args.get("linhas", default=100, type=int)
    conteudo = ler_log_nvidia_sistema(linhas)
    if conteudo is None:
        flash("Log de sistema NVIDIA ainda nao gerado.", "error")
        return redirect(url_for("logs.pagina_logs_sistema"))
    return _renderizar_log(
        "nvidia/system/sistema_nvidia.log", conteudo, url_for("logs.pagina_logs_sistema")
    )


@log_bp.route("/abrir-pasta", methods=["POST"])
def abrir_pasta_logs():
    """Abre pasta logs/ no explorador."""
    ok, mensagem = abrir_pasta_logs_explorador()
    flash(mensagem, "success" if ok else "error")
    return redirect(url_for("logs.pagina_logs_sistema"))
