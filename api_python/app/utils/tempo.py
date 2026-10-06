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
Utilitarios de data/hora para exibicao no terminal e logs.

Por que tres referencias de tempo?
-------------------------------
- UTC (`timezone.utc`): padrao mundial para comparar eventos entre maquinas/regioes.
- UTC-03 fixo: referencia pedagogica "hora Brasil" sem depender do SO (horario de verso).
- Hora local (`astimezone()`): o que o sistema operacional considera "agora" ai —
  util para depurar quando o note esta em outro fuso.

Formatacao em texto (`strftime`) e apenas para exibir ao usuario; para calculos use
sempre objetos `datetime` com timezone explícito.
"""

from datetime import datetime, timedelta, timezone

from colorama import Fore, Style

# Offset fixo -3 h em relacao ao UTC (equivalente ao horario padrao de Brasilia).
UTC_BRASIL = timezone(timedelta(hours=-3))


def obter_relogio_atual():
    """Monta a linha colorida do relogio no cabecalho dos menus (valor em UTC)."""
    return f"{Fore.CYAN}[ {obter_timestamp()} UTC ]{Style.RESET_ALL}"


def obter_timestamp():
    """Momento atual em UTC — usar como referencia principal em logs e cadastros."""
    agora = datetime.now(timezone.utc)
    return agora.strftime('%d/%m/%Y | %H:%M:%S')


def obter_timestamp_utc_brasil():
    """Mesmo instante expresso no deslocamento UTC-03 (comparacao com relatorios BR)."""
    agora_br = datetime.now(UTC_BRASIL)
    return agora_br.strftime('%d/%m/%Y | %H:%M:%S')


def obter_timestamp_sistema():
    """Relogio configurado no Windows/Linux (inclui offset do SO na propria string)."""
    agora_sistema = datetime.now().astimezone()
    return agora_sistema.strftime('%d/%m/%Y | %H:%M:%S %z')
