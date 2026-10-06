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
Concorrência: dois scans ao mesmo tempo, registro de jobs, logger sob threads.

PROPÓSITO DE NEGÓCIO
--------------------
A aplicação dispara scans em threads e mantém o progresso num dicionário global
em memória. Duas abas abertas, um duplo clique no botão, ou o próprio operador
rodando um scan de projeto enquanto o scan de containers ainda termina — tudo
isso produz execução simultânea. Nenhum desses caminhos tem lock.

Esta é a revisão de falha operacional aplicada ao que existe: o que acontece
quando duas operações legítimas acontecem juntas?

INVARIANTES DO DOMÍNIO
----------------------
- INV-CON-001 · Cada job recebe identificador único, mesmo criado no mesmo
  instante por threads diferentes.
- INV-CON-002 · Atualizar um job não corrompe outro.
- INV-CON-003 · O logger não duplica handler sob criação concorrente — handler
  duplicado faz cada linha aparecer N vezes no arquivo.
- INV-CON-004 · Dois scans simultâneos produzem dois relatórios distintos.
  **Esta invariante está QUEBRADA hoje** — ver o registro em
  `tests/regressao/test_achados_auditoria.py`.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha de concorrência não aparece em uso de uma pessoa só; aparece na
apresentação, com duas pessoas mexendo. É o tipo de defeito que passa em toda
revisão sequencial.
"""

from __future__ import annotations

import logging
import threading

import pytest

pytestmark = [pytest.mark.robustez, pytest.mark.unidade]


# ── INV-CON-001 · Unicidade de job ───────────────────────────────────────────

def test_jobs_criados_em_paralelo_recebem_ids_distintos():
    """
    30 threads criam job ao mesmo tempo: 30 identificadores diferentes.

    Id repetido faria duas execuções compartilharem estado de progresso — a
    barra de uma sobrescreveria a da outra e um usuário veria o resultado alheio.
    """
    from app.web.services import job_progresso

    job_progresso.JOBS_PROGRESSO.clear()
    ids: list[str] = []
    trava = threading.Lock()
    largada = threading.Event()

    def criar():
        largada.wait()
        job_id = job_progresso.criar_job("paralelo")
        with trava:
            ids.append(job_id)

    threads = [threading.Thread(target=criar) for _ in range(30)]
    for t in threads:
        t.start()
    largada.set()
    for t in threads:
        t.join(timeout=10)

    assert len(ids) == 30, f"nem todas as threads terminaram: {len(ids)}"
    assert len(set(ids)) == 30, (
        f"ids repetidos: {len(ids) - len(set(ids))} colisao(oes) em 30 jobs"
    )


def test_registro_de_jobs_sobrevive_a_escrita_concorrente():
    """
    Criação e atualização simultâneas não perdem nem corrompem entradas.

    `JOBS_PROGRESSO` é um `dict` global sem lock. Em CPython o GIL protege a
    operação atômica do dicionário, mas a sequência ler-modificar-gravar de
    `atualizar_job` não é atômica. Este teste mede se, na prática, o estado
    final de cada job é o que aquela thread escreveu.
    """
    from app.web.services import job_progresso

    job_progresso.JOBS_PROGRESSO.clear()
    quantidade = 40
    ids = [job_progresso.criar_job(f"job {i}") for i in range(quantidade)]
    largada = threading.Event()
    erros: list[str] = []

    def trabalhar(indice: int, job_id: str):
        largada.wait()
        for passo in range(20):
            job_progresso.atualizar_job(
                job_id, {"percentual": passo * 5, "mensagem": f"{indice}:{passo}"}
            )
        dados = job_progresso.obter_job(job_id)
        if dados is None:
            erros.append(f"job {job_id} sumiu do registro")
        elif dados["mensagem"] != f"{indice}:19":
            erros.append(
                f"job {job_id} terminou com {dados['mensagem']!r}, "
                f"esperado {indice}:19"
            )

    threads = [
        threading.Thread(target=trabalhar, args=(i, ids[i]))
        for i in range(quantidade)
    ]
    for t in threads:
        t.start()
    largada.set()
    for t in threads:
        t.join(timeout=15)

    assert not erros, "estado corrompido sob concorrencia:\n  " + "\n  ".join(erros)
    assert len(job_progresso.JOBS_PROGRESSO) == quantidade


def test_obter_job_durante_atualizacao_nao_estoura():
    """Leitura concorrente com escrita não pode levantar exceção."""
    from app.web.services import job_progresso

    job_progresso.JOBS_PROGRESSO.clear()
    job_id = job_progresso.criar_job("leitura concorrente")
    parar = threading.Event()
    erros: list[str] = []

    def escrever():
        contador = 0
        while not parar.is_set():
            contador += 1
            job_progresso.atualizar_job(job_id, {"percentual": contador % 100})

    def ler():
        try:
            while not parar.is_set():
                dados = job_progresso.obter_job(job_id)
                if dados is not None:
                    _ = dados["percentual"], dados["status"]
        except Exception as erro:  # noqa: BLE001 — queremos QUALQUER exceção
            erros.append(f"{type(erro).__name__}: {erro}")

    escritor = threading.Thread(target=escrever)
    leitores = [threading.Thread(target=ler) for _ in range(4)]
    escritor.start()
    for t in leitores:
        t.start()

    threading.Event().wait(0.4)
    parar.set()
    escritor.join(timeout=5)
    for t in leitores:
        t.join(timeout=5)

    assert not erros, f"leitura concorrente estourou: {erros}"


# ── INV-CON-003 · Logger ─────────────────────────────────────────────────────

@pytest.mark.xfail(
    strict=True,
    reason="ACHADO · corrida TOCTOU em _configurar_raiz_se_preciso: a checagem "
           "`if log.handlers: return` e o `log.addHandler(handler)` estao na "
           "mesma funcao sem lock. MEDIDO AQUI: 24 threads chamando get_logger "
           "pela primeira vez ao mesmo tempo anexam os 24 FileHandlers, e cada "
           "linha passaria a aparecer 24 vezes no arquivo. O impacto hoje e "
           "baixo porque o primeiro get_logger acontece no import, com uma "
           "thread so — mas o mecanismo esta vivo. Correcao: um "
           "threading.Lock em volta da checagem e da adicao.",
)
def test_logger_nao_duplica_handler_sob_criacao_concorrente(sandbox_de_caminhos):
    """
    `_configurar_raiz_se_preciso` testa `if log.handlers` e só depois adiciona.

    Entre o teste e a adição há uma janela: duas threads podem passar pelo `if`
    juntas e anexar dois FileHandlers ao mesmo arquivo. O sintoma é cada linha
    de log aparecer duplicada — confuso justamente na hora de investigar um erro.
    """
    from app.utils.log_sistema import get_logger

    for handler in list(logging.getLogger("ASPM").handlers):
        handler.close()
        logging.getLogger("ASPM").removeHandler(handler)

    largada = threading.Event()

    def pegar():
        largada.wait()
        get_logger("concorrente")

    threads = [threading.Thread(target=pegar) for _ in range(24)]
    for t in threads:
        t.start()
    largada.set()
    for t in threads:
        t.join(timeout=10)

    arquivo_handlers = [
        h for h in logging.getLogger("ASPM").handlers
        if isinstance(h, logging.FileHandler)
    ]
    assert len(arquivo_handlers) <= 1, (
        f"{len(arquivo_handlers)} FileHandlers anexados ao logger raiz — cada "
        "linha de log vai aparecer repetida esse tanto de vezes"
    )


def test_linha_de_log_nao_aparece_duplicada(sandbox_de_caminhos):
    """
    Efeito do teste acima, medido no arquivo: uma linha escrita, uma linha lida.

    Contar handler é medir o mecanismo; contar linha no arquivo é medir o dano.
    """
    from app.utils.log_sistema import get_logger

    log = get_logger("contagem")
    marca = "MARCA_UNICA_PARA_CONTAGEM_DE_DUPLICATA"
    log.info(marca)
    for handler in logging.getLogger("ASPM").handlers:
        handler.flush()

    arquivo = sandbox_de_caminhos / "logs" / "erro_sistema.log"
    assert arquivo.is_file(), "o log central nao foi criado no sandbox"

    conteudo = arquivo.read_text(encoding="utf-8", errors="ignore")
    assert conteudo.count(marca) == 1, (
        f"a linha apareceu {conteudo.count(marca)} vezes no arquivo"
    )


# ── Threads de trabalho ──────────────────────────────────────────────────────

def test_iniciar_thread_executa_todas_as_tarefas_disparadas():
    """
    `iniciar_thread` não pode perder tarefa sob disparo em rajada.

    Cenário real: o operador clica em "escanear" em três abas quase ao mesmo
    tempo. Uma tarefa que não executa deixa a barra de progresso parada para
    sempre, sem erro.
    """
    from app.web.services import job_progresso

    quantidade = 25
    executadas: list[str] = []
    trava = threading.Lock()
    terminou = threading.Semaphore(0)

    def alvo(job_id):
        with trava:
            executadas.append(job_id)
        terminou.release()

    for i in range(quantidade):
        job_progresso.iniciar_thread(f"job_{i}", alvo)

    for _ in range(quantidade):
        assert terminou.acquire(timeout=10), "tarefa nao executou no tempo esperado"

    assert len(executadas) == quantidade
    assert len(set(executadas)) == quantidade, "algum job_id foi executado duas vezes"


def test_thread_de_trabalho_nao_bloqueia_o_processo():
    """
    As threads de scan são daemon: o processo encerra mesmo com scan em curso.

    Sem isso, fechar a aplicação com um scan grande em andamento deixaria o
    processo pendurado e o operador acharia que travou.
    """
    from app.web.services import job_progresso

    capturada: dict[str, threading.Thread] = {}
    pronto = threading.Event()

    original = threading.Thread

    class Espiao(original):  # type: ignore[misc, valid-type]
        def start(self):
            capturada["t"] = self
            pronto.set()
            return super().start()

    threading.Thread = Espiao  # type: ignore[misc]
    try:
        job_progresso.iniciar_thread("job_daemon", lambda _job: None)
        assert pronto.wait(5), "a thread nao chegou a ser criada"
    finally:
        threading.Thread = original  # type: ignore[misc]

    thread = capturada["t"]
    thread.join(timeout=5)
    assert thread.daemon is True, (
        "a thread de trabalho nao e daemon — fechar a aplicacao com scan em "
        "andamento deixaria o processo pendurado"
    )
