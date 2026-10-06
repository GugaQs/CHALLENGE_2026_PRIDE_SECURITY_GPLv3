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

"""Renderizacao do menu principal da aplicacao CLI."""

from colorama import init, Fore, Style

init(autoreset=True)

def menu(relogio=""):
    """Exibe o menu principal no terminal.

    Args:
        relogio: Texto formatado do relogio UTC para cabecalho do menu.
    """
    if relogio:
        print(relogio.center(64))
    print()
    print(Fore.CYAN + Style.BRIGHT + """🛡️  ASPM - PRIDE SECURITY - CHALLENGE - FIAP - 2026 - CYBER SEGURANÇA  🛡️""")
    print()
    print(Fore.BLUE + "====================================================================================")
    print()
    print(Fore.YELLOW + "   1 - 🔍  SCAN DE SOFTWARE")
    print(Fore.YELLOW + "   2 - 📂  SCAN DE PROJETO")
    print(Fore.YELLOW + "   3 - 📂  SCAN DE PROJETO - IA LOCAL")
    print(Fore.YELLOW + "   4 - 📂  SCAN DE PROJETO - IA API")
    print(Fore.YELLOW + "   5 - 📜  LOG DE SISTEMA")
    print(Fore.YELLOW + "   6 - 🐳  SCAN DE CONTAINERS")
    print(Fore.YELLOW + "   7 - ℹ️   SOBRE O PROJETO")
    print()
    print(Fore.RED +    "   0 - ❌  SAIR")
    print()
    print(Fore.BLUE + "====================================================================================")
