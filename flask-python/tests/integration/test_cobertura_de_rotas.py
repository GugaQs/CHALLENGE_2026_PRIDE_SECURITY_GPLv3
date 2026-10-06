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
Cobertura de TODAS as rotas registradas — varredura que não envelhece.

PROPÓSITO DE NEGÓCIO
--------------------
Uma auditoria mediu que 25 dos 42 endpoints não tinham nenhum teste. Escrever um
teste por rota resolve hoje e apodrece amanhã: a rota nova nasce sem cobertura e
ninguém percebe.

Aqui a lista de rotas é lida do próprio `url_map` da aplicação. Rota nova entra
na varredura automaticamente, sem ninguém lembrar de nada — que é a diferença
entre guarda executável e documentação com sorte.

INVARIANTES DO DOMÍNIO
----------------------
- INV-ROT-001 · Toda rota GET sem parâmetro responde sem 5xx.
- INV-ROT-002 · Toda rota GET com parâmetro trata valor inexistente sem 5xx.
- INV-ROT-003 · Toda rota POST recusa corpo vazio sem 5xx.
- INV-ROT-004 · Nenhuma rota fica órfã da varredura por engano: a lista de
  exceções é explícita e justificada, uma linha por rota.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
5xx numa rota significa caminho não tratado alcançável por HTTP.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.integracao]


# Rotas deliberadamente fora da varredura automática, cada uma com o motivo.
# Manter esta lista CURTA: cada linha aqui é cobertura que se abre mão.
EXCECOES = {
    # Abre o explorador de arquivos do sistema operacional — numa suíte
    # automatizada, penduraria a execução esperando alguém fechar a janela.
    "/scan/selecionar-pasta": "abre dialogo nativo bloqueante",
    "/logs/abrir-pasta": "abre o Explorer na maquina de quem roda",
    "/scan/logs/<nome_log>/abrir-falha": "abre o editor do sistema",
    "/ia-local/imprimir-parecer": "envia para a impressora",
    # Servida pelo Flask, não é código do projeto.
    "/static/<path:filename>": "handler do proprio Flask",
}


def _rotas(app):
    """Todas as regras registradas, exceto as declaradas em EXCECOES."""
    for regra in app.url_map.iter_rules():
        if str(regra) in EXCECOES:
            continue
        yield regra


def _preencher(regra) -> str | None:
    """
    Substitui os parâmetros da rota por valores inexistentes porém plausíveis.

    Devolve None quando o conversor não é conhecido — melhor pular explicitamente
    do que inventar um valor e testar outra coisa.
    """
    caminho = str(regra)
    substitutos = {
        "nome_log": "relatorio_que_nao_existe.json",
        "job_id": "job_inexistente",
        "hw": "amd",
        "hardware": "amd",
        "arquivo": "arquivo_inexistente.md",
        "caminho_relativo": "generic/reports/inexistente.json",
        "nome_arquivo": "inexistente.log",
        "secao": "scan",
        "indice": "1",
        "falha_id": "1",
        "filename": "css/style.css",
    }
    for nome, valor in substitutos.items():
        caminho = caminho.replace(f"<{nome}>", valor)
        caminho = caminho.replace(f"<path:{nome}>", valor)
        caminho = caminho.replace(f"<int:{nome}>", valor)
    if "<" in caminho:
        return None
    return caminho


# ── INV-ROT-001 e 002 · GET ──────────────────────────────────────────────────

def test_toda_rota_get_responde_sem_erro_de_servidor(app, client_producao):
    """
    Varre todas as rotas GET com valores inexistentes.

    Um relatório apagado, um job já expirado ou um link antigo colado no
    navegador são situações rotineiras. Nenhuma pode devolver 500.
    """
    falhas = []
    puladas = []

    for regra in _rotas(app):
        if "GET" not in regra.methods:
            continue
        caminho = _preencher(regra)
        if caminho is None:
            puladas.append(str(regra))
            continue
        resposta = client_producao.get(caminho)
        if resposta.status_code >= 500:
            falhas.append(f"{regra} -> {caminho} -> {resposta.status_code}")

    assert not falhas, "Rotas GET com 5xx:\n  " + "\n  ".join(falhas)
    assert not puladas, (
        "Rotas puladas por conversor desconhecido — acrescente o parametro em "
        f"`_preencher` para que voltem a ser cobertas: {puladas}"
    )


