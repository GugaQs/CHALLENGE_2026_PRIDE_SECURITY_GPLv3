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

"""Menu CLI para scan de containers Docker (Dockerfile, compose, imagens)."""

from colorama import Fore, Style

from app.utils.helpers import limpar_tela
from app.utils.log_sistema import get_logger

_log = get_logger("scan_containers")


def menu_scan_containers():
    """Menu do modulo de scan de containers."""
    while True:
        limpar_tela()
        print(
            Fore.BLUE
            + Style.BRIGHT
            + "===================================================================================="
        )
        print(
            Fore.WHITE + "🐳  SCAN DE CONTAINERS DOCKER".center(80)
        )
        print(
            Fore.BLUE
            + "===================================================================================="
        )
        print()
        print(Fore.YELLOW + "   1 - 🔍  ESCANEAR PROJETO (Dockerfile / compose)")
        print(Fore.YELLOW + "   2 - 📋  RELATORIOS")
        print()
        print(Fore.RED + "   0 - ↩️  VOLTAR AO MENU PRINCIPAL")
        print()
        print(
            Fore.BLUE
            + "===================================================================================="
        )

        opcao = input(Fore.CYAN + "👉  Escolha uma opção: " + Style.RESET_ALL)

        if opcao == "0":
            break

        _log.info("Scan containers: opcao %r selecionada (em desenvolvimento)", opcao)
        print(Fore.YELLOW + "\n🚧 Módulo de Scan de Containers em desenvolvimento...")
        input(f"\n{Fore.CYAN}↩️  Pressione Enter para continuar...{Style.RESET_ALL}")
