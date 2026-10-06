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
ASPM PRIDE Security — ponto de entrada (CLI).

Fluxo didático em camadas
-------------------------
1) Este arquivo (`main.py`) so orquestra: menu, opções e tratamento de erro global.
2) Cada opção delega para um módulo em `app/ui/...` (cadastro, scan, logs, sobre).
3) Regras de seguranca do scan ficam em `app/ui/scan_projeto/filtros/regras_seguranca.py`.
4) Persistência simples do cadastro: arquivo texto em `app/ui/cadastro/`.

Logging
-------
- Configuração central em `app/utils/log_sistema.py` (`get_logger`): um único ficheiro
  `logs/erro_sistema.log`, nível INFO no handler, timestamps UTC.
- Módulos registam fluxo (INFO/WARNING) e exceções (`logger.exception`) nos pontos críticos.

Próximos passos sugeridos no documento de análise (resumo)
-----------------------------------------------------------
- Validar entradas (e-mail, CPF, caminho do projeto) antes de persistir.
- Substituir TXT por SQLite quando precisar consultas e integridade.
- Testes automatizados: ver pasta `tests/` e `pytest`.
"""

import sys
import os
from colorama import init, Fore, Style

# Forçar output em UTF-8 para evitar erros com emojis no Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Adiciona o diretório atual ao path para facilitar imports relativos quando rodar daqui
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.ui.menu import menu
from app.ui.cadastro.menu_cadastro import cadastro_menu
from app.ui.scan_projeto.menu_scan_projeto import scan_projeto
from app.ui.scan_ia_local.menu_ia_local import menu_ia_local
from app.ui.scan_ia_api.menu_ia_api import menu_ia_api
from app.ui.sobre.sobre import mostrar_sobre
from app.ui.log_sistema.menu_log_sistema import menu_log_sistema
from app.ui.scan_containers.menu_scan_containers import menu_scan_containers
from app.utils.helpers import limpar_tela
from app.utils.tempo import obter_relogio_atual
from app.utils.log_sistema import get_logger

# Log central: ver `app/utils/log_sistema.py` (ficheiro `logs/erro_sistema.log`).
logger_sistema = get_logger()

init(autoreset=True)

def main():
    """Executa o loop principal da aplicacao com tratamento de falhas.

    Fluxo:
    1) Limpa tela e renderiza menu.
    2) Captura opcao do usuario.
    3) Encaminha para o modulo correspondente.
    4) Trata interrupcao manual e excecoes inesperadas.
    """
    try:
        while True:
            limpar_tela()
            print()
            relogio = obter_relogio_atual()
            print()
            menu(relogio)  # Cabecalho visual — texto em app/ui/menu.py
            print()
            opcao = input(Fore.CYAN + "👉  Escolha uma opção: " + Style.RESET_ALL)

            if opcao == "1":
                logger_sistema.info("Menu principal: entrada modulo cadastro")
                cadastro_menu()
            elif opcao == "2":
                logger_sistema.info("Menu principal: opcao scan de software (placeholder)")
                print(Fore.YELLOW + "\n🚧 🔍 Módulo de Scan de Software está em desenvolvimento! Aguarde novidades.")
                input(f"\n{Fore.CYAN}↩️  Pressione Enter para continuar...{Style.RESET_ALL}")
            elif opcao == "3":
                logger_sistema.info("Menu principal: entrada modulo scan de projeto")
                scan_projeto()
            elif opcao == "4":
                logger_sistema.info("Menu principal: entrada modulo scan IA local")
                menu_ia_local()
            elif opcao == "5":
                logger_sistema.info("Menu principal: entrada modulo scan IA API")
                menu_ia_api()
            elif opcao == "6":
                logger_sistema.info("Menu principal: entrada log de sistema")
                menu_log_sistema()

            
            elif opcao == "7":
                logger_sistema.info("Menu principal: modulo scan de containers")
                menu_scan_containers()
            elif opcao == "8":
                logger_sistema.info("Menu principal: tela sobre")
                mostrar_sobre()
            elif opcao == "0":
                logger_sistema.info("Menu principal: saida solicitada pelo usuario")
                print(Fore.GREEN + "\n👋  Saindo... Até logo!")
                break
            else:
                logger_sistema.warning("Menu principal: opcao invalida (%r)", opcao)
                print(Fore.RED + "\n⚠️  Opção inválida! Tente novamente.")
                input(f"\n{Fore.CYAN}↩️  Pressione Enter para continuar...{Style.RESET_ALL}")
                
    except KeyboardInterrupt:
        logger_sistema.warning(
            "Execucao interrompida pelo usuario (KeyboardInterrupt)."
        )
        # Tratamento explícito para Ctrl+C inserido pelo usuário
        print(Fore.YELLOW + "\n\n⚠️  Interrupção manual (Ctrl+C) detectada. Encerrando a aplicação com segurança." + Style.RESET_ALL)
    except Exception:
        # Excecao inesperada: traceback completo no ficheiro
        print(Fore.RED + "\n❌ Ocorreu um erro fatal durante a execução! Detalhes foram salvos no Log de Sistema." + Style.RESET_ALL)
        logger_sistema.exception("Erro fatal no loop principal (main).")
        input(f"\n{Fore.CYAN}↩️  Pressione Enter para fechar...{Style.RESET_ALL}")
 
if __name__ == "__main__":
    main()