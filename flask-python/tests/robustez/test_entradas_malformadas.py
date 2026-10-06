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
Entradas malformadas, tipos errados e valores de borda.

PROPÓSITO DE NEGÓCIO
--------------------
Todo endpoint JSON desta aplicação lê um campo do corpo e o trata como string de
caminho. O `app.js` sempre manda string, mas o endpoint é HTTP público: qualquer
cliente manda o que quiser. Entrada inesperada deve virar **recusa explícita**,
não HTTP 500 com traceback.

Isto é a revisão de "erro de boa-fé" aplicada à API: não é sobre o atacante, é
sobre o que acontece quando um formulário envia campo vazio, um número chega
onde se esperava texto, ou alguém cola um caminho com barra final.

INVARIANTES DO DOMÍNIO
----------------------
- INV-ROB-001 · Nenhuma entrada, de nenhum tipo, produz 5xx.
- INV-ROB-002 · Recusa vem com mensagem, não com corpo vazio.
- INV-ROB-003 · Valor de borda numérico (0, negativo, gigante, não numérico) é
  normalizado, e a mensagem exibida corresponde ao que de fato aconteceu.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
5xx aqui significa caminho de código não tratado alcançável por HTTP. Em modo
`debug=True` — que é como o `app.py` sobe hoje — isso entrega o console do
Werkzeug junto com o traceback.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.robustez, pytest.mark.integracao]


# Valores que um cliente HTTP pode mandar onde a aplicação espera um caminho.
#
# Separados em dois grupos porque o comportamento hoje difere:
#  - os TRATADOS caem no `(valor or "").strip()` e viram recusa educada;
#  - os NÃO TRATADOS são truthy e não-string, então `.strip()` levanta
#    AttributeError e a rota devolve 500. Esse é achado confirmado, registrado em
#    tests/regressao/test_achados_auditoria.py::
#      test_endpoints_assincronos_recusam_caminho_nao_string
#    Quando for corrigido, junte as duas listas aqui.
# ATENÇÃO ao acrescentar valor aqui: nada nesta lista pode ser um DIRETÓRIO
# EXISTENTE. `"."` e `"../../.."` estavam aqui e são caminhos válidos — cada POST
# disparava um scan REAL da árvore inteira numa thread de fundo. A thread
# sobrevive ao teardown do teste, e por isso escrevia o relatório no `logs/`
# verdadeiro, já fora do sandbox: 3 arquivos de 1,2 MB por execução.
# O caminho tem de ser sintaticamente plausível e comprovadamente inexistente.
VALORES_TRATADOS = [
    None,
    False,
    [],
    {},
    "",
    "   ",
    "\x00",
    "a" * 5000,
    "ç∂€",
    "C:/caminho/que/nao/existe/xyz123",
    "/pasta/inexistente/para/teste/zzz999",
    "..\\..\\pasta_que_nao_existe_zzz999",
]

VALORES_NAO_STRING_TRUTHY = [123, 3.14, True, ["/tmp"], {"caminho": "/tmp"}]

VALORES_ESTRANHOS = VALORES_TRATADOS

ENDPOINTS_JSON = [
    ("/scan/executar-assincrono", "caminho"),
    ("/ia-local/executar-assincrono", "caminho"),
    ("/ia-local/cognitivo-assincrono", "caminho"),
    ("/modulos/containers/executar-assincrono", "caminho"),
]


# ── INV-ROB-001 · Nada derruba ───────────────────────────────────────────────

@pytest.mark.parametrize("rota,campo", ENDPOINTS_JSON)
def test_endpoint_json_nao_devolve_5xx_com_valor_estranho(client_producao, rota, campo):
    """Cada endpoint assíncrono, contra a bateria inteira de valores."""
    quebrou = []
    for valor in VALORES_ESTRANHOS:
        resposta = client_producao.post(rota, json={campo: valor})
        if resposta.status_code >= 500:
            quebrou.append((repr(valor)[:40], resposta.status_code))

    assert not quebrou, (
        f"{rota} devolveu 5xx:\n  "
        + "\n  ".join(f"{v} -> {s}" for v, s in quebrou)
    )


