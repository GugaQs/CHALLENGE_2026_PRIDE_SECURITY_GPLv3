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
Módulo de interface para Scan de Projeto usando IA Local.
Roteador para interfaces específicas de Hardware (AMD/NVIDIA).
Refatorado para Clean Code com pacotes dedicados.
"""

from colorama import Fore, Style
from app.utils.helpers import limpar_tela
from app.utils.log_sistema import get_logger
from .executar_scan_ia import testar_conexao_gpu

# Importando dos novos pacotes subdivididos
from .scan_amd.menu import menu_amd_especifico
from .scan_nvidia.menu import menu_nvidia_especifico

_log = get_logger("scan_ia_local")

import subprocess

# Estado global simples para hardware selecionado
hardware_atual = "AMD" # Padrão inicial

def detectar_gpu_automatica():
    """Tenta detectar se há uma GPU NVIDIA presente no sistema."""
    global hardware_atual
    try:
        # Tenta rodar o nvidia-smi para ver se há drivers NVIDIA
        subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        hardware_atual = "NVIDIA"
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        # Se falhar, assume que é AMD ou o padrão configurado
        return False

def menu_ia_local():
    """Menu principal para o scan com IA Local (Roteador)."""
    global hardware_atual
    
    # Tenta detecção automática na primeira execução do menu
    detectar_gpu_automatica()
    
    while True:
        limpar_tela()
        status_gpu = testar_conexao_gpu()
        status_text = Fore.GREEN + f"CONECTADO ({status_gpu[1]})" if status_gpu[0] else Fore.RED + "DESCONECTADO (LM Studio offline)"

        print(Fore.MAGENTA + Style.BRIGHT + "====================================================================================")
        print(Fore.WHITE + "🤖  ASPM - SELETOR DE ACELERAÇÃO IA LOCAL".center(80))
        print(Fore.MAGENTA + "====================================================================================")
        print(Fore.CYAN + f" 🔋 Modo de Hardware: " + (Fore.RED + "🔴 AMD RADEON" if hardware_atual == "AMD" else Fore.GREEN + "🟢 NVIDIA GEFORCE"))
        print(Fore.CYAN + f" 🔌 Status do Servidor: " + status_text)
        print(Fore.MAGENTA + "------------------------------------------------------------------------------------")
        print()
        print(Fore.YELLOW + f"   1 - 🚀 ENTRAR NO PAINEL DE CONTROLE {hardware_atual}")
        print(Fore.YELLOW + "   2 - ⚙️  MUDAR HARDWARE (Alternar Desktop/Notebook)")
        print(Fore.YELLOW + "   3 - 🔌 TESTAR CONEXÃO DO SERVIDOR")
        print()
        print(Fore.RED +    "   0 - ↩️  VOLTAR AO MENU PRINCIPAL")
        print()
        print(Fore.MAGENTA + "====================================================================================")
        
        opcao = input(Fore.CYAN + "👉 Escolha: " + Style.RESET_ALL)

        if opcao == "1":
            if hardware_atual == "AMD":
                menu_amd_especifico()
            else:
                menu_nvidia_especifico()
        elif opcao == "2":
            mudar_hardware()
        elif opcao == "3":
            ok, model = testar_conexao_gpu()
            if ok:
                print(Fore.GREEN + f"\n✅ Sucesso! Conexão ativa com o modelo: {model}")
            else:
                print(Fore.RED + "\n❌ Falha! Verifique se o LM Studio está rodando o servidor local.")
            input(f"\n{Fore.CYAN}↩️ Pressione Enter para continuar...{Style.RESET_ALL}")
        elif opcao == "0":
            break

def mudar_hardware():
    """Submenu para alternar o hardware alvo."""
    global hardware_atual
    limpar_tela()
    print(Fore.MAGENTA + "====================================================================================")
    print(Fore.WHITE + "⚙️  ALTERAR CONFIGURAÇÃO DE HARDWARE".center(80))
    print(Fore.MAGENTA + "====================================================================================")
    print()
    print(Fore.RED + "   1 - 🔴 AMD Radeon RX 7800 (Desktop Mode)")
    print(Fore.GREEN + "   2 - 🟢 NVIDIA GeForce RTX (Notebook Mode)")
    print()
    
    escolha = input(Fore.CYAN + "👉 Selecione o modo: " + Style.RESET_ALL)
    if escolha == "1":
        hardware_atual = "AMD"
    elif escolha == "2":
        hardware_atual = "NVIDIA"
    
    print(Fore.GREEN + f"\n✅ Ambiente configurado para {hardware_atual}!")
    input(f"\n{Fore.CYAN}↩️ Pressione Enter para voltar...{Style.RESET_ALL}")
