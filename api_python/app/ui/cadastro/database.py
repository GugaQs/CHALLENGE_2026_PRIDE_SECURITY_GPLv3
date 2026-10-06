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

"""Persistencia simples em arquivo TXT para o modulo de cadastro."""

import os

from app.utils.log_sistema import get_logger
from app.utils.tempo import (
    obter_timestamp,
    obter_timestamp_utc_brasil,
    obter_timestamp_sistema,
)

ARQUIVO_USUARIOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "usuarios.txt"))

_log = get_logger("cadastro_db")

def persistir_usuario(nome, email, cpf):
    """
    Grava o usuario no arquivo TXT com formato
    `timestamp_utc;timestamp_utc_brasil;data_sistema;nome;email;cpf`.

    Args:
        nome: Nome do usuario.
        email: Email informado.
        cpf: CPF informado.

    Returns:
        dict | bool: Dicionario de datas do registro em sucesso, ou False em erro.
    """
    try:
        data_registro_utc = obter_timestamp()
        data_registro_utc_br = obter_timestamp_utc_brasil()
        data_registro_sistema = obter_timestamp_sistema()
        with open(ARQUIVO_USUARIOS, "a", encoding="utf-8") as f:
            # Formato atualizado:
            # utc_global;utc_brasil;data_sistema;nome;email;cpf
            f.write(
                f"{data_registro_utc};{data_registro_utc_br};"
                f"{data_registro_sistema};{nome};{email};{cpf}\n"
            )
        return {
            "utc_global": data_registro_utc,
            "utc_brasil": data_registro_utc_br,
            "data_sistema": data_registro_sistema,
        }
    except Exception:
        _log.exception("Falha ao persistir usuario em %s", ARQUIVO_USUARIOS)
        print("Erro ao persistir usuário — detalhes no log do sistema.")
        return False

def carregar_usuarios():
    """
    Le os registros do arquivo TXT e retorna lista com os campos.

    Returns:
        list[list[str]]: Lista de registros no formato
        `[timestamp_utc, timestamp_utc_brasil, data_sistema, nome, email, cpf]`
        ou formato legado `[timestamp_utc, nome, email, cpf]`.
    """
    if not os.path.exists(ARQUIVO_USUARIOS):
        return []

    usuarios_cadastrados = []
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
            for linha in f:
                dados = linha.strip().split(";")
                if len(dados) >= 4:
                    usuarios_cadastrados.append(dados)
        return usuarios_cadastrados
    except Exception:
        _log.exception("Falha ao ler arquivo de usuarios: %s", ARQUIVO_USUARIOS)
        print("Erro ao ler banco de dados — detalhes no log do sistema.")
        return []