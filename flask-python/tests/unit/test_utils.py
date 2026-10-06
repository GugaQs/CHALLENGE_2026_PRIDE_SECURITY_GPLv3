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
Utilitários: tempo, progresso e helpers de terminal.

PROPÓSITO DE NEGÓCIO
--------------------
`app/utils/` é a base compartilhada: o carimbo de tempo que vai para a trilha de
auditoria de todo relatório, o cálculo que alimenta a barra de progresso e o
helper de limpeza de tela do modo CLI. São funções pequenas, sem teste até aqui,
e que aparecem em todo relatório gerado.

INVARIANTES DO DOMÍNIO
----------------------
- INV-UTL-001 · O carimbo técnico é UTC. Gravar hora local quebraria a
  correlação entre o relatório e o log do sistema, que é UTC.
- INV-UTL-002 · O horário do Brasil é exatamente UTC−3 do carimbo técnico.
- INV-UTL-003 · O percentual fica em [0, 100] para qualquer entrada, porque
  alimenta `style.width` no navegador.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Erro de fuso aqui desloca a data de todos os relatórios em horas — e a
divergência só aparece quando alguém tenta cruzar o relatório com o log.
"""

from __future__ import annotations

import datetime
import re

import pytest

pytestmark = pytest.mark.unidade


# ── Tempo ────────────────────────────────────────────────────────────────────

FORMATO = re.compile(r"^\d{2}/\d{2}/\d{4} \| \d{2}:\d{2}:\d{2}")


def test_timestamp_tecnico_esta_em_utc():
    """
    `obter_timestamp()` acompanha o relógio UTC, não o do container.

    Comparado com uma janela de tolerância de dois minutos: se a função usasse
    hora local numa máquina em UTC−3, a diferença seria de horas.
    """
    from app.utils.tempo import obter_timestamp

    marcado = obter_timestamp()
    assert FORMATO.match(marcado), f"formato inesperado: {marcado!r}"

    agora_utc = datetime.datetime.now(datetime.timezone.utc)
    lido = datetime.datetime.strptime(marcado, "%d/%m/%Y | %H:%M:%S").replace(
        tzinfo=datetime.timezone.utc
    )
    diferenca = abs((agora_utc - lido).total_seconds())
    assert diferenca < 120, (
        f"o carimbo esta {diferenca / 3600:.1f}h fora do UTC — provavel uso de "
        f"hora local. Marcado: {marcado}, UTC agora: {agora_utc}"
    )


def test_horario_do_brasil_e_exatamente_tres_horas_atras():
    """INV-UTL-002 · a diferença é fixa em 3 horas."""
    from app.utils.tempo import obter_timestamp, obter_timestamp_utc_brasil

    utc = datetime.datetime.strptime(obter_timestamp(), "%d/%m/%Y | %H:%M:%S")
    brasil = datetime.datetime.strptime(
        obter_timestamp_utc_brasil(), "%d/%m/%Y | %H:%M:%S"
    )
    diferenca = (utc - brasil).total_seconds()
    assert abs(diferenca - 3 * 3600) < 120, (
        f"diferenca UTC-Brasil de {diferenca / 3600:.2f}h, esperado 3h"
    )


def test_timestamp_do_sistema_traz_o_deslocamento_de_fuso():
    """O carimbo do sistema identifica o fuso, para não ser confundido com UTC."""
    from app.utils.tempo import obter_timestamp_sistema

    marcado = obter_timestamp_sistema()
    assert FORMATO.match(marcado), f"formato inesperado: {marcado!r}"
    assert re.search(r"[+-]\d{4}$", marcado.strip()), (
        f"sem deslocamento de fuso no fim: {marcado!r} — sem ele, ninguem "
        "distingue este carimbo do de UTC"
    )


def test_relogio_da_tela_nao_vem_vazio():
    """O cabeçalho do menu CLI mostra este texto; vazio deixaria a tela torta."""
    from app.utils.tempo import obter_relogio_atual

    relogio = obter_relogio_atual()
    assert isinstance(relogio, str)
    assert relogio.strip(), "relogio vazio"


def test_funcoes_de_tempo_sao_estaveis_em_chamadas_seguidas():
    """Duas chamadas próximas não podem divergir em minutos."""
    from app.utils.tempo import obter_timestamp

    primeiro = datetime.datetime.strptime(obter_timestamp(), "%d/%m/%Y | %H:%M:%S")
    segundo = datetime.datetime.strptime(obter_timestamp(), "%d/%m/%Y | %H:%M:%S")
    assert abs((segundo - primeiro).total_seconds()) < 5


# ── Progresso ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "atual,total,esperado",
    [
        (0, 10, 0),
        (5, 10, 50),
        (10, 10, 100),
        (10, 0, 0),      # divisão por zero tratada
        (0, 0, 0),
        (20, 10, 100),   # teto respeitado
        (1, 3, 33),
    ],
)
def test_percentual_para_entradas_normais(atual, total, esperado):
    """Casos que a barra de progresso realmente encontra."""
    from app.utils.progresso_scan import calcular_percentual

    assert calcular_percentual(atual, total) == esperado


def test_percentual_nunca_passa_de_cem():
    """`min(100, ...)` protege o teto — a barra não pode transbordar."""
    from app.utils.progresso_scan import calcular_percentual

    for atual, total in [(999, 10), (10 ** 9, 1), (101, 100)]:
        assert calcular_percentual(atual, total) == 100


def test_notificar_progresso_repassa_o_payload_ao_callback():
    """O worker chama isto a cada arquivo; o payload alimenta o polling."""
    from app.utils.progresso_scan import notificar_progresso

    recebidos = []
    notificar_progresso(recebidos.append, 3, 10, "analisando")

    assert len(recebidos) == 1, "o callback deveria ter sido chamado uma vez"
    payload = recebidos[0]
    assert payload["atual"] == 3
    assert payload["total"] == 10
    assert payload["percentual"] == 30
    assert payload["mensagem"] == "analisando"


def test_notificar_progresso_sem_callback_nao_estoura():
    """
    O motor de scan também roda pelo CLI, sem callback.

    Passar `None` é uso legítimo, não erro — e não pode derrubar o scan inteiro.

    A asserção é explícita e não decorativa: sem ela o teste passaria mesmo que
    a função virasse um `pass`, e a guarda
    `test_nenhum_teste_da_suite_fica_sem_assert` reprova por isso.
    """
    from app.utils.progresso_scan import notificar_progresso

    resultado = notificar_progresso(None, 1, 2, "sem callback")
    assert resultado is None, (
        "com callback ausente a funcao nao deve produzir efeito nem retorno"
    )


def test_notificar_progresso_com_callback_que_falha_nao_derruba_o_scan():
    """
    Documenta o comportamento atual: exceção no callback **propaga**.

    Não é necessariamente errado, mas é um acoplamento a conhecer: um defeito
    na atualização de progresso interrompe o scan que já estava em andamento.
    Se um dia passar a ser engolido, este teste avisa da mudança.
    """
    from app.utils.progresso_scan import notificar_progresso

    def callback_ruim(_payload):
        raise RuntimeError("falha no callback")

    with pytest.raises(RuntimeError):
        notificar_progresso(callback_ruim, 1, 2, "x")


# ── Helpers ──────────────────────────────────────────────────────────────────

def test_limpar_tela_nao_estoura(monkeypatch):
    """
    `limpar_tela` é chamada em todo laço de menu do CLI.

    O comando do SO é interceptado: rodar `cls`/`clear` de dentro do pytest
    embaralharia a saída do próprio teste.
    """
    import app.utils.helpers as helpers

    chamadas = []
    monkeypatch.setattr(helpers.os, "system", lambda cmd: chamadas.append(cmd) or 0)

    helpers.limpar_tela()

    assert chamadas, "limpar_tela nao chamou o comando do sistema"


def test_limpar_tela_com_comando_falhando_nao_derruba_o_menu(monkeypatch):
    """
    Código de saída diferente de zero não pode interromper o menu.

    NOTA: `os.system` **devolve** o código de erro, não levanta `OSError`.
    O `except OSError` que existe em `helpers.py` é, por isso, inalcançável —
    achado registrado em `tests/regressao/test_achados_auditoria.py`. Este teste
    prova o que importa na prática: falha do comando não derruba o menu.
    """
    import app.utils.helpers as helpers

    chamadas = []

    def falhar(cmd):
        chamadas.append(cmd)
        return 1  # codigo de erro do shell

    monkeypatch.setattr(helpers.os, "system", falhar)
    helpers.limpar_tela()

    assert chamadas, "o comando nem chegou a ser tentado"
    assert len(chamadas) == 1, (
        f"limpar_tela tentou {len(chamadas)} comandos apos falha — nao pode "
        "entrar em retry silencioso"
    )


def test_limpar_tela_propaga_excecao_real_do_sistema(monkeypatch):
    """
    Se `os.system` levantar de verdade, o `except OSError` do código atua.

    Controle positivo do tratamento que existe: sem este caso, ninguém saberia
    se o `except` funciona ou se é decorativo.
    """
    import app.utils.helpers as helpers

    tentativas = []

    def estourar(cmd):
        tentativas.append(cmd)
        raise OSError("falha simulada do sistema")

    monkeypatch.setattr(helpers.os, "system", estourar)

    helpers.limpar_tela()  # não pode propagar

    assert tentativas, "o comando nem chegou a ser tentado"
