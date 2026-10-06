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

"""Listagem de usuarios cadastrados no arquivo local."""

from colorama import init, Fore, Style
import os
import sys

# 1. AJUSTE DE PATH: Permite que o Python encontre os módulos da raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# 2. TRATAMENTO DE IMPORT: Resolve o conflito entre execução direta e via pacote
try:
    from app.ui.cadastro.database import ARQUIVO_USUARIOS # Para execução direta (python list.py)
except ImportError:
    from .database import ARQUIVO_USUARIOS # Para execução via main.py

from app.utils.log_sistema import get_logger

init(autoreset=True)

_log = get_logger("cadastro_list")

def listar_usuarios():
    """Le os registros em arquivo e apresenta dados formatados no terminal.

    O modulo aceita linhas nos formatos:
    - legado: `timestamp_utc;nome;email;cpf`
    - atual: `timestamp_utc;timestamp_utc_brasil;data_sistema;nome;email;cpf`
    """
    print()
    print(Fore.CYAN + "================ USUÁRIOS CADASTRADOS ================")

    # Verificação de GRC: O arquivo físico existe no disco?
    if not os.path.exists(ARQUIVO_USUARIOS):
        _log.warning("Listagem: arquivo de usuarios inexistente (%s)", ARQUIVO_USUARIOS)
        print(Fore.RED + "⚠️ Base de dados não encontrada ou vazia." + Style.RESET_ALL)
        print(Fore.CYAN + "======================================================")
        return

    try:
        # Abrindo o arquivo em modo leitura ("r")
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
            linhas = f.readlines()

        if len(linhas) == 0:
            print(Fore.RED + "⚠️ Nenhum usuário cadastrado no arquivo." + Style.RESET_ALL)
        else:
            for i, linha in enumerate(linhas, start=1):
                # Desmembra a linha (Split pelo separador definido no banco)
                dados = linha.strip().split(";")
                
                # Compatibilidade com estrutura antiga e nova.
                if len(dados) == 4:
                    data_hora, nome, email, cpf = dados
                    
                    print()
                    print(f"{Fore.YELLOW}Registro #{i}{Style.RESET_ALL}")
                    print(f"🕒 UTC Global..: {data_hora} UTC")
                    print(f"👤 Nome....: {nome}")
                    print(f"📧 Email...: {email}")
                    print(f"🆔 CPF.....: {cpf}")
                elif len(dados) >= 6:
                    data_hora_utc, data_hora_br, data_sistema, nome, email, cpf = dados[:6]

                    print()
                    print(f"{Fore.YELLOW}Registro #{i}{Style.RESET_ALL}")
                    print(f"🕒 UTC Global..: {data_hora_utc} UTC")
                    print(f"🇧🇷 UTC Brasil..: {data_hora_br} (UTC-03)")
                    print(f"🖥️ Data Sistema: {data_sistema}")
                    print(f"👤 Nome....: {nome}")
                    print(f"📧 Email...: {email}")
                    print(f"🆔 CPF.....: {cpf}")
                else:
                    # Se alguém editou o TXT e quebrou a estrutura, o SOC avisa:
                    print(f"{Fore.RED}⚠️ Registro {i} corrompido ou legado (formato antigo).{Style.RESET_ALL}")

    except Exception:
        _log.exception("Falha ao ler listagem de usuarios (%s)", ARQUIVO_USUARIOS)
        print(f"{Fore.RED}❌ Erro técnico ao ler arquivo — veja o log do sistema.{Style.RESET_ALL}")

    print(Fore.CYAN + "======================================================" + Style.RESET_ALL)

# 3. BLOCO DE TESTE: Executa a listagem apenas se rodar o arquivo diretamente
if __name__ == "__main__":
    listar_usuarios()