def test_toda_rota_get_sem_parametro_responde_200(
    app, client_producao, sandbox_de_caminhos
):
    """
    Página sem parâmetro tem de abrir. Aqui 200 é o critério, não "não-500".

    Uma página que responde 302 para todo mundo está quebrada de outro jeito —
    e passaria despercebida num teste que só recusa 5xx.

    O sandbox é semeado com os logs de hardware antes da varredura: as rotas
    `/logs/atalho/*` redirecionam quando o arquivo alvo não existe, e sem a
    semente o teste mediria a ausência do arquivo em vez da saúde da rota.
    """
    for hardware in ("amd", "nvidia"):
        destino = (
            sandbox_de_caminhos / "logs" / hardware / "system"
            / f"sistema_{hardware}.log"
        )
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(
            "2026-01-01 00:00:00,000 - INFO - ASPM - linha semeada pelo teste\n",
            encoding="utf-8",
        )

    problemas = []
    for regra in _rotas(app):
        if "GET" not in regra.methods or regra.arguments:
            continue
        caminho = str(regra)
        resposta = client_producao.get(caminho)
        if resposta.status_code != 200:
            problemas.append(f"{caminho} -> {resposta.status_code}")

    assert not problemas, "Paginas que nao abriram:\n  " + "\n  ".join(problemas)


# ── INV-ROT-003 · POST ───────────────────────────────────────────────────────

def test_toda_rota_post_recusa_corpo_vazio_sem_erro_de_servidor(app, client_producao):
    """POST sem nenhum campo é o caso de um formulário submetido em branco."""
    falhas = []
    for regra in _rotas(app):
        if "POST" not in regra.methods:
            continue
        caminho = _preencher(regra)
        if caminho is None:
            continue
        for kwargs in ({"data": {}}, {"json": {}}):
            resposta = client_producao.post(caminho, **kwargs)
            if resposta.status_code >= 500:
                falhas.append(f"{regra} -> {caminho} ({kwargs}) -> {resposta.status_code}")

    assert not falhas, "Rotas POST com 5xx:\n  " + "\n  ".join(falhas)


# ── INV-ROT-004 · A varredura cobre mesmo tudo? ──────────────────────────────

def test_lista_de_excecoes_nao_tem_rota_fantasma(app):
    """
    Toda rota em `EXCECOES` precisa existir de verdade.

    Uma exceção apontando para rota que foi renomeada esconde a rota nova: ela
    não é testada e ninguém sabe. É a mesma classe de falha da guarda que varria
    diretório inexistente e saía verde.
    """
    registradas = {str(r) for r in app.url_map.iter_rules()}
    fantasmas = sorted(set(EXCECOES) - registradas)
    assert not fantasmas, (
        f"EXCECOES aponta para rotas que nao existem mais: {fantasmas}. "
        "Remova-as, senao a rota que as substituiu fica sem cobertura."
    )


def test_a_varredura_cobre_a_maioria_das_rotas(app):
    """
    Controle positivo do instrumento: a varredura tem de estar vendo algo.

    Se `_preencher` parar de reconhecer os parâmetros, todas as rotas seriam
    puladas e os testes acima passariam por cegueira, não por saúde.
    """
    total = len(list(app.url_map.iter_rules()))
    cobertas = sum(1 for r in _rotas(app) if _preencher(r) is not None)

    assert total > 30, f"apenas {total} rotas no url_map — a app carregou?"
    assert cobertas >= total - len(EXCECOES), (
        f"a varredura cobre {cobertas} de {total} rotas; esperado ao menos "
        f"{total - len(EXCECOES)}"
    )


def test_todos_os_blueprints_esperados_estao_registrados(app):
    """
    A remoção do cadastro tirou um blueprint; nenhum outro pode sumir junto.

    `create_app` registra oito. Se um `register_blueprint` for removido por
    engano num merge, o módulo inteiro some da aplicação e só um teste de rota
    específica pegaria — este pega o desaparecimento em si.
    """
    esperados = {
        "main", "scan", "sobre", "ia_local", "logs", "modulos", "documentacao",
    }
    registrados = set(app.blueprints)

    faltando = esperados - registrados
    assert not faltando, f"blueprints ausentes de create_app(): {sorted(faltando)}"
    assert "cadastro" not in registrados, (
        "o blueprint de cadastro voltou — ele foi removido desta camada web de "
        "proposito; o cadastro vive apenas no modulo api_python"
    )
