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
Mantido para referência; o fluxo ativo é `scan_nvidia/menu.py`.
"""

from colorama import Fore, Style
from app.utils.helpers import limpar_tela
from ..executar_scan_ia import testar_conexao_gpu, analisar_relatorio_existente
from app.ui.scan_projeto.executar_scan import rodar_engine_scan
import os

def menu_nvidia_especifico():
    while True:
        limpar_tela()
        ok, model = testar_conexao_gpu()
        status = Fore.GREEN + f"ONLINE ({model})" if ok else Fore.RED + "OFFLINE"

        print(Fore.GREEN + Style.BRIGHT + "====================================================================================")
        print(Fore.WHITE + "🟢  ASPM IA - GEFORCE CUDA ACCELERATED (NVIDIA)".center(80))
        print(Fore.GREEN + "====================================================================================")
        print(f" {Fore.GREEN}GPU: {Fore.WHITE}NVIDIA GeForce RTX Series  |  {Fore.GREEN}Status: {status}")
        print(Fore.GREEN + "------------------------------------------------------------------------------------")
        print()
        print(Fore.WHITE + "   1 - 📂  SCAN DE PROJETO (Assinaturas - MODO CUDA)")
        print(Fore.WHITE + "   2 - ⚡  SCAN COGNITIVO IA (Análise via Tensor Cores)")
        print(Fore.WHITE + "   3 - 🧠  VALIDAÇÃO TÉCNICA VIA IA (Re-análise)")
        print(Fore.WHITE + "   4 - 🛠️   CONFIGURAR TENSORRT")
        print()
        print(Fore.GREEN + "   0 - ↩️  VOLTAR")
        print()
        print(Fore.GREEN + "====================================================================================")
        
        opcao = input(Fore.GREEN + "👉 Escolha (GeForce Mode): " + Style.RESET_ALL)
        
        if opcao == "1":
            print(Fore.GREEN + "\n--- [ INICIANDO SCAN DE ASSINATURAS (MODO NVIDIA) ] ---")
            caminho = input(Fore.WHITE + "📂 Digite o caminho do projeto: " + Style.RESET_ALL)
            if os.path.exists(caminho):
                rodar_engine_scan(caminho)
            else:
                print(Fore.RED + "\n⚠️ Caminho inválido.")
            input(f"\n{Fore.GREEN}↩️ Pressione Enter para continuar...{Style.RESET_ALL}")

        elif opcao == "3":
            pasta_logs = "app/ui/scan_projeto/logs"
            if os.path.exists(pasta_logs):
                arquivos = [f for f in os.listdir(pasta_logs) if f.endswith(".json")]
                if arquivos:
                    ultimo_log = os.path.join(pasta_logs, sorted(arquivos)[-1])
                    print(Fore.CYAN + f"\n📄 Analisando: {ultimo_log}")
                    texto, _md, _txt = analisar_relatorio_existente(ultimo_log)
                    print(Fore.WHITE + "\n--- [ PARECER DA IA NA GPU NVIDIA ] ---")
                    print(texto)
                else:
                    print(Fore.RED + "\n⚠️ Nenhum relatório encontrado.")
            input(f"\n{Fore.GREEN}↩️ Pressione Enter...{Style.RESET_ALL}")

        elif opcao == "0":
            break
