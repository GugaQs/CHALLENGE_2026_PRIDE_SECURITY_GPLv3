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

"""Menu CLI para scan de software instalado."""

from colorama import Fore, Style

from app.utils.helpers import limpar_tela
from app.utils.log_sistema import get_logger

from .listar_software import listar_software_instalado_resumo

_log = get_logger("scan_software")


def menu_scan_software():
    """Menu do modulo scan de software."""
    while True:
        limpar_tela()
        print(Fore.BLUE + Style.BRIGHT + "=" * 84)
        print(Fore.WHITE + "🔍  SCAN DE SOFTWARE INSTALADO".center(84))
        print(Fore.BLUE + "=" * 84)
        print()
        print(Fore.YELLOW + "   1 - 📋  LISTAR SOFTWARE (resumo do sistema)")
        print(Fore.YELLOW + "   2 - 🚀  VARREDURA COMPLETA (em desenvolvimento)")
        print()
        print(Fore.RED + "   0 - ↩️  VOLTAR")
        print()

        opcao = input(Fore.CYAN + "Escolha uma opcao: " + Style.RESET_ALL).strip()

        if opcao == "0":
            break
        if opcao == "1":
            listar_software_instalado_resumo()
            input(f"\n{Fore.CYAN}Enter para continuar...{Style.RESET_ALL}")
            continue

        _log.info("Scan software: opcao %r (em desenvolvimento)", opcao)
        print(Fore.YELLOW + "\n🚧 Varredura completa em desenvolvimento...")
        input(f"\n{Fore.CYAN}Enter para continuar...{Style.RESET_ALL}")
