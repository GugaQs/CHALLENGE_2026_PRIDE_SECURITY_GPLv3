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

"""Listagem resumida de software instalado (Windows)."""

import os
import subprocess

from colorama import Fore, Style

from app.utils.log_sistema import get_logger

_log = get_logger("scan_software_listar")


def _listar_via_powershell():
    """Obtem nomes de programas instalados via PowerShell."""
    comando = (
        "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, "
        "HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* "
        "| Where-Object { $_.DisplayName } "
        "| Select-Object -ExpandProperty DisplayName"
    )
    try:
        retorno = subprocess.run(
            ["powershell", "-NoProfile", "-Command", comando],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as erro:
        _log.warning("Falha ao listar software: %s", erro)
        return []

    if retorno.returncode != 0:
        return []

    nomes = []
    for linha in (retorno.stdout or "").splitlines():
        nome = linha.strip()
        if nome:
            nomes.append(nome)
    return sorted(set(nomes))


def listar_software_instalado(limite=50):
    """Retorna lista de software instalado (ate limite)."""
    if os.name != "nt":
        return [], "Listagem disponivel apenas no Windows."

    nomes = _listar_via_powershell()
    if not nomes:
        return [], "Nenhum software listado ou comando indisponivel."

    total = len(nomes)
    if limite and total > limite:
        return nomes[:limite], f"Exibindo {limite} de {total} programas."
    return nomes, f"Total: {total} programas."


def listar_software_instalado_resumo():
    """Imprime resumo no terminal (CLI)."""
    nomes, mensagem = listar_software_instalado(limite=30)
    print(Fore.CYAN + mensagem + Style.RESET_ALL)
    if not nomes:
        print(Fore.YELLOW + "Sem dados para exibir." + Style.RESET_ALL)
        return
    for i, nome in enumerate(nomes, 1):
        print(f"{Fore.YELLOW}{i:>3}{Style.RESET_ALL} - {nome}")
