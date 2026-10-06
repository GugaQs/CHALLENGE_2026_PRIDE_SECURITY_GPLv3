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

"""Listagem filtrada simples sobre relatorios de scan."""

from __future__ import annotations

from colorama import Fore, Style

from app.utils.helpers import limpar_tela
from app.utils.log_sistema import get_logger
from ..listar_falhas import apresentar_tabela_logs, ler_json_log
from .service import (
    agrupar_por_campo,
    carregar_falhas,
    filtrar_falhas,
    ranking_arquivos_criticos,
    salvar_relatorio_filtrado,
)

_log = get_logger("scan_listar_menu")

# Normaliza entrada do usuario para o valor salvo no JSON
_ALIASES_SEVERIDADE = {
    "CRITICO": "CRÍTICO",
    "CRÍTICO": "CRÍTICO",
    "MEDIO": "MÉDIO",
    "MÉDIO": "MÉDIO",
    "ALTO": "ALTO",
    "ALTA": "ALTO",
    "BAIXO": "BAIXO",
    "BAIXA": "BAIXO",
}


def _montar_filtros_simples(falhas):
    """Uma lista numerada + ate duas linhas de resposta."""
    por_tipo = agrupar_por_campo(falhas, "tipo")
    ordenado = sorted(por_tipo.items(), key=lambda x: len(x[1]), reverse=True)

    print(f"\n{Fore.CYAN}Tipos de alerta no relatorio:{Style.RESET_ALL}")
    print(Fore.BLUE + "-" * 60 + Style.RESET_ALL)
    for i, (nome, ocorrencias) in enumerate(ordenado, 1):
        nome_curto = nome if len(nome) <= 52 else nome[:49] + "..."
        print(f"  {Fore.YELLOW}{i:2}{Style.RESET_ALL}  {nome_curto}  ({len(ocorrencias)})")
    print(Fore.BLUE + "-" * 60 + Style.RESET_ALL)

    nums = input(
        Fore.CYAN + "Numeros dos tipos (ex: 1,3) ou Enter = todos: " + Style.RESET_ALL
    ).strip()

    tipos_escolhidos = set()
    if nums:
        for parte in nums.replace(";", ",").split(","):
            parte = parte.strip()
            if not parte.isdigit():
                continue
            idx = int(parte)
            if 1 <= idx <= len(ordenado):
                tipos_escolhidos.add(ordenado[idx - 1][0])

    sev_txt = input(
        Fore.CYAN + "Severidade (CRITICO, ALTO, MEDIO, BAIXO) ou Enter = todas: "
        + Style.RESET_ALL
    ).strip().upper()

    severidades = set()
    if sev_txt:
        for tok in sev_txt.replace(";", ",").split(","):
            tok = tok.strip()
            if not tok:
                continue
            severidades.add(_ALIASES_SEVERIDADE.get(tok, tok))

    return {
        "tipo": tipos_escolhidos,
        "severidade": severidades,
        "confianca": set(),
        "arquivo_contem": None,
        "codigo_contem": None,
        "linha_min": None,
        "linha_max": None,
    }


def _mostrar_resultado(filtradas, max_linhas=25):
    print(
        f"\n{Fore.GREEN}Total apos filtro: {len(filtradas)} alerta(s){Style.RESET_ALL}"
    )
    print(Fore.BLUE + "=" * 72 + Style.RESET_ALL)
    for falha in filtradas[:max_linhas]:
        print(
            f"{falha.get('severidade', '-'):8} | {str(falha.get('tipo', '-'))[:36]:36} | "
            f"{falha.get('arquivo', '-')}:{falha.get('linha', '-')}"
        )
    if len(filtradas) > max_linhas:
        print(f"... e mais {len(filtradas) - max_linhas} alerta(s)")
    print(Fore.BLUE + "=" * 72 + Style.RESET_ALL)

    top = ranking_arquivos_criticos(filtradas, top_n=5)
    if top:
        print(f"{Fore.CYAN}Arquivos com mais peso (top 5):{Style.RESET_ALL}")
        for item in top:
            print(f"  • {item['arquivo']} (score {item['score']})")


def filtrar_alertas_relatorio(caminho_log: str, *, limpar_tela_inicio: bool = True) -> None:
    """
    Executa o fluxo de filtro para um JSON ja escolhido (sem nova lista de arquivos).

    Args:
        caminho_log: Caminho do arquivo JSON do relatorio.
        limpar_tela_inicio: Se True, limpa a tela antes (padrao ao vir do menu scan).
    """
    if limpar_tela_inicio:
        limpar_tela()
    print(Fore.BLUE + "=" * 60)
    print(f"{Fore.YELLOW}FILTRAR ALERTAS{Style.RESET_ALL}")
    print(Fore.BLUE + "=" * 60 + Style.RESET_ALL)

    dados = ler_json_log(caminho_log)
    if not dados:
        input(f"\n{Fore.CYAN}↩️  Enter para voltar...{Style.RESET_ALL}")
        return

    falhas = carregar_falhas(dados)
    if not falhas:
        print(Fore.RED + "Nenhuma falha neste relatorio." + Style.RESET_ALL)
        input(f"\n{Fore.CYAN}↩️  Enter para voltar...{Style.RESET_ALL}")
        return

    filtros = _montar_filtros_simples(falhas)
    filtradas = filtrar_falhas(falhas, filtros)
    _mostrar_resultado(filtradas)

    exp = input(
        Fore.CYAN + "Salvar JSON filtrado? (s/N): " + Style.RESET_ALL
    ).strip().lower()
    if exp in ("s", "sim", "y"):
        if filtradas:
            try:
                path = salvar_relatorio_filtrado(dados, filtros, filtradas, caminho_log)
                print(f"{Fore.GREEN}Salvo: {path}{Style.RESET_ALL}")
            except OSError:
                _log.exception("Erro ao salvar relatorio filtrado.")
                print(f"{Fore.RED}Erro ao salvar — detalhes no log do sistema.{Style.RESET_ALL}")
        else:
            print(Fore.YELLOW + "Nada para salvar." + Style.RESET_ALL)

    input(f"\n{Fore.CYAN}↩️  Enter para voltar...{Style.RESET_ALL}")


def menu_listar_filtros():
    """Fluxo autonomo: escolhe relatorio na lista e depois filtra."""
    limpar_tela()
    print(Fore.BLUE + "=" * 60)
    print(f"{Fore.YELLOW}FILTRAR ALERTAS DO RELATORIO{Style.RESET_ALL}")
    print(Fore.BLUE + "=" * 60 + Style.RESET_ALL)

    caminho_log = apresentar_tabela_logs()
    if not caminho_log:
        return

    filtrar_alertas_relatorio(caminho_log, limpar_tela_inicio=False)
