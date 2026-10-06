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

"""Tela de apresentacao institucional do projeto e equipe."""

from colorama import Fore, Style
from app.utils.helpers import limpar_tela
from app.utils.log_sistema import get_logger

_log = get_logger("sobre")


def mostrar_sobre():
    """
    Exibe dados da equipe, repositorio e opcoes de navegacao.
    """
    limpar_tela()
    
    print(Fore.BLUE + "=" * 80)
    print(Fore.CYAN + " " * 25 + "ℹ️  SOBRE O PROJETO")
    print(Fore.BLUE + "=" * 80 + "\n")
    
    print(Fore.WHITE + "🛡️  " + Fore.YELLOW + "ASPM - PRIDE SECURITY - CHALLENGE FIAP 2026")
    print(Fore.WHITE + "Uma ferramenta modular CLI de Cyber Defense e Posture Management.\n")
    print(Fore.CYAN + "📁 Repositório Oficial no GitHub:")
    print(Fore.WHITE + "https://github.com/carmipa/CHALLENGE_2026_PRIDE_SECURITY\n")
    
    print(Fore.BLUE + "-" * 80)
    print(Fore.CYAN + "🎓 Turma 1TDCPV - Integrantes da Equipe:")
    print(Fore.BLUE + "-" * 80)
    
    equipe = [
        ("Paulo André Carminati", "RM570877"),
        ("Gustav Quental Scorsi", "RM569862"), # Conforme escrito na imagem
        ("André Archanjo dos Santos torres", "RM570458"),
        ("Luiz Carlos da Paixão dos Santos", "RM573009"),
        ("Victor Henrique de Barros Oliveira", "RM570012")
    ]
    
    for nome, rm in equipe:
        print(f"{Fore.YELLOW}• {Fore.WHITE}{nome:<40} {Fore.CYAN}[{rm}]")
    
    print(Fore.BLUE + "\n" + "=" * 80)
    
    while True:
        prompt = (f"\n{Fore.CYAN}Opções:\n"
                  f"{Fore.YELLOW}[R]{Style.RESET_ALL} Abrir a documentação detalhada (README.md)\n"
                  f"{Fore.RED}[0]{Style.RESET_ALL} Voltar ao Menu Principal\n"
                  f"{Fore.CYAN}👉 Digite sua escolha: {Style.RESET_ALL}")
        
        opcao = input(prompt).strip().lower()
        
        if opcao == '0':
            break
        elif opcao == 'r':
            import os
            import subprocess
            
            base_dir = os.path.dirname(__file__)
            # Procura pelo README em "../../../" (api_python) e "../../../../" (Challenge folder)
            caminhos_tentativas = [
                os.path.abspath(os.path.join(base_dir, "..", "..", "..", "readme.md")),
                os.path.abspath(os.path.join(base_dir, "..", "..", "..", "README.md")),
                os.path.abspath(os.path.join(base_dir, "..", "..", "..", "..", "readme.md")),
                os.path.abspath(os.path.join(base_dir, "..", "..", "..", "..", "README.md"))
            ]
            
            caminho_readme = None
            for c in caminhos_tentativas:
                if os.path.exists(c):
                    caminho_readme = c
                    break
                    
            if caminho_readme:
                print(Fore.YELLOW + f"🚀 Lançando leitor do sistema para: {os.path.basename(caminho_readme)}..." + Style.RESET_ALL)
                try:
                    if os.name == 'nt':
                        os.startfile(caminho_readme)
                    else:
                        subprocess.run(['xdg-open', caminho_readme], check=False)
                except Exception as e:
                    _log.exception("Falha ao abrir README no sistema.")
                    print(Fore.RED + f"❌ Erro ao abrir README: {e}" + Style.RESET_ALL)
            else:
                print(Fore.RED + "⚠️ Arquivo README.md não encontrado na raiz do projeto." + Style.RESET_ALL)
        else:
            print(Fore.RED + "⚠️ Opção inválida!" + Style.RESET_ALL)
