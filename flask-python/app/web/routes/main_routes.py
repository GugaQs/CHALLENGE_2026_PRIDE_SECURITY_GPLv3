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

"""Rotas do menu principal."""

import os

from flask import Blueprint, render_template, send_file


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Dashboard principal."""
    return render_template("index.html")


@main_bp.route("/icon.png")
def icon():
    """Icone do projeto."""
    caminho = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "icon.png")
    )
    return send_file(caminho, mimetype="image/png")
