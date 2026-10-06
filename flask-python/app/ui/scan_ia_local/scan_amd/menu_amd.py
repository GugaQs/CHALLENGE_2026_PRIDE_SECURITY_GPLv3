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
Interface legada — use `menu.py` (importado por `menu_ia_local`).
Mantido para referência; o fluxo ativo é `scan_amd/menu.py`.
"""

from colorama import Fore, Style
from app.utils.helpers import limpar_tela
from ..executar_scan_ia import testar_conexao_gpu, analisar_relatorio_existente
from app.ui.scan_projeto.executar_scan import rodar_engine_scan
import os

def menu_amd_especifico():
    while True:
        limpar_tela()
        ok, model = testar_conexao_gpu()
        status = Fore.GREEN + f"ATIVO ({model})" if ok else Fore.RED + "OFFLINE"
        
        print(Fore.RED + Style.BRIGHT + "====================================================================================")
        print(Fore.WHITE + "🔴  ASPM IA - RADEON ACCELERATED SCAN (AMD ROCm/DirectML)".center(80))
        print(Fore.RED + "====================================================================================")
        print(f" {Fore.RED}GPU: {Fore.WHITE}AMD Radeon RX 7800 Series  |  {Fore.RED}Status: {status}")
        print(Fore.RED + "------------------------------------------------------------------------------------")
        print()
        print(Fore.WHITE + "   1 - 📂  SCAN DE PROJETO (Assinaturas - Otimizado AMD)")
        print(Fore.WHITE + "   2 - 🚀  SCAN COGNITIVO IA (Análise Profunda)")
        print(Fore.WHITE + "   3 - 📊  RE-ANALISAR ÚLTIMO RELATÓRIO COM GEMMA")
        print(Fore.WHITE + "   4 - 🧪  BENCHMARK RADEON")
        print()
        print(Fore.RED +    "   0 - ↩️  VOLTAR")
        print()
        print(Fore.RED + "====================================================================================")
        
        opcao = input(Fore.RED + "👉 Escolha (Radeon Mode): " + Style.RESET_ALL)
        
        if opcao == "1":
            print(Fore.RED + "\n--- [ INICIANDO SCAN DE ASSINATURAS (MODO AMD) ] ---")
            caminho = input(Fore.WHITE + "📂 Digite o caminho do projeto: " + Style.RESET_ALL)
            if os.path.exists(caminho):
                rodar_engine_scan(caminho)
            else:
                print(Fore.RED + "\n⚠️ Caminho inválido.")
            input(f"\n{Fore.RED}↩️ Pressione Enter para continuar...{Style.RESET_ALL}")
            
        elif opcao == "2":
            print(Fore.YELLOW + "\n🚧 Scan Cognitivo IA (Análise direta de arquivos) em desenvolvimento.")
            input(f"\n{Fore.RED}↩️ Pressione Enter...{Style.RESET_ALL}")

        elif opcao == "3":
            pasta_logs = "app/ui/scan_projeto/logs"
            if os.path.exists(pasta_logs):
                arquivos = [f for f in os.listdir(pasta_logs) if f.endswith(".json")]
                if arquivos:
                    ultimo_log = os.path.join(pasta_logs, sorted(arquivos)[-1])
                    print(Fore.CYAN + f"\n📄 Analisando último relatório: {ultimo_log}")
                    texto, _md, _txt = analisar_relatorio_existente(ultimo_log)
                    print(Fore.WHITE + "\n--- [ PARECER DA IA NA GPU AMD ] ---")
                    print(texto)
                else:
                    print(Fore.RED + "\n⚠️ Nenhum relatório encontrado.")
            input(f"\n{Fore.RED}↩️ Pressione Enter...{Style.RESET_ALL}")
            
        elif opcao == "0":
            break
