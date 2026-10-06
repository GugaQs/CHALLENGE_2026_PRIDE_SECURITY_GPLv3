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

"""Menu CLI para consultar arquivos em logs/ (erros e demais .log)."""

from __future__ import annotations

import os
import subprocess

from colorama import Fore, Style

from app.utils.helpers import limpar_tela
from app.utils.tempo import obter_relogio_atual
from app.utils.log_sistema import get_logger

LOG_ERRO_PADRAO = "erro_sistema.log"

_log = get_logger("menu_log_sistema")


def obter_diretorio_logs():
    """Pasta `logs` na raiz do projeto (mesma usada em main.py)."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs"))


def _listar_arquivos_log():
    pasta_base = obter_diretorio_logs()
    if not os.path.isdir(pasta_base):
        return pasta_base, []
    
    arquivos_encontrados = []
    # Lista arquivos na raiz de logs/
    for f in os.listdir(pasta_base):
        if f.lower().endswith(".log") and os.path.isfile(os.path.join(pasta_base, f)):
            arquivos_encontrados.append(f)
            
    # Lista arquivos em subpastas conhecidas (amd, nvidia, generic)
    for sub in ["amd", "nvidia", "generic"]:
        for category in ["system", "reports"]:
            pasta_sub = os.path.join(pasta_base, sub, category)
            if os.path.isdir(pasta_sub):
                for f in os.listdir(pasta_sub):
                    if f.lower().endswith((".log", ".json", ".md", ".txt")):
                        arquivos_encontrados.append(os.path.join(sub, category, f))
                    
    return pasta_base, sorted(arquivos_encontrados)


def _ler_linhas_arquivo(caminho, max_linhas=None):
    """Le texto UTF-8; opcionalmente mantem apenas as ultimas max_linhas."""
    try:
        with open(caminho, "r", encoding="utf-8", errors="replace") as f:
            linhas = f.readlines()
    except OSError as e:
        _log.warning("Leitura de log falhou (%s): %s", caminho, e)
        return None, str(e)
    if max_linhas is not None and len(linhas) > max_linhas:
        linhas = linhas[-max_linhas:]
    return linhas, None


def _mostrar_arquivo(caminho, titulo, ultimas=None):
    nome = os.path.basename(caminho)
    linhas, erro = _ler_linhas_arquivo(caminho, max_linhas=ultimas)
    print(f"\n{Fore.CYAN}{titulo}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Arquivo: {nome}{Style.RESET_ALL}")
    print(Fore.BLUE + "-" * 72 + Style.RESET_ALL)
    if erro:
        print(Fore.RED + f"Erro ao ler: {erro}" + Style.RESET_ALL)
        return
    if not linhas:
        print(Fore.YELLOW + "(arquivo vazio)" + Style.RESET_ALL)
        return
    if ultimas:
        print(
            Fore.YELLOW
            + f"(ultimas {len(linhas)} linhas){Style.RESET_ALL}\n"
        )
    corpo = "".join(linhas)
    print(Fore.WHITE + corpo.rstrip() + Style.RESET_ALL)
    print(Fore.BLUE + "-" * 72 + Style.RESET_ALL)


def _abrir_pasta_logs():
    pasta = obter_diretorio_logs()
    if not os.path.isdir(pasta):
        print(Fore.RED + f"Pasta nao encontrada: {pasta}" + Style.RESET_ALL)
        return
    try:
        if os.name == "nt":
            os.startfile(pasta)
        else:
            subprocess.run(["xdg-open", pasta], check=False)
        print(Fore.GREEN + f"Pasta aberta: {pasta}" + Style.RESET_ALL)
    except OSError:
        _log.exception("Nao foi possivel abrir a pasta de logs no explorador.")
        print(Fore.RED + "Nao foi possivel abrir a pasta — veja o log do sistema." + Style.RESET_ALL)


def menu_log_sistema():
    """Loop do menu Log de Sistema."""
    _log.info("Menu log de sistema aberto")
    while True:
        limpar_tela()
        relogio = obter_relogio_atual()
        pasta_logs, arquivos = _listar_arquivos_log()

        print(relogio.center(60))
        print()
        print(Fore.BLUE + "=" * 62 + Style.RESET_ALL)
        print(f"{Fore.YELLOW}📜 LOG DE SISTEMA{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Pasta: {pasta_logs}{Style.RESET_ALL}")
        print(Fore.BLUE + "=" * 62 + Style.RESET_ALL)
        print()
        print(f"{Fore.YELLOW}1{Style.RESET_ALL} - Ver ultimas linhas de {LOG_ERRO_PADRAO}")
        print(f"{Fore.YELLOW}2{Style.RESET_ALL} - Ver {LOG_ERRO_PADRAO} completo (aviso se for grande)")
        print(f"{Fore.YELLOW}3{Style.RESET_ALL} - Escolher outro arquivo (inclui reports e system)")
        print(f"{Fore.YELLOW}4{Style.RESET_ALL} - Listar todos os arquivos em subpastas")
        print(f"{Fore.YELLOW}5{Style.RESET_ALL} - Abrir pasta logs no explorador")
        print(f"{Fore.YELLOW}6{Style.RESET_ALL} - Ver log de SISTEMA AMD (system/sistema_amd.log)")
        print(f"{Fore.YELLOW}7{Style.RESET_ALL} - Ver log de SISTEMA NVIDIA (system/sistema_nvidia.log)")
        print(f"{Fore.YELLOW}8{Style.RESET_ALL} - Listar relatorios GERAIS (generic/reports)")
        print(f"{Fore.RED}0{Style.RESET_ALL} - Voltar ao menu principal")
        print()

        opcao = input(Fore.CYAN + "Escolha uma opcao: " + Style.RESET_ALL).strip()

        if opcao == "0":
            _log.info("Menu log de sistema: voltar ao principal")
            break

        if opcao == "1":
            caminho = os.path.join(pasta_logs, LOG_ERRO_PADRAO)
            if not os.path.isfile(caminho):
                print(
                    Fore.YELLOW
                    + f"Ainda nao existe {LOG_ERRO_PADRAO} (sem erros registrados)."
                    + Style.RESET_ALL
                )
            else:
                n_txt = input(
                    Fore.CYAN + "Quantas ultimas linhas (padrao 80): " + Style.RESET_ALL
                ).strip()
                try:
                    n = int(n_txt) if n_txt else 80
                    n = max(10, min(n, 500))
                except ValueError:
                    n = 80
                _mostrar_arquivo(
                    caminho,
                    "Ultimas linhas do log de erros",
                    ultimas=n,
                )
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")

        elif opcao == "2":
            caminho = os.path.join(pasta_logs, LOG_ERRO_PADRAO)
            if not os.path.isfile(caminho):
                print(
                    Fore.YELLOW
                    + f"Arquivo {LOG_ERRO_PADRAO} nao encontrado."
                    + Style.RESET_ALL
                )
            else:
                try:
                    tamanho = os.path.getsize(caminho)
                except OSError:
                    tamanho = 0
                if tamanho > 200_000:
                    conf = input(
                        Fore.YELLOW
                        + f"Arquivo grande (~{tamanho // 1024} KB). "
                        + "Deseja mesmo exibir tudo? (s/N): "
                        + Style.RESET_ALL
                    ).strip().lower()
                    if conf not in ("s", "sim"):
                        print(Fore.CYAN + "Cancelado. Use opcao 1 para ver o final." + Style.RESET_ALL)
                        input(f"\n{Fore.CYAN}↩️  Enter...")
                        continue
                _mostrar_arquivo(caminho, "Log de erros completo", ultimas=None)
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")

        elif opcao == "3":
            if not arquivos:
                print(Fore.YELLOW + "Nenhum arquivo .log na pasta." + Style.RESET_ALL)
            else:
                print(f"\n{Fore.CYAN}Arquivos .log:{Style.RESET_ALL}")
                for i, nome in enumerate(arquivos, 1):
                    print(f"  {Fore.YELLOW}{i}{Style.RESET_ALL} - {nome}")
                raw = input(
                    Fore.CYAN + "Numero do arquivo (0 = cancelar): " + Style.RESET_ALL
                ).strip()
                if raw.isdigit():
                    idx = int(raw)
                    if 1 <= idx <= len(arquivos):
                        caminho = os.path.join(pasta_logs, arquivos[idx - 1])
                        modo = input(
                            Fore.CYAN + "Ultimas N linhas (numero) ou Enter para ultimas 120: "
                            + Style.RESET_ALL
                        ).strip()
                        try:
                            n = int(modo) if modo else 120
                            n = max(10, min(n, 1000))
                        except ValueError:
                            n = 120
                        _mostrar_arquivo(caminho, "Visualizacao", ultimas=n)
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")

        elif opcao == "4":
            print(f"\n{Fore.CYAN}Arquivos em {pasta_logs}:{Style.RESET_ALL}")
            if not os.path.isdir(pasta_logs):
                print(Fore.RED + "Pasta logs nao existe." + Style.RESET_ALL)
            elif not arquivos:
                print(Fore.YELLOW + "(nenhum .log)" + Style.RESET_ALL)
            else:
                for nome in arquivos:
                    caminho = os.path.join(pasta_logs, nome)
                    try:
                        tam = os.path.getsize(caminho)
                    except OSError:
                        tam = 0
                    print(f"  - {nome}  ({tam} bytes)")
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")

        elif opcao == "5":
            _abrir_pasta_logs()
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")

        elif opcao == "6":
            caminho = os.path.join(pasta_logs, "amd", "system", "sistema_amd.log")
            if not os.path.isfile(caminho):
                print(Fore.YELLOW + "Log de sistema AMD ainda nao gerado em /system." + Style.RESET_ALL)
            else:
                _mostrar_arquivo(caminho, "Log de Sistema AMD", ultimas=100)
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")

        elif opcao == "7":
            caminho = os.path.join(pasta_logs, "nvidia", "system", "sistema_nvidia.log")
            if not os.path.isfile(caminho):
                print(Fore.YELLOW + "Log de sistema NVIDIA ainda nao gerado em /system." + Style.RESET_ALL)
            else:
                _mostrar_arquivo(caminho, "Log de Sistema NVIDIA", ultimas=100)
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")

        elif opcao == "8":
            pasta_gen = os.path.join(pasta_logs, "generic", "reports")
            if not os.path.isdir(pasta_gen):
                print(Fore.YELLOW + "Pasta de relatorios gerais nao encontrada." + Style.RESET_ALL)
            else:
                arquivos_gen = sorted([f for f in os.listdir(pasta_gen) if f.endswith(".json")])
                if not arquivos_gen:
                    print(Fore.YELLOW + "Nenhum relatorio JSON em generic/reports." + Style.RESET_ALL)
                else:
                    print(f"\n{Fore.CYAN}Relatorios em generic/reports:{Style.RESET_ALL}")
                    for i, f in enumerate(arquivos_gen, 1):
                        print(f"  {Fore.YELLOW}{i}{Style.RESET_ALL} - {f}")
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")

        else:
            print(Fore.RED + "Opcao invalida." + Style.RESET_ALL)
            input(f"\n{Fore.CYAN}↩️  Enter para continuar...{Style.RESET_ALL}")
