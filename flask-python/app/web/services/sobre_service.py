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

"""Servicos para pagina Sobre — dados estaticos em funcoes puras."""


def obter_dados_sobre():
    """Retorna dados institucionais do projeto."""
    return {
        "titulo": "ASPM - Pride Security - Challenge FIAP 2026",
        "descricao": (
            "Ferramenta modular de Cyber Defense: scan por assinaturas, "
            "IA local (AMD/NVIDIA + LM Studio) e interface web Flask."
        ),
        "repositorio": "https://github.com/carmipa/CHALLENGE_2026_PRIDE_SECURITY",
        "integrantes": [
            {"nome": "Paulo Andre Carminati", "rm": "RM570877"},
            {"nome": "Gustav Quental Scorsi", "rm": "RM569862"},
            {"nome": "Andre Archanjo dos Santos Torres", "rm": "RM570458"},
            {"nome": "Luiz Carlos da Paixao dos Santos", "rm": "RM573009"},
            {"nome": "Victor Henrique de Barros Oliveira", "rm": "RM570012"},
        ],
    }
