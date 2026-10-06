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

"""Funcoes utilitarias compartilhadas da aplicacao."""

import os

from app.utils.log_sistema import get_logger


def limpar_tela():
    """
    Limpa o terminal de acordo com o sistema operacional (Windows/Linux/Mac).
    """
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except OSError as e:
        get_logger("helpers").warning("limpar_tela: comando do SO falhou: %s", e)
