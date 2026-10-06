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
Registro EXECUTÁVEL dos achados de auditoria — confirmados e refutados.

PROPÓSITO DE NEGÓCIO
--------------------
Uma auditoria produziu 41 achados confirmados neste módulo. Achado que vive só
em documento é reencontrado pela auditoria seguinte, rejulgado do zero e
esquecido de novo. Aqui cada achado vira teste.

COMO LER ESTE ARQUIVO
---------------------
Os defeitos **ainda não corrigidos** estão marcados `xfail(strict=True)` e
afirmam o comportamento **CORRETO**, não o atual. Consequência prática, e é o
ponto todo:

- enquanto o defeito existe, o teste falha → `xfail` → a suíte fica verde;
- no instante em que alguém corrigir, o teste passa → `XPASS` → e como o marcador
  é `strict`, **a suíte reprova**, obrigando a remover o marcador.

Ou seja: o registro não apodrece. Ele avisa sozinho quando deixa de ser verdade.

A seção final guarda os achados **REFUTADOS**, com o motivo e a medição. Sem ela,
a próxima auditoria reencontra o mesmo falso positivo e ninguém lembra que já foi
julgado.

MÉTODO
------
Todo achado aqui foi **reproduzido de forma independente** antes de ser
registrado; nenhum entrou por confiança no relatório. Os que não reproduziram
estão na seção de refutados, com a evidência da refutação.
"""

from __future__ import annotations

import gc
import json
import os

import pytest

from tests.conftest import RAIZ_MODULO

pytestmark = pytest.mark.regressao


# ═════════════════════════════════════════════════════════════════════════════
# CRÍTICOS
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.xfail(
    strict=True,
    reason="ACHADO CRITICO-1 · salvar_log_json nomeia o relatorio por SEGUNDO e "
           "grava direto no caminho final: dois scans que terminam no mesmo "
           "segundo produzem o mesmo nome e o ultimo sobrescreve o primeiro. "
           "Correcao: sufixo unico (job_id/uuid) + escrita atomica via "
           "os.replace(tmp, final).",
)
def test_dois_scans_no_mesmo_segundo_nao_se_sobrescrevem(sandbox_de_caminhos):
    """Cada execução de scan precisa produzir seu próprio arquivo."""
    from app.ui.scan_projeto.executar_scan import salvar_log_json

    primeiro = salvar_log_json({"projeto": "SCAN_A"})
    segundo = salvar_log_json({"projeto": "SCAN_B"})

    assert primeiro != segundo, (
        "os dois scans gravaram no MESMO arquivo — o primeiro relatorio se perdeu"
    )
    with open(primeiro, encoding="utf-8") as fh:
        assert json.load(fh)["projeto"] == "SCAN_A", "SCAN_A foi sobrescrito"


@pytest.mark.xfail(
    strict=True,
    reason="ACHADO CRITICO-2 · detectar_gpu_automatica()/obter_gpu_padrao() "
           "devolvem bool, mas _hardware_valido() faz valor.lower(). Numa "
           "maquina COM driver NVIDIA a deteccao devolve True e GET /ia-local/ "
           "estoura AttributeError -> HTTP 500. Numa maquina sem nvidia-smi "
           "devolve False e o bug fica invisivel — que e por que atravessou a "
           "suite. Correcao: devolver 'nvidia'/'amd' e blindar o tipo.",
)
def test_deteccao_de_gpu_devolve_o_contrato_que_a_rota_espera():
    """`obter_gpu_padrao()` tem de devolver a string que `_hardware_valido` lê."""
    from app.web.services.ia_local_service import obter_gpu_padrao

    valor = obter_gpu_padrao()
    assert isinstance(valor, str), (
        f"obter_gpu_padrao devolveu {type(valor).__name__} ({valor!r}); "
        "_hardware_valido() chama .lower() e vai estourar"
    )
    assert valor in {"amd", "nvidia"}


@pytest.mark.xfail(
    strict=True,
    reason="ACHADO CRITICO-2 (segunda metade) · _hardware_valido nao blinda o "
           "tipo da entrada. Correcao: valor = valor if isinstance(valor, str) "
           "else ''.",
)
@pytest.mark.parametrize("entrada", [True, 123, 3.5, [1], {"a": 1}])
def test_hardware_valido_nao_estoura_com_tipo_inesperado(entrada):
    """
    `_hardware_valido` precisa degradar para 'amd', nunca levantar.

    Só valores **truthy** entram na lista: o código é `(valor or "").lower()`,
    então `False`, `[]` e `{}` caem no `or ""` e passam. Parametrizar com eles
    faria o teste XPASSar e mascararia o defeito real, que é com valor truthy —
    exatamente o caso da máquina COM driver NVIDIA, onde a detecção devolve
    `True`.
    """
    from app.web.routes.ia_local_routes import _hardware_valido

    assert _hardware_valido(entrada) in {"amd", "nvidia"}


def test_hardware_valido_aceita_valores_falsy_sem_estourar():
    """
    Contraparte do teste acima, e passa hoje: valor falsy vira 'amd'.

    Fica registrado para que uma futura blindagem de tipo não quebre este
    caminho, que é o que mantém a página de pé em máquina sem GPU NVIDIA.
    """
    from app.web.routes.ia_local_routes import _hardware_valido

    for entrada in (False, None, "", [], {}, 0):
        assert _hardware_valido(entrada) == "amd", f"falhou com {entrada!r}"


@pytest.mark.xfail(
    strict=True,
    reason="ACHADO CRITICO-4 · app.py (raiz) sobe com host='0.0.0.0' e "
           "debug=True. O console interativo do Werkzeug fica exposto a toda a "
           "rede local: quem alcancar a porta 5000 executa Python no processo. "
           "Correcao: host='127.0.0.1' e debug controlado por variavel de "
           "ambiente, com o padrao em False.",
)
def test_entrypoint_nao_expoe_debugger_para_a_rede():
    """O entrypoint padrão não pode combinar `0.0.0.0` com `debug=True`."""
    with open(os.path.join(RAIZ_MODULO, "app.py"), encoding="utf-8") as fh:
        fonte = fh.read()

    expoe_rede = "0.0.0.0" in fonte
    debug_ligado = "debug=True" in fonte
    assert not (expoe_rede and debug_ligado), (
        "app.py combina host=0.0.0.0 com debug=True — console do Werkzeug "
        "acessivel por qualquer maquina da rede"
    )


# ═════════════════════════════════════════════════════════════════════════════
# ALTOS
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.xfail(
    strict=True,
    reason="ACHADO ALTO · got_request_exception.connect(registrar_excecao, app) "
           "usa o padrao weak=True do blinker, e `registrar_excecao` e funcao "
           "LOCAL de create_app(). Sem outra referencia forte, o receiver e "
           "coletado pelo GC assim que create_app retorna: NENHUMA excecao da "
           "web chega ao erro_sistema.log. Medido: receivers == 0. "
           "Correcao: connect(..., weak=False).",
)
def test_receiver_de_excecao_sobrevive_ao_garbage_collector():
    """O log de exceções da web precisa continuar ligado após `create_app()`."""
    from flask import got_request_exception

    from app.web.app import create_app

    create_app()
    gc.collect()

    assert len(got_request_exception.receivers) > 0, (
        "nenhum receiver ligado a got_request_exception — o erro_sistema.log "
        "nunca vai registrar um 500 da camada web"
    )


@pytest.mark.xfail(
    strict=True,
    reason="ACHADO ALTO · /documentacao/arquivo?file= confina a leitura a raiz "
           "do repositorio, mas a raiz INCLUI .git/. O arquivo .git/config "
           "guarda a URL do remoto e, em configuracoes com credencial "
           "embutida, o segredo. Servido com 200 sem autenticacao. "
           "Correcao: lista branca de extensao (imagem/pdf/svg) e recusa "
           "explicita de qualquer componente de caminho que comece com ponto.",
)
@pytest.mark.parametrize("alvo", [".git/config", ".git/HEAD", ".git/index"])
def test_metadados_do_git_nao_sao_servidos(client_producao, alvo):
    """`.git/` nunca pode sair pela rota de arquivo da documentação."""
    resposta = client_producao.get(
        "/documentacao/arquivo", query_string={"file": alvo}
    )
    assert resposta.status_code != 200, (
        f"serviu {alvo} com {len(resposta.data)} bytes"
    )


@pytest.mark.xfail(
    strict=True,
    reason="ACHADO ALTO · os quatro endpoints assincronos fazem "
           "(dados.get('caminho') or '').strip() sem checar o tipo. Um cliente "
           "HTTP que mande numero, booleano truthy, lista ou objeto no campo "
           "`caminho` provoca AttributeError e HTTP 500 — com o app.py subindo "
           "em debug=True, isso entrega o console do Werkzeug junto com o "
           "traceback. Medido em /scan, /ia-local (x2) e /modulos/containers. "
           "Correcao: recusar quando nao for str, com a mesma mensagem da "
           "recusa de caminho vazio.",
)
@pytest.mark.parametrize(
    "rota",
    [
        "/scan/executar-assincrono",
        "/ia-local/executar-assincrono",
        "/ia-local/cognitivo-assincrono",
        "/modulos/containers/executar-assincrono",
    ],
)
def test_endpoints_assincronos_recusam_caminho_nao_string(client_producao, rota):
    """Tipo inesperado no campo `caminho` deve virar recusa, não 500."""
    quebrou = []
    for valor in (123, 3.14, True, ["/tmp"], {"caminho": "/tmp"}):
        resposta = client_producao.post(rota, json={"caminho": valor})
        if resposta.status_code >= 500:
            quebrou.append((repr(valor), resposta.status_code))

    assert not quebrou, (
        f"{rota} devolveu 5xx com caminho nao-string: "
        + "; ".join(f"{v} -> {s}" for v, s in quebrou)
    )


@pytest.mark.xfail(
    strict=True,
    reason="ACHADO ALTO · ler_arquivo_log usa os.path.commonpath para confinar "
           "a leitura em logs/. No Windows, commonpath levanta ValueError "
           "('Paths don't have the same drive') quando os caminhos estao em "
           "unidades diferentes — a excecao nao e tratada e a rota devolve 500. "
           "Correcao: envolver em try/except ValueError e tratar como recusa.",
)
def test_logs_ver_com_caminho_em_outro_drive_nao_derruba_a_rota(
    client_producao, sandbox_de_caminhos
):
    """
    Caminho absoluto em outra unidade deve ser recusado, não derrubar.

    ATENÇÃO ao montar o vetor: `commonpath` só levanta quando as unidades
    DIFEREM. O sandbox dos testes fica em `%TEMP%` (unidade C:), então
    `C:\\Windows\\win.ini` **compartilha** a unidade e o defeito não aparece —
    foi assim que a primeira versão deste teste passou por engano. A unidade do
    vetor é derivada da unidade do sandbox para garantir que sejam diferentes.
    """
    unidade_sandbox = os.path.splitdrive(str(sandbox_de_caminhos))[0].upper()
    outra = "Z:" if unidade_sandbox != "Z:" else "Y:"

    resposta = client_producao.get("/logs/ver/" + outra + "\\qualquer\\arquivo.log")
    assert resposta.status_code < 500, (
        f"HTTP {resposta.status_code}: ValueError nao tratado em "
        f"os.path.commonpath (sandbox em {unidade_sandbox}, vetor em {outra})"
    )


def test_nenhum_teste_da_suite_fica_sem_assert():
    """
    Varre a suíte à procura de função `test_*` sem nenhuma asserção.

    ACHADO ALTO — **já corrigido.** `tests/test_log_paths.py::test_logs` não
    tinha nenhum assert: imprimia `✅`/`❌` e passava sempre, inclusive com os
    logs ausentes e com a função de caminho quebrada. Foi reescrito.

    Este teste nasceu marcado `xfail(strict=True)`; ao ser corrigido ele passou,
    o `strict` reprovou a suíte e obrigou a remover o marcador — que é o
    mecanismo deste arquivo funcionando. Fica agora como guarda permanente
    contra a classe de falha voltar em QUALQUER teste.

    Teste sem assert é o pior dos instrumentos: conta como cobertura, fica verde
    para sempre e não pode reprovar nem quando tudo está quebrado.
    """
    import ast

    sem_assert = []
    raiz_testes = os.path.join(RAIZ_MODULO, "tests")

    for pasta, dirs, arquivos in os.walk(raiz_testes):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for nome in arquivos:
            if not (nome.startswith("test_") and nome.endswith(".py")):
                continue
            caminho = os.path.join(pasta, nome)
            with open(caminho, encoding="utf-8") as fh:
                arvore = ast.parse(fh.read(), filename=caminho)

            for no in ast.walk(arvore):
                if not isinstance(no, ast.FunctionDef):
                    continue
                if not no.name.startswith("test_"):
                    continue
                tem_assert = any(
                    isinstance(interno, (ast.Assert, ast.Raise))
                    for interno in ast.walk(no)
                )
                # `pytest.raises` e `pytest.fail` também são verificação válida.
                usa_pytest = any(
                    isinstance(interno, ast.Attribute)
                    and interno.attr in {"raises", "fail", "warns", "approx"}
                    for interno in ast.walk(no)
                )
                if not tem_assert and not usa_pytest:
                    rel = os.path.relpath(caminho, RAIZ_MODULO)
                    sem_assert.append(f"{rel}::{no.name}")

    assert not sem_assert, (
        "Testes SEM nenhuma asseracao (passam sempre, nao provam nada):\n  "
        + "\n  ".join(sem_assert)
    )


# ═════════════════════════════════════════════════════════════════════════════
# ACHADOS REFUTADOS — registrados para a próxima auditoria não reencontrá-los
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.xfail(
    strict=True,
    reason="ACHADO ALTO · um unico relatorio ilegivel na pasta derruba a "
           "listagem /scan/logs inteira com HTTP 500 "
           "(jinja2.UndefinedError: 'dict object' has no attribute "
           "'score_risco'). O arquivo ruim e parseado para um dicionario "
           "incompleto que segue para o template. Um relatorio interrompido no "
           "meio da gravacao — o que o ACHADO CRITICO-1 torna provavel — deixa "
           "a tela de relatorios inacessivel. Correcao: descartar entrada sem "
           "as chaves obrigatorias na montagem da lista, ou usar acesso "
           "tolerante no template.",
)
def test_relatorio_ilegivel_nao_derruba_a_listagem(client_producao, sandbox_de_caminhos):
    """
    Um relatório corrompido não pode tornar a tela inteira inacessível.

    NOTA DE MÉTODO — este achado eu **refutei por engano** numa primeira
    medição, e o erro vale registro. Meu script ad-hoc repontava o `__file__` do
    `scan_service`, mas `obter_diretorio_logs()` é definida em
    `app.ui.scan_projeto.listar_falhas` e importada de lá. O script continuou
    lendo a pasta REAL de relatórios, cheia de arquivos válidos, e devolveu 200.
    O "200" não era prova de tratamento: era o instrumento apontado para o
    diretório errado. Dentro do sandbox correto do `conftest.py`, a rota
    devolve 500.
    """
    pasta = sandbox_de_caminhos / "logs" / "generic" / "reports"
    pasta.mkdir(parents=True, exist_ok=True)

    quebrou = []
    for conteudo in ('{"truncado": ', '["lista", "nao", "dict"]', "", "nao e json"):
        (pasta / "report_20260101_000000.json").write_text(conteudo, encoding="utf-8")
        resposta = client_producao.get("/scan/logs?secao=scan")
        if resposta.status_code >= 500:
            quebrou.append((conteudo[:24], resposta.status_code))

    assert not quebrou, (
        "relatorio ilegivel derrubou a listagem: "
        + "; ".join(f"{c!r} -> {s}" for c, s in quebrou)
    )


def test_refutado_scan_logs_sistema_confina_corretamente(client_producao, payloads_traversal):
    """
    REFUTADO · "/scan/logs/sistema/<path> derruba com ValueError em commonpath".

    Medição própria: os 10 vetores de traversal, incluindo `C:\\Windows\\win.ini`
    em outra unidade, devolveram 302 (recusa por redirecionamento). A rota irmã
    `/logs/ver/` **de fato** cai — essa continua registrada como confirmada
    acima. O defeito não é da mesma classe nas duas rotas.
    """
    for vetor in payloads_traversal:
        resposta = client_producao.get("/scan/logs/sistema/" + vetor)
        assert resposta.status_code < 500, (
            f"{vetor!r} derrubou /scan/logs/sistema com {resposta.status_code}"
        )
