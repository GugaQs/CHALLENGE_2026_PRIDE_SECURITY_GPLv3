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

"""Menu interativo para operacoes de scan de projeto."""

from colorama import init, Fore, Style
import os
import sys

# Garante que os imports relativos funcionem se rodar isolado ou pela main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Importar as funções de utilitários
from app.utils.helpers import limpar_tela
from app.utils.tempo import obter_relogio_atual

# Importar o motor do scanner de projeto
from .executar_scan import rodar_engine_scan
from .listar_falhas import (
    apresentar_tabela_logs,
    ler_json_log,
    navegar_falhas_detalhadamente,
    escolher_por_tipo,
    escolher_por_gravidade,
)
from .listar.menu_listar import filtrar_alertas_relatorio
from app.utils.log_sistema import get_logger

init(autoreset=True)

_log = get_logger("scan_projeto_menu")


def scan_projeto():
    """Exibe menu do scanner e direciona para scan ou visualizacao de logs."""
    _log.info("Menu scan de projeto exibido")
    while True:
        try:
            limpar_tela()
            relogio = obter_relogio_atual()
            menu_text = f"""
        {relogio.center(60)}
        {Fore.YELLOW}    📝  scanner de projetos{Style.RESET_ALL}

        {Fore.YELLOW}1 - ➕  SCANEAR PROJETO{Style.RESET_ALL}
        {Fore.YELLOW}2 - 📋  RELATORIO DE FALHAS (navegar ou filtrar){Style.RESET_ALL}

        {Fore.RED}0 - 🔙 VOLTAR AO MENU PRINCIPAL{Style.RESET_ALL}
        """
            print(menu_text)

            opcao = input(Fore.CYAN + "Escolha uma opção: " + Style.RESET_ALL)

            if opcao == "1":
                print()
                caminho = input(Fore.CYAN + "📂 Caminho do projeto: " + Style.RESET_ALL)
                if os.path.exists(caminho):
                    _log.info("Iniciando scan do projeto em %s", caminho)
                    rodar_engine_scan(caminho)
                else:
                    _log.warning("Scan abortado: caminho nao existe (%s)", caminho)
                    print(Fore.RED + "❌ Caminho não encontrado." + Style.RESET_ALL)
                input(f"\n{Fore.CYAN} ↩️  Pressione Enter para voltar ao menu...{Style.RESET_ALL}")
            elif opcao == "2":
                print()
                caminho_selecionado = apresentar_tabela_logs()
                if caminho_selecionado:
                    _log.info(
                        "Relatorio selecionado: %s",
                        os.path.basename(caminho_selecionado),
                    )
                    print(
                        f"\n{Fore.WHITE}Relatorio: "
                        f"{os.path.basename(caminho_selecionado)}{Style.RESET_ALL}"
                    )
                    dados_rel = ler_json_log(caminho_selecionado)
                    if not dados_rel:
                        continue
                    todas_falhas = dados_rel.get("vulnerabilidades", []) or dados_rel.get(
                        "falhas_encontradas", []
                    )

                    modo = input(
                        Fore.CYAN
                        + "👉 Enter=todas | T=por tipo | G=por gravidade | F=filtrar: "
                        + Style.RESET_ALL
                    ).strip().lower()

                    if modo in ("f", "filtro", "filtrar"):
                        filtrar_alertas_relatorio(caminho_selecionado)
                    elif modo in ("t", "tipo"):
                        falhas_sub, etiqueta = escolher_por_tipo(todas_falhas)
                        if etiqueta and not falhas_sub:
                            print(
                                Fore.YELLOW + "Nenhuma falha para esse criterio."
                                + Style.RESET_ALL
                            )
                            input(Fore.CYAN + "Enter para voltar... " + Style.RESET_ALL)
                        else:
                            navegar_falhas_detalhadamente(
                                caminho_selecionado,
                                falhas=falhas_sub,
                                etiqueta_filtro=etiqueta,
                            )
                    elif modo in ("g", "grav", "gravidade", "severidade"):
                        falhas_sub, etiqueta = escolher_por_gravidade(todas_falhas)
                        if etiqueta and not falhas_sub:
                            print(
                                Fore.YELLOW + "Nenhuma falha para esse criterio."
                                + Style.RESET_ALL
                            )
                            input(Fore.CYAN + "Enter para voltar... " + Style.RESET_ALL)
                        else:
                            navegar_falhas_detalhadamente(
                                caminho_selecionado,
                                falhas=falhas_sub,
                                etiqueta_filtro=etiqueta,
                            )
                    else:
                        navegar_falhas_detalhadamente(caminho_selecionado)
            elif opcao == "0":
                _log.info("Scan projeto: voltar ao menu principal")
                break
            else:
                _log.warning("Scan projeto: opcao invalida (%r)", opcao)
                print(Fore.RED + "⚠️ Opção inválida! Tente novamente.")
        except KeyboardInterrupt:
            raise
        except Exception:
            _log.exception("Erro no loop do menu scan de projeto.")
            print(
                Fore.RED
                + "❌ Erro registrado no log do sistema. Pressione Enter..."
                + Style.RESET_ALL
            )
            input(f"\n{Fore.CYAN} ↩️  Enter...{Style.RESET_ALL}")

if __name__ == "__main__":
    scan_projeto()
