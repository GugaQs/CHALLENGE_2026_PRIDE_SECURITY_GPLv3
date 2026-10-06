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

"""Configuracao do modulo scan IA via API (funcoes puras)."""

import json
import os

from app.utils.log_sistema import get_logger

_log = get_logger("scan_ia_api_config")

PROVEDORES_DISPONIVEIS = ("openai", "anthropic", "gemini")


def _pasta_config():
    """Pasta logs/config na raiz do projeto."""
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    pasta = os.path.join(base, "logs", "config")
    os.makedirs(pasta, exist_ok=True)
    return pasta


def _arquivo_config():
    return os.path.join(_pasta_config(), "ia_api.json")


def carregar_config_ia_api():
    """Carrega provedor e flag de chave configurada."""
    padrao = {
        "provedor": "openai",
        "tem_chave": False,
        "api_key_mascarada": "",
    }
    caminho = _arquivo_config()
    if not os.path.isfile(caminho):
        return padrao

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        padrao.update({k: dados.get(k, padrao[k]) for k in padrao})
    except (OSError, json.JSONDecodeError):
        _log.warning("Config IA API invalida, usando padrao.")
    return padrao


def salvar_provedor_ia_api(provedor):
    """Persiste provedor selecionado."""
    provedor = (provedor or "").strip().lower()
    if provedor not in PROVEDORES_DISPONIVEIS:
        return False, "Provedor invalido."

    config = carregar_config_ia_api()
    config["provedor"] = provedor
    try:
        with open(_arquivo_config(), "w", encoding="utf-8") as arquivo:
            json.dump(config, arquivo, indent=2, ensure_ascii=False)
    except OSError:
        _log.exception("Falha ao salvar provedor IA API.")
        return False, "Nao foi possivel salvar configuracao."

    return True, f"Provedor definido: {provedor}."


def registrar_api_key_ia_api(api_key):
    """
    Registra que uma chave foi informada (nao grava a chave completa em disco).
    Armazena apenas os 4 ultimos caracteres para exibicao.
    """
    api_key = (api_key or "").strip()
    if len(api_key) < 8:
        return False, "Informe uma API key valida (minimo 8 caracteres)."

    config = carregar_config_ia_api()
    config["tem_chave"] = True
    config["api_key_mascarada"] = "*" * (len(api_key) - 4) + api_key[-4:]

    try:
        with open(_arquivo_config(), "w", encoding="utf-8") as arquivo:
            json.dump(config, arquivo, indent=2, ensure_ascii=False)
    except OSError:
        _log.exception("Falha ao registrar API key IA API.")
        return False, "Nao foi possivel salvar configuracao."

    _log.info("API key IA API registrada (mascarada em disco).")
    return True, "API key registrada com sucesso (nao armazenamos a chave completa)."


def iniciar_varredura_ia_api(caminho_projeto):
    """Placeholder da varredura remota via API."""
    caminho_projeto = (caminho_projeto or "").strip()
    if not caminho_projeto or not os.path.isdir(caminho_projeto):
        return False, "Informe um caminho de projeto valido."

    config = carregar_config_ia_api()
    if not config.get("tem_chave"):
        return False, "Configure a API key antes de iniciar a varredura."

    _log.info(
        "Varredura IA API solicitada (placeholder): provedor=%s caminho=%s",
        config.get("provedor"),
        caminho_projeto,
    )
    return (
        False,
        "Varredura remota via API em desenvolvimento. "
        f"Provedor atual: {config.get('provedor')}.",
    )
