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

"""
Módulo de interface para Scan de Projeto usando IA via API (OpenAI, Anthropic, Gemini).
"""

from colorama import Fore, Style
from app.utils.helpers import limpar_tela
from app.utils.log_sistema import get_logger

_log = get_logger("scan_ia_api")

def menu_ia_api():
    """Menu principal para o scan com IA via API."""
    while True:
        limpar_tela()
        print(Fore.BLUE + Style.BRIGHT + "====================================================================================")
        print(Fore.WHITE + "☁️  SCAN DE PROJETO - INTELIGÊNCIA ARTIFICIAL VIA API".center(80))
        print(Fore.BLUE + "====================================================================================")
        print()
        print(Fore.YELLOW + "   1 - 🔑 CONFIGURAR API KEY")
        print(Fore.YELLOW + "   2 - 🤖 SELECIONAR PROVEDOR (GPT-4 / Claude 3 / Gemini Pro)")
        print(Fore.YELLOW + "   3 - 🚀 INICIAR VARREDURA REMOTA")
        print()
        print(Fore.RED +    "   0 - ↩️  VOLTAR AO MENU PRINCIPAL")
        print()
        print(Fore.BLUE + "====================================================================================")
        
        opcao = input(Fore.CYAN + "👉  Escolha uma opção: " + Style.RESET_ALL)

        if opcao == "0":
            break
        else:
            print(Fore.YELLOW + "\n🚧 Módulo de IA via API em desenvolvimento...")
            input(f"\n{Fore.CYAN}↩️  Pressione Enter para continuar...{Style.RESET_ALL}")
