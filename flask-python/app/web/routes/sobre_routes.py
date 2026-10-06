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

"""Rotas da pagina Sobre."""

from flask import Blueprint, render_template

from app.web.services.sobre_service import obter_dados_sobre


sobre_bp = Blueprint("sobre", __name__, url_prefix="/sobre")


@sobre_bp.route("/", methods=["GET"])
def pagina_sobre():
    """Informacoes institucionais."""
    return render_template("sobre/sobre.html", dados=obter_dados_sobre())