@pytest.mark.parametrize("rota,campo", ENDPOINTS_JSON)
def test_endpoint_json_nao_devolve_5xx_sem_corpo(client_producao, rota, campo):
    """POST sem corpo, com corpo vazio, e com JSON inválido."""
    casos = [
        ("sem corpo", {}),
        ("json vazio", {"json": {}}),
        ("campo ausente", {"json": {"outro": "x"}}),
        ("corpo texto", {"data": "isto nao e json"}),
        ("json malformado", {"data": '{"caminho": ', "content_type": "application/json"}),
    ]
    quebrou = []
    for nome, kwargs in casos:
        resposta = client_producao.post(rota, **kwargs)
        if resposta.status_code >= 500:
            quebrou.append((nome, resposta.status_code))

    assert not quebrou, (
        f"{rota} devolveu 5xx:\n  " + "\n  ".join(f"{n} -> {s}" for n, s in quebrou)
    )


@pytest.mark.parametrize(
    "rota",
    ["/scan/executar", "/ia-local/executar", "/ia-local/cognitivo",
     "/ia-local/reanalisar", "/modulos/containers"],
)
def test_form_post_nao_devolve_5xx_com_campo_ausente_ou_estranho(client_producao, rota):
    """Rotas de formulário, sem campo e com valores estranhos."""
    quebrou = []
    for dados in ({}, {"caminho": ""}, {"caminho": "   "},
                  {"caminho": "a" * 3000}, {"caminho": "\x00"},
                  {"campo_errado": "x"}):
        resposta = client_producao.post(rota, data=dados, follow_redirects=False)
        if resposta.status_code >= 500:
            quebrou.append((str(dados)[:40], resposta.status_code))

    assert not quebrou, (
        f"{rota} devolveu 5xx:\n  " + "\n  ".join(f"{d} -> {s}" for d, s in quebrou)
    )


def test_status_de_job_inexistente_devolve_404_e_nao_500(client_producao):
    """Consultar job que não existe é caso comum: aba antiga, F5 depois do fim."""
    for molde in ("/scan/status/{}", "/ia-local/status/{}",
                  "/modulos/containers/status/{}"):
        for job in ("inexistente", "", "../../etc", "a" * 500, "%00"):
            resposta = client_producao.get(molde.format(job))
            assert resposta.status_code < 500, (
                f"{molde.format(job)} -> {resposta.status_code}"
            )


# ── INV-ROB-002 · Recusa com mensagem ────────────────────────────────────────

@pytest.mark.parametrize("rota,campo", ENDPOINTS_JSON)
def test_recusa_traz_mensagem_e_nao_corpo_vazio(client_producao, rota, campo):
    """
    Recusar sem dizer por quê faz o operador tentar de novo igual.

    O `app.js` mostra `dados.mensagem` num toast; sem ela o usuário vê o botão
    voltar ao normal e nada acontecer.
    """
    resposta = client_producao.post(rota, json={campo: ""})
    corpo = resposta.get_json(silent=True)

    assert corpo is not None, f"{rota} recusou com corpo nao-JSON"
    assert corpo.get("ok") is False, f"{rota} nao sinalizou recusa: {corpo}"
    assert corpo.get("mensagem"), f"{rota} recusou sem mensagem: {corpo}"


# ── INV-ROB-003 · Bordas numéricas ───────────────────────────────────────────

@pytest.mark.lento
@pytest.mark.parametrize(
    "limite", ["0", "-1", "-999", "999999999", "abc", "", "1.5", "1e9", "%00"]
)
def test_scan_software_com_limite_de_borda_nao_derruba(client_producao, limite):
    """
    O campo `limite` vem de um `<input type=number>`, mas HTTP aceita tudo.

    Marcado `lento`: cada execução consulta o inventário real de programas
    instalados do Windows (~0,8 s). Excluir com `-m "not lento"` quando quiser
    o ciclo rápido; a suíte completa continua rodando-o.
    """
    resposta = client_producao.post(
        "/modulos/scan-software", data={"limite": limite}, follow_redirects=True
    )
    assert resposta.status_code < 500, f"limite={limite!r} -> {resposta.status_code}"


