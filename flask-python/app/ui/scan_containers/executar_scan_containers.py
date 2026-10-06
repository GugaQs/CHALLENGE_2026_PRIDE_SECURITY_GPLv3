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

"""Funcoes de scan de containers Docker (estrutura inicial)."""

import os

from app.utils.log_sistema import get_logger
from app.utils.progresso_scan import notificar_progresso

_log = get_logger("scan_containers")

NOMES_ALVO = (
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
)


def _contar_arquivos_pasta(caminho_projeto, ignorados):
    """Conta arquivos para calcular progresso da varredura."""
    total = 0
    for raiz, pastas, arquivos in os.walk(caminho_projeto):
        pastas[:] = [p for p in pastas if p not in ignorados]
        total += len(arquivos)
    return total


def listar_artefatos_docker(caminho_projeto, progress_callback=None):
    """Lista Dockerfiles e compose encontrados no projeto."""
    caminho_projeto = os.path.abspath(caminho_projeto or "")
    if not os.path.isdir(caminho_projeto):
        return []

    ignorados = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    encontrados = []
    total_arquivos = _contar_arquivos_pasta(caminho_projeto, ignorados)
    processados = 0

    notificar_progresso(
        progress_callback,
        0,
        max(total_arquivos, 1),
        "Buscando artefatos Docker...",
    )

    for raiz, pastas, arquivos in os.walk(caminho_projeto):
        pastas[:] = [p for p in pastas if p not in ignorados]
        for nome in arquivos:
            processados += 1
            if nome in NOMES_ALVO:
                encontrados.append(
                    {
                        "nome": nome,
                        "caminho": os.path.join(raiz, nome),
                        "caminho_relativo": os.path.relpath(
                            os.path.join(raiz, nome), caminho_projeto
                        ),
                    }
                )
            if processados % 25 == 0 or processados == total_arquivos:
                notificar_progresso(
                    progress_callback,
                    processados,
                    max(total_arquivos, 1),
                )

    encontrados.sort(key=lambda item: item["caminho_relativo"])
    return encontrados


def executar_scan_containers(caminho_projeto, progress_callback=None):
    """
    Executa varredura inicial de artefatos Docker.
    Retorna lista de arquivos e mensagem de status.
    """
    caminho_projeto = (caminho_projeto or "").strip()
    if not caminho_projeto:
        return False, "Informe o caminho do projeto.", []

    if not os.path.isdir(caminho_projeto):
        return False, "Caminho invalido ou inexistente.", []

    artefatos = listar_artefatos_docker(caminho_projeto, progress_callback)
    _log.info(
        "Scan containers: %s artefato(s) em %s",
        len(artefatos),
        caminho_projeto,
    )

    if not artefatos:
        return (
            True,
            "Nenhum Dockerfile ou docker-compose encontrado neste caminho.",
            [],
        )

    return (
        True,
        f"Encontrados {len(artefatos)} artefato(s) Docker. Analise profunda em desenvolvimento.",
        artefatos,
    )
