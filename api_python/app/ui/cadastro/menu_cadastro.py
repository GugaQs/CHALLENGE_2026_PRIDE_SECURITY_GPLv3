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

"""Menu interativo do modulo de cadastro."""

from colorama import init, Fore, Style
import os
import sys

# Garante que os imports relativos funcionem se rodar isolado ou pela main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Tenta importar as funções de create e list
try:
    from app.ui.cadastro.create import add_usuario
    from app.ui.cadastro.list import listar_usuarios
except ImportError:
    # Caso rode direto na pasta (uso legado)
    from app.ui.cadastro.create import add_usuario
    from app.ui.cadastro.list import listar_usuarios

from app.utils.helpers import limpar_tela
from app.utils.tempo import obter_relogio_atual
from app.utils.log_sistema import get_logger

init(autoreset=True)

_log = get_logger("cadastro_menu")


def cadastro_menu():
    """Renderiza menu de cadastro e roteia as opcoes da area."""
    _log.info("Menu cadastro exibido")
    while True:
        try:
            limpar_tela()
            relogio = obter_relogio_atual()
            menu_text = f"""
    {relogio.center(60)}
    {Fore.YELLOW}    📝  CADASTRO DE USUÁRIO{Style.RESET_ALL}

    {Fore.YELLOW}1 - ➕  NOVO CADASTRO{Style.RESET_ALL}
    {Fore.YELLOW}2 - 📋  LISTAR USUÁRIOS CADASTRADOS{Style.RESET_ALL}
    {Fore.YELLOW}3 - ✏️  ATUALIZAR DADOS CADASTRAIS{Style.RESET_ALL}

    {Fore.RED}0 - 🔙 VOLTAR AO MENU PRINCIPAL{Style.RESET_ALL}
        """
            print(menu_text)

            opcao = input(Fore.CYAN + "Escolha uma opção no Cadastro: " + Style.RESET_ALL)

            if opcao == "1":
                _log.info("Cadastro: novo usuario (formulario)")
                add_usuario()
                input(f"\n{Fore.CYAN} ↩️  Pressione Enter para voltar ao menu...{Style.RESET_ALL}")
            elif opcao == "2":
                _log.info("Cadastro: listar usuarios")
                listar_usuarios()
                input(f"\n{Fore.CYAN} ↩️  Pressione Enter para voltar ao menu...{Style.RESET_ALL}")
            elif opcao == "3":
                _log.info("Cadastro: atualizar dados (nao implementado)")
                print(Fore.YELLOW + "⚠️  Funcionalidade de atualização em desenvolvimento.")
                input(f"\n{Fore.CYAN} ↩️  Pressione Enter para voltar ao menu...{Style.RESET_ALL}")
            elif opcao == "0":
                _log.info("Cadastro: voltar ao menu principal")
                break
            else:
                _log.warning("Cadastro: opcao invalida (%r)", opcao)
                print(Fore.RED + "⚠️ Opção inválida! Tente novamente.")
        except KeyboardInterrupt:
            raise
        except Exception:
            _log.exception("Erro no loop do menu de cadastro.")
            print(Fore.RED + "❌ Erro registrado no log do sistema. Pressione Enter...")
            input(f"\n{Fore.CYAN} ↩️  Enter...{Style.RESET_ALL}")

if __name__ == "__main__":
    cadastro_menu()
