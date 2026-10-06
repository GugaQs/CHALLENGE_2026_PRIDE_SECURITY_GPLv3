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
Filtros avançados de relatório de scan.

PROPÓSITO DE NEGÓCIO
--------------------
Um relatório de scan traz centenas de falhas. Quem vai corrigir precisa reduzir
a lista ao que importa: só as críticas, só num arquivo, só num intervalo de
linhas. Esse recorte vira um `report_filtrado_*.json` que a equipe usa como
lista de trabalho — se o filtro errar, a correção acontece no lugar errado ou
uma falha crítica fica de fora sem ninguém notar.

Era o módulo com a menor cobertura da camada web (13%).

INVARIANTES DO DOMÍNIO
----------------------
- INV-FLT-001 · Campo vazio no formulário **não** vira filtro; se virasse, o
  formulário em branco devolveria zero falhas em vez de todas.
- INV-FLT-002 · Filtro de linha aceita apenas dígito. Texto no campo é ignorado,
  nunca vira `int()` que estoura no meio da requisição.
- INV-FLT-003 · Filtrar é sempre um subconjunto: nenhuma falha nova aparece.
- INV-FLT-004 · Relatório inexistente devolve recusa, não exceção.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha aqui produz lista de trabalho errada — o defeito mais caro deste módulo,
porque parece que funcionou.
"""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.unidade


class FormularioFalso(dict):
    """Imita `request.form`: `.get(chave)` devolvendo None para ausente."""


# ── INV-FLT-001 · Campo vazio não vira filtro ────────────────────────────────

def test_formulario_em_branco_nao_produz_nenhum_filtro():
    """
    Formulário vazio precisa significar "sem filtro", nunca "filtro vazio".

    Se `""` virasse `{"tipo": {""}}`, o formulário em branco devolveria zero
    falhas — e o operador concluiria que o projeto está limpo.
    """
    from app.web.services.scan_filtro_service import montar_filtros_do_formulario

    for vazio in ({}, {"tipo": "", "severidade": "   ", "linha_min": ""}):
        assert montar_filtros_do_formulario(FormularioFalso(vazio)) == {}


def test_campos_preenchidos_viram_filtros_no_formato_do_motor():
    """Texto vira conjunto; substring vira string; linha vira inteiro."""
    from app.web.services.scan_filtro_service import montar_filtros_do_formulario

    filtros = montar_filtros_do_formulario(FormularioFalso({
        "tipo": "SQL Injection Provavel",
        "severidade": "CRÍTICO",
        "confianca": "ALTA",
        "arquivo_contem": "service",
        "codigo_contem": "SELECT",
        "linha_min": "10",
        "linha_max": "200",
    }))

    assert filtros["tipo"] == {"SQL Injection Provavel"}
    assert filtros["severidade"] == {"CRÍTICO"}
    assert filtros["confianca"] == {"ALTA"}
    assert filtros["arquivo_contem"] == "service"
    assert filtros["codigo_contem"] == "SELECT"
    assert filtros["linha_min"] == 10 and isinstance(filtros["linha_min"], int)
    assert filtros["linha_max"] == 200


def test_espacos_em_volta_do_valor_sao_removidos():
    """Copiar e colar de outra tela traz espaço; ele não pode virar filtro."""
    from app.web.services.scan_filtro_service import montar_filtros_do_formulario

    filtros = montar_filtros_do_formulario(FormularioFalso({
        "tipo": "  RCE  ", "arquivo_contem": "  app.py  ",
    }))
    assert filtros["tipo"] == {"RCE"}
    assert filtros["arquivo_contem"] == "app.py"


# ── INV-FLT-002 · Linha só aceita dígito ─────────────────────────────────────

@pytest.mark.parametrize(
    "valor", ["abc", "-5", "1.5", "1e3", " ", "10a", "+7", "0x10", "", "  12  x"]
)
def test_linha_nao_numerica_e_ignorada_em_vez_de_estourar(valor):
    """
    `isdigit()` é o portão antes do `int()`.

    Sem ele, `int("abc")` levantaria ValueError no meio do POST de filtro e a
    tela devolveria 500 para quem digitou errado — erro de boa-fé clássico.
    """
    from app.web.services.scan_filtro_service import montar_filtros_do_formulario

    filtros = montar_filtros_do_formulario(
        FormularioFalso({"linha_min": valor, "linha_max": valor})
    )
    assert "linha_min" not in filtros, f"{valor!r} virou filtro de linha"
    assert "linha_max" not in filtros


def test_digito_unicode_e_aceito_como_numero():
    """
    `"٣".isdigit()` é True e `int("٣")` devolve 3 — comportamento do Python.

    Descoberto ao escrever o teste acima, que inicialmente listava `٣` como
    "não numérico" e reprovou. **O código estava certo e o teste errado.** Fica
    registrado porque é contraintuitivo: colar um algarismo indo-arábico no
    campo de linha produz um filtro válido, não um erro.
    """
    from app.web.services.scan_filtro_service import montar_filtros_do_formulario

    filtros = montar_filtros_do_formulario(FormularioFalso({"linha_min": "٣"}))
    assert filtros["linha_min"] == 3


def test_linha_negativa_e_recusada_porque_nao_e_digito():
    """
    `"-5".isdigit()` é False, então o negativo é descartado.

    Documenta o comportamento: número de linha negativo não existe, e ignorar é
    a resposta certa. Se um dia `isdigit` for trocado por `lstrip('-').isdigit()`
    isto avisa da mudança de semântica.
    """
    from app.web.services.scan_filtro_service import montar_filtros_do_formulario

    assert "linha_min" not in montar_filtros_do_formulario(
        FormularioFalso({"linha_min": "-5"})
    )


# ── INV-FLT-003 e 004 · Aplicação sobre relatório real ───────────────────────

@pytest.fixture
def relatorio_com_falhas(sandbox_de_caminhos):
    """Grava no sandbox um relatório com falhas de severidades variadas."""
    pasta = sandbox_de_caminhos / "logs" / "generic" / "reports"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / "report_20260101_010101.json"
    caminho.write_text(json.dumps({
        "projeto": "amostra",
        "data_scan": "01/01/2026 | 01:01:01",
        "total_arquivos": 3,
        "total_vulnerabilidades": 4,
        "vulnerabilidades": [
            {"arquivo": "a_service.py", "linha": 10, "tipo": "SQL Injection Provavel",
             "severidade": "CRÍTICO", "confianca": "ALTA", "trecho": "SELECT 1"},
            {"arquivo": "b_utils.py", "linha": 50, "tipo": "Execução de Risco (RCE)",
             "severidade": "ALTO", "confianca": "MEDIA", "trecho": "os.system(x)"},
            {"arquivo": "c_view.js", "linha": 120, "tipo": "XSS (Cross-Site Scripting)",
             "severidade": "MÉDIO", "confianca": "BAIXA", "trecho": "innerHTML"},
            {"arquivo": "a_service.py", "linha": 300, "tipo": "Credenciais Hardcoded",
             "severidade": "CRÍTICO", "confianca": "ALTA", "trecho": "senha = 'x'"},
        ],
    }, ensure_ascii=False), encoding="utf-8")
    return caminho.name


def test_opcoes_do_formulario_saem_do_relatorio_sem_repetir(relatorio_com_falhas):
    """Os selects mostram cada valor uma vez, em ordem estável."""
    from app.web.services.scan_filtro_service import obter_opcoes_filtro

    opcoes = obter_opcoes_filtro(relatorio_com_falhas)

    assert opcoes["severidades"] == sorted({"CRÍTICO", "ALTO", "MÉDIO"})
    assert len(opcoes["tipos"]) == 4, opcoes["tipos"]
    assert opcoes["confiancas"] == sorted({"ALTA", "MEDIA", "BAIXA"})
    for chave in opcoes:
        assert len(opcoes[chave]) == len(set(opcoes[chave])), f"{chave} repetiu"


def test_opcoes_de_relatorio_inexistente_vem_vazias_sem_estourar():
    """INV-FLT-004 · nome inexistente devolve estrutura vazia, não exceção."""
    from app.web.services.scan_filtro_service import obter_opcoes_filtro

    opcoes = obter_opcoes_filtro("nao_existe_12345.json")
    assert opcoes == {"tipos": [], "severidades": [], "confiancas": []}


def test_filtro_por_severidade_devolve_subconjunto(relatorio_com_falhas):
    """INV-FLT-003 · filtrar reduz; nunca inventa falha."""
    from app.web.services.scan_filtro_service import aplicar_filtro_relatorio

    ok, mensagem, nome_novo, ranking = aplicar_filtro_relatorio(
        relatorio_com_falhas, {"severidade": {"CRÍTICO"}}
    )

    assert ok is True, mensagem
    assert nome_novo and nome_novo.endswith(".json")
    assert "2 falhas" in mensagem, mensagem
    assert ranking, "o ranking de arquivos criticos veio vazio"


def test_filtro_sem_correspondencia_recusa_com_mensagem(relatorio_com_falhas):
    """
    Zero resultado é recusa explícita, não arquivo vazio no disco.

    Gerar um `report_filtrado_*.json` sem nenhuma falha encheria a pasta de
    relatórios inúteis e faria o operador achar que o filtro funcionou.
    """
    from app.web.services.scan_filtro_service import aplicar_filtro_relatorio

    ok, mensagem, nome_novo, ranking = aplicar_filtro_relatorio(
        relatorio_com_falhas, {"severidade": {"INEXISTENTE"}}
    )

    assert ok is False
    assert nome_novo is None, "nao pode gravar arquivo quando nada corresponde"
    assert ranking == []
    assert mensagem, "recusa sem mensagem"


def test_filtro_sobre_relatorio_inexistente_recusa(sandbox_de_caminhos):
    """INV-FLT-004 · aplicar filtro em relatório que sumiu é recusa educada."""
    from app.web.services.scan_filtro_service import aplicar_filtro_relatorio

    ok, mensagem, nome_novo, ranking = aplicar_filtro_relatorio(
        "sumiu_12345.json", {"severidade": {"CRÍTICO"}}
    )

    assert ok is False
    assert nome_novo is None
    assert ranking == []
    assert mensagem


def test_agrupamento_por_campo_soma_o_total_das_falhas(relatorio_com_falhas):
    """Agrupar por arquivo tem de conservar a contagem total."""
    from app.web.services.scan_filtro_service import obter_agrupamentos

    grupos = obter_agrupamentos(relatorio_com_falhas, "arquivo")

    assert grupos, "agrupamento veio vazio"
    total = sum(
        len(v) if isinstance(v, list) else v for v in grupos.values()
    )
    assert total == 4, f"a soma dos grupos ({total}) difere das 4 falhas"


def test_agrupamento_de_relatorio_inexistente_vem_vazio():
    """Nome inexistente devolve dicionário vazio, não exceção."""
    from app.web.services.scan_filtro_service import obter_agrupamentos

    assert obter_agrupamentos("sumiu_12345.json", "arquivo") == {}


def test_agrupamento_por_campo_inexistente_nao_estoura(relatorio_com_falhas):
    """Campo que nenhuma falha possui: agrupa em vazio, sem levantar."""
    from app.web.services.scan_filtro_service import obter_agrupamentos

    resultado = obter_agrupamentos(relatorio_com_falhas, "campo_que_nao_existe")
    assert isinstance(resultado, dict)
