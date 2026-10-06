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

"""Utilitarios de progresso para motores de scan (CLI e web)."""


def calcular_percentual(atual, total):
    """Calcula percentual inteiro de 0 a 100."""
    if not total or total <= 0:
        return 0
    return min(100, int((atual / total) * 100))


def notificar_progresso(callback, atual, total, mensagem=None):
    """Invoca callback de progresso no formato esperado pela web."""
    if not callback:
        return
    callback(
        {
            "status": "em_andamento",
            "mensagem": mensagem or f"Escaneando arquivos ({atual}/{total})...",
            "percentual": calcular_percentual(atual, total),
            "atual": atual,
            "total": total,
        }
    )
