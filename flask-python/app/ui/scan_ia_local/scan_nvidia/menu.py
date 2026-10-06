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
Interface dedicada para hardware NVIDIA GeForce.
Versão Final: Multi-relatórios e Impressão.
"""

from colorama import Fore, Style
import os
import subprocess
from app.utils.helpers import limpar_tela
from ..executar_scan_ia import testar_conexao_gpu, analisar_relatorio_existente, imprimir_relatorio
from .executar_scan import rodar_engine_scan_nvidia
from .listar_falhas import navegar_falhas_nvidia, apresentar_tabela_logs_nvidia

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
        print(Fore.WHITE + "   1 - 📂  INICIAR SCAN DE PROJETO")
        print(Fore.WHITE + "   2 - 📋  LISTAR FALHAS / AUDITORIA")
        print(Fore.WHITE + "   3 - 🚀  SCAN COGNITIVO IA (Parecer Completo)")
        print(Fore.WHITE + "   4 - 🧠  RE-ANALISAR ÚLTIMO RELATÓRIO")
        print(Fore.WHITE + "   5 - 🖨️   IMPRIMIR ÚLTIMO PARECER TÉCNICO")
        print()
        print(Fore.GREEN + "   0 - ↩️  VOLTAR")
        print()
        print(Fore.GREEN + "====================================================================================")
        
        opcao = input(Fore.GREEN + "👉 Escolha (GeForce Mode): " + Style.RESET_ALL)
        
        if opcao == "1":
            caminho = input(Fore.WHITE + "\n📂 Caminho do projeto: " + Style.RESET_ALL)
            if os.path.exists(caminho):
                rodar_engine_scan_nvidia(caminho)
            else:
                print(Fore.RED + "\n⚠️ Caminho inválido.")
            input(f"\n{Fore.GREEN}↩️ Pressione Enter...{Style.RESET_ALL}")

        elif opcao == "2":
            log_selecionado = apresentar_tabela_logs_nvidia()
            if log_selecionado:
                navegar_falhas_nvidia(log_selecionado)
            input(f"\n{Fore.GREEN}↩️ Pressione Enter...{Style.RESET_ALL}")

        elif opcao == "3" or opcao == "4":
            log_json = ""
            if opcao == "3":
                caminho = input(Fore.WHITE + "\n📂 Caminho para SCAN COGNITIVO: " + Style.RESET_ALL)
                if os.path.exists(caminho):
                    log_json = rodar_engine_scan_nvidia(caminho)
                else:
                    print(Fore.RED + "\n⚠️ Caminho inválido."); continue
            else:
                base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
                pasta_logs = os.path.join(base, "logs", "nvidia", "reports")
                if not os.path.isdir(pasta_logs):
                    print(Fore.RED + "\n⚠️ Pasta de logs ainda não existe.")
                    input(f"\n{Fore.GREEN}↩️ Pressione Enter...{Style.RESET_ALL}")
                    continue
                arquivos = [f for f in os.listdir(pasta_logs) if f.endswith(".json")]
                if arquivos:
                    log_json = os.path.join(pasta_logs, sorted(arquivos)[-1])
                else:
                    print(Fore.RED + "\n⚠️ Nenhum log encontrado.")
                    input(f"\n{Fore.GREEN}↩️ Pressione Enter...{Style.RESET_ALL}")
                    continue

            terminal_text, md_path, txt_path = analisar_relatorio_existente(log_json)
            print(Fore.WHITE + "\n--- [ PARECER TÉCNICO IA ] ---")
            print(terminal_text)
            if md_path and txt_path:
                print(
                    Fore.YELLOW
                    + f"\n📄 Arquivos gerados:\n   - {os.path.basename(md_path)}\n   - {os.path.basename(txt_path)}"
                )
                sub = input(
                    Fore.CYAN
                    + "\nDeseja [A]brir Premium, [T]xt simples, [I]mprimir ou [S]air? "
                ).lower()
                if sub == "a" and os.name == "nt":
                    os.startfile(md_path)
                elif sub == "a":
                    subprocess.run(["xdg-open", md_path], check=False)
                elif sub == "t" and os.name == "nt":
                    os.startfile(txt_path)
                elif sub == "t":
                    subprocess.run(["xdg-open", txt_path], check=False)
                elif sub == "i":
                    imprimir_relatorio(txt_path)
            else:
                print(
                    Fore.YELLOW
                    + "\nℹ️ Nenhum ficheiro .md/.txt gerado (sem achados ou IA indisponível)."
                )
            
            input(f"\n{Fore.GREEN}↩️ Pressione Enter...{Style.RESET_ALL}")

        elif opcao == "5":
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            pasta_logs = os.path.join(base, "logs", "nvidia", "reports")
            if not os.path.isdir(pasta_logs):
                print(Fore.RED + "\n⚠️ Pasta de relatórios NVIDIA ainda não existe.")
                input(f"\n{Fore.GREEN}↩️ Pressione Enter...{Style.RESET_ALL}")
                continue
            arquivos = [f for f in os.listdir(pasta_logs) if f.endswith("_AI_LEITURA.txt")]
            if arquivos:
                imprimir_relatorio(os.path.join(pasta_logs, sorted(arquivos)[-1]))
            else:
                print(Fore.RED + "\n⚠️ Nenhum relatório pronto para impressão.")
            input(f"\n{Fore.GREEN}↩️ Pressione Enter...{Style.RESET_ALL}")

        elif opcao == "0":
            break