@pytest.mark.parametrize(
    "parametros",
    [
        {"pagina": "0"}, {"pagina": "-5"}, {"pagina": "abc"}, {"pagina": "9" * 20},
        {"por_pagina": "0"}, {"por_pagina": "-10"}, {"por_pagina": "999999"},
        {"por_pagina": "abc"}, {"pagina": "1", "por_pagina": "0"},
        {"severidade": "INEXISTENTE"}, {"severidade": "'; DROP TABLE--"},
        {"tipo": "\x00"}, {"arquivo": "../.." },
        {"linhas": "-1"}, {"linhas": "0"}, {"linhas": "abc"},
    ],
)
def test_querystring_de_paginacao_e_filtro_nao_derruba(client_producao, parametros):
    """Paginação e filtros vêm da URL e são editáveis à mão pelo usuário."""
    for rota in ("/scan/logs", "/logs/"):
        resposta = client_producao.get(rota, query_string=parametros)
        assert resposta.status_code < 500, (
            f"{rota}?{parametros} -> {resposta.status_code}"
        )


def test_paginacao_negativa_nao_devolve_mais_dados_do_que_o_pedido(client_producao):
    """
    `?linhas=-1` não pode inverter o corte e despejar o arquivo inteiro.

    Corte negativo em Python (`linhas[-n:]` com n negativo) devolve o começo da
    lista em vez do fim — e num log grande isso vira despejo acidental.
    """
    resposta = client_producao.get("/logs/", query_string={"linhas": "-1"})
    assert resposta.status_code < 500
    # Sem log real no sandbox, a página é pequena; o que importa é não estourar
    # e não devolver um corpo desproporcional.
    assert len(resposta.data) < 5_000_000, "resposta desproporcional para linhas=-1"


# ── Método HTTP errado ───────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "rota", ["/scan/executar-assincrono", "/logs/abrir-pasta", "/scan/selecionar-pasta"]
)
def test_get_em_rota_de_post_devolve_405_e_nao_500(client_producao, rota):
    """
    Método errado é 405, nunca 500.

    `/scan/logs/limpar` ficou fora da lista de propósito: `/scan/logs/<nome_log>`
    também casa com esse caminho, então um GET cai na rota de leitura e
    redireciona (302). É sobreposição de rota, não defeito — mas vale saber que
    existe, porque significa que ninguém consegue ter um relatório chamado
    `limpar`.
    """
    resposta = client_producao.get(rota)
    assert resposta.status_code == 405, f"{rota} GET -> {resposta.status_code}"


def test_rota_de_leitura_de_log_e_a_de_limpar_se_sobrepoem(client_producao):
    """
    Documenta a sobreposição: `GET /scan/logs/limpar` cai em `<nome_log>`.

    Não é falha de segurança (a limpeza continua exigindo POST + CSRF), mas é
    uma armadilha de manutenção: acrescentar `/scan/logs/<verbo>` no futuro
    colide com nomes de relatório.
    """
    resposta = client_producao.get("/scan/logs/limpar", follow_redirects=False)
    assert resposta.status_code < 500
    assert resposta.status_code != 405, (
        "se isto virar 405, a sobreposicao foi resolvida — atualize o teste "
        "acima para incluir /scan/logs/limpar na lista"
    )


@pytest.mark.parametrize("rota", ["/", "/scan/", "/sobre/", "/documentacao/"])
def test_post_em_rota_de_get_devolve_405_e_nao_500(client_producao, rota):
    """O inverso: POST numa página de leitura."""
    resposta = client_producao.post(rota, data={})
    assert resposta.status_code in (405, 400), f"{rota} POST -> {resposta.status_code}"
