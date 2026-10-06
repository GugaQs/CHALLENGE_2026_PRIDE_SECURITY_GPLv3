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

"""Fluxo de cadastro de usuario no modulo de cadastro."""

from colorama import Fore, Style, init
import sys
import os

# Ajuste técnico para permitir testes isolados de pacotes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Se for testar isolado, use o import absoluto temporariamente ou ajuste o path
try:
    from app.ui.cadastro.database import persistir_usuario  # Tenta importar localmente se rodar direto
except ImportError:
    from .database import persistir_usuario # Usa o relativo se rodar pela main

from app.utils.validacao_cadastro import (
    formatar_cpf_exibicao,
    normalizar_cpf,
    normalizar_email,
    normalizar_nome,
    validar_formulario_cadastro,
)
from app.utils.log_sistema import get_logger

init(autoreset=True)

_log = get_logger("cadastro_create")

def add_usuario():
    """Coleta dados de usuario via terminal e persiste no arquivo local.

    O fluxo solicita nome, email e CPF, grava no arquivo de dados e exibe um
    recibo visual para o usuario.
    """
    print(f"{Fore.CYAN}👤 NOVO USUÁRIO")
    print()
    nome =  input("👤 Digite o nome do usuário..: ")
    email = input("📧 Digite o email do usuário.: ")
    cpf =   input("🆔 Digite o CPF do usuário...: ")
    print()

    try:
        # Validação antes de gravar (evita lixo no TXT; ver app/utils/validacao_cadastro.py).
        form_ok, msg_erro = validar_formulario_cadastro(nome, email, cpf)
        if not form_ok:
            _log.warning("Cadastro rejeitado na validacao: %s", msg_erro)
            print(f"{Fore.RED}❌ Dados inválidos: {msg_erro}{Style.RESET_ALL}")
            return

        nome_s = normalizar_nome(nome)
        email_s = normalizar_email(email)
        cpf_s = normalizar_cpf(cpf)

        # 1. Grava no "Banco de Dados" (Arquivo TXT) e gera o timestamp automático
        registro_tempo = persistir_usuario(nome_s, email_s, cpf_s)
        
        if not registro_tempo:
            raise RuntimeError("Falha ao gerar metadados de tempo para auditoria.")

        _log.info(
            "Usuario cadastrado com sucesso (UTC auditoria: %s)",
            registro_tempo.get("utc_global", "?"),
        )

        # 2. Gera o Log de Auditoria (Simulação para teste)
        print(
            f"{Fore.YELLOW}ℹ️ [LOG]: Registro UTC gerado em "
            f"{registro_tempo['utc_global']} para auditoria."
        )

        # 3. Feedback Visual (Seu Recibo)
        print(f"\n{Fore.GREEN}======================================================")
        print(f"{Fore.GREEN}✅ USUÁRIO GRAVADO COM SUCESSO NO SISTEMA")
        print()
        print(f"{Fore.WHITE}🕒 UTC Global..: {registro_tempo['utc_global']} UTC")
        print(f"{Fore.WHITE}🇧🇷 UTC Brasil..: {registro_tempo['utc_brasil']} (UTC-03)")
        print(f"{Fore.WHITE}🖥️ Data Sistema: {registro_tempo['data_sistema']}")
        print()
        print(f"{Fore.GREEN}👤 Nome....: {nome_s}")
        print(f"{Fore.GREEN}📧 Email...: {email_s}")
        print(f"{Fore.GREEN}🆔 CPF.....: {formatar_cpf_exibicao(cpf_s)}")
        print()
        print(f"{Fore.GREEN}======================================================")

    except Exception as e:
        _log.exception("Erro no fluxo add_usuario.")
        print(f"{Fore.RED}❌ Erro crítico no processo de cadastro: {e}")

# O "Pulo do Gato" para rodar o teste isolado
if __name__ == "__main__":
    add_usuario()