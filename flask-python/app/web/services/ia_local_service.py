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

"""Servicos web de IA local — delega para app.ui.scan_ia_local."""

import json
import os

from app.ui.scan_ia_local.executar_scan_ia import (
    analisar_com_ia_local,
    salvar_relatorios_ia,
    testar_conexao_gpu,
)
from app.ui.scan_ia_local.menu_ia_local import detectar_gpu_automatica
from app.ui.scan_ia_local.scan_amd.executar_scan import rodar_engine_scan_amd
from app.ui.scan_ia_local.scan_amd.listar_falhas import obter_diretorio_logs_amd
from app.ui.scan_ia_local.scan_nvidia.executar_scan import rodar_engine_scan_nvidia
from app.web.services.job_progresso import (
    atualizar_job,
    criar_job,
    iniciar_thread,
    obter_job,
)
from app.ui.scan_ia_local.scan_nvidia.listar_falhas import obter_diretorio_logs_nvidia

_ASPM_CONTEXTO = (
    "ASPM PRIDE 2026 — interface web Flask; relatorios em logs/amd e logs/nvidia; "
    "LM Studio em localhost:1234."
)


def obter_gpu_padrao():
    """Hardware sugerido (nvidia se nvidia-smi responder)."""
    return detectar_gpu_automatica()


def status_lm_studio():
    """Status da conexao com LM Studio."""
    conectado, modelo = testar_conexao_gpu()
    return {"conectado": conectado, "modelo": modelo or "—"}


def _pasta_relatorios(hardware):
    """Diretorio de JSON por GPU."""
    if hardware == "nvidia":
        return obter_diretorio_logs_nvidia()
    return obter_diretorio_logs_amd()


def listar_relatorios_gpu(hardware):
    """Lista relatorios JSON do perfil AMD ou NVIDIA."""
    pasta = _pasta_relatorios(hardware)
    if not os.path.isdir(pasta):
        return []

    itens = []
    for nome in sorted(os.listdir(pasta), reverse=True):
        if not nome.endswith(".json"):
            continue
        caminho = os.path.join(pasta, nome)
        item = {
            "nome_arquivo": nome,
            "caminho_completo": caminho,
            "projeto": "—",
            "total_falhas": 0,
            "tem_parecer_md": os.path.exists(caminho.replace(".json", "_AI_PREMIUM.md")),
            "tem_parecer_txt": os.path.exists(caminho.replace(".json", "_AI_LEITURA.txt")),
        }
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            item["projeto"] = dados.get("projeto", "—")
            item["total_falhas"] = len(dados.get("vulnerabilidades", []))
        except (OSError, json.JSONDecodeError):
            pass
        itens.append(item)
    return itens


def _rodar_motor_gpu(hardware, caminho_alvo, progress_callback=None, silent=False):
    """Delega para motor AMD ou NVIDIA."""
    if hardware == "nvidia":
        return rodar_engine_scan_nvidia(
            caminho_alvo,
            progress_callback=progress_callback,
            silent=silent,
        )
    return rodar_engine_scan_amd(
        caminho_alvo,
        progress_callback=progress_callback,
        silent=silent,
    )


def executar_scan_gpu(hardware, caminho_alvo):
    """Executa motor AMD ou NVIDIA."""
    caminho_alvo = (caminho_alvo or "").strip()
    if not caminho_alvo:
        return False, "Informe o caminho do projeto.", None
    if not os.path.isdir(caminho_alvo):
        return False, "Caminho invalido ou inexistente.", None

    caminho_log = _rodar_motor_gpu(hardware, caminho_alvo)
    if not caminho_log or not os.path.exists(caminho_log):
        return False, "Scan concluido sem gerar relatorio.", None

    return True, "Scan GPU executado com sucesso.", os.path.basename(caminho_log)


def iniciar_scan_gpu_assincrono(hardware, caminho_alvo):
    """Inicia scan GPU em background com progresso."""
    caminho_alvo = (caminho_alvo or "").strip()
    if not caminho_alvo:
        return False, "Informe o caminho do projeto.", None
    if not os.path.isdir(caminho_alvo):
        return False, "Caminho invalido ou inexistente.", None

    job_id = criar_job(f"Iniciando scan {hardware.upper()}...")
    iniciar_thread(
        job_id,
        lambda jid: _executar_scan_gpu_background(jid, hardware, caminho_alvo),
    )
    return True, "Scan iniciado.", job_id


def _executar_scan_gpu_background(job_id, hardware, caminho_alvo):
    """Worker assincrono do scan GPU."""

    def atualizar(payload):
        atualizar_job(job_id, payload)

    try:
        caminho_log = _rodar_motor_gpu(
            hardware,
            caminho_alvo,
            progress_callback=atualizar,
            silent=True,
        )
        if caminho_log and os.path.exists(caminho_log):
            nome = os.path.basename(caminho_log)
            atualizar_job(
                job_id,
                {
                    "status": "concluido",
                    "mensagem": "Scan GPU concluido.",
                    "percentual": 100,
                    "nome_log": nome,
                    "redirect_url": (
                        f"/ia-local/auditoria/{hardware}/{nome}"
                    ),
                },
            )
        else:
            atualizar_job(
                job_id,
                {"status": "erro", "mensagem": "Scan sem relatorio gerado."},
            )
    except Exception as erro:
        atualizar_job(job_id, {"status": "erro", "mensagem": str(erro)})


def iniciar_scan_cognitivo_assincrono(hardware, caminho_alvo):
    """Scan GPU + IA com barra de progresso em duas fases."""
    caminho_alvo = (caminho_alvo or "").strip()
    if not caminho_alvo:
        return False, "Informe o caminho do projeto.", None
    if not os.path.isdir(caminho_alvo):
        return False, "Caminho invalido ou inexistente.", None

    job_id = criar_job("Preparando scan cognitivo...")
    iniciar_thread(
        job_id,
        lambda jid: _executar_cognitivo_background(jid, hardware, caminho_alvo),
    )
    return True, "Scan cognitivo iniciado.", job_id


def _executar_cognitivo_background(job_id, hardware, caminho_alvo):
    """Worker: scan (0-85%) + IA (85-100%)."""

    def atualizar_scan(payload):
        percentual = int(payload.get("percentual", 0))
        atualizar_job(
            job_id,
            {
                "mensagem": payload.get("mensagem", "Escaneando..."),
                "percentual": int(percentual * 0.85),
                "atual": payload.get("atual", 0),
                "total": payload.get("total", 0),
            },
        )

    try:
        caminho_log = _rodar_motor_gpu(
            hardware,
            caminho_alvo,
            progress_callback=atualizar_scan,
            silent=True,
        )
        if not caminho_log or not os.path.exists(caminho_log):
            atualizar_job(job_id, {"status": "erro", "mensagem": "Scan sem relatorio."})
            return

        atualizar_job(
            job_id,
            {
                "mensagem": "Analisando com IA local (LM Studio)...",
                "percentual": 90,
            },
        )
        ok, msg, caminho_md, _ = analisar_relatorio_ia(caminho_log)
        if ok and caminho_md:
            atualizar_job(
                job_id,
                {
                    "status": "concluido",
                    "mensagem": "Scan cognitivo concluido.",
                    "percentual": 100,
                    "redirect_url": (
                        f"/ia-local/parecer/{hardware}/"
                        f"{os.path.basename(caminho_md)}"
                    ),
                },
            )
        else:
            atualizar_job(
                job_id,
                {
                    "status": "erro",
                    "mensagem": msg or "Falha na analise IA.",
                },
            )
    except Exception as erro:
        atualizar_job(job_id, {"status": "erro", "mensagem": str(erro)})


def obter_status_job_ia(job_id):
    """Status de job assincrono (IA local / containers)."""
    return obter_job(job_id)


def analisar_relatorio_ia(caminho_json):
    """Gera parecer IA a partir de relatorio JSON."""
    caminho_json = (caminho_json or "").strip()
    if not caminho_json or not os.path.isfile(caminho_json):
        return False, "Relatorio JSON nao encontrado.", None, None

    with open(caminho_json, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    vulnerabilidades = dados.get("vulnerabilidades", [])
    if not vulnerabilidades:
        return False, "Nenhuma vulnerabilidade para analise.", None, None

    linhas = [
        f"Projeto: {dados.get('projeto', '?')}",
        f"Caminho: {dados.get('caminho_total', '?')}",
        f"Hardware: {dados.get('hardware', 'n/d')}",
        f"Total achados: {len(vulnerabilidades)}",
        "",
        "Amostra:",
    ]
    for falha in vulnerabilidades[:20]:
        linhas.append(
            f"- {falha.get('severidade')} | {falha.get('tipo')} | "
            f"{falha.get('arquivo')}:{falha.get('linha')}"
        )

    sistema = (
        "Voce e CSO senior. Relatorio Markdown com priorizacao, riscos e proximos passos."
    )
    prompt = _ASPM_CONTEXTO + "\n\n" + "\n".join(linhas)

    parecer = analisar_com_ia_local(prompt, sistema)
    if str(parecer).startswith("Falha"):
        return False, parecer, None, None

    caminho_md, caminho_txt = salvar_relatorios_ia(caminho_json, parecer, dados)
    return True, "Analise cognitiva concluida.", caminho_md, caminho_txt


def ler_parecer_markdown(caminho_md):
    """Le arquivo de parecer .md."""
    caminho_md = (caminho_md or "").strip()
    if not caminho_md or not os.path.isfile(caminho_md):
        return None
    try:
        with open(caminho_md, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except OSError:
        return None


def _caminho_relatorio(hardware, nome_arquivo):
    """Monta caminho absoluto seguro do relatorio JSON."""
    pasta = _pasta_relatorios(hardware)
    nome = os.path.basename(nome_arquivo or "")
    caminho = os.path.abspath(os.path.join(pasta, nome))
    if os.path.commonpath([pasta, caminho]) != pasta:
        return None
    return caminho if os.path.isfile(caminho) else None


def obter_ultimo_relatorio_json(hardware):
    """Retorna caminho do relatorio JSON mais recente da GPU."""
    pasta = _pasta_relatorios(hardware)
    if not os.path.isdir(pasta):
        return None
    arquivos = sorted(
        [f for f in os.listdir(pasta) if f.endswith(".json")],
        reverse=True,
    )
    if not arquivos:
        return None
    return os.path.join(pasta, arquivos[0])


def obter_ultimo_parecer_md(hardware):
    """Retorna caminho do ultimo parecer Markdown gerado."""
    pasta = _pasta_relatorios(hardware)
    if not os.path.isdir(pasta):
        return None
    arquivos = sorted(
        [f for f in os.listdir(pasta) if f.endswith("_AI_PREMIUM.md")],
        reverse=True,
    )
    if not arquivos:
        return None
    return os.path.join(pasta, arquivos[0])


def obter_dados_auditoria(hardware, nome_arquivo):
    """Carrega relatorio GPU e falhas enriquecidas para auditoria web."""
    from app.ui.scan_projeto.listar_falhas import enriquecer_falhas_para_web

    caminho = _caminho_relatorio(hardware, nome_arquivo)
    if not caminho:
        return None

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return None

    falhas = dados.get("vulnerabilidades", [])
    enriquecer_falhas_para_web(falhas)
    return {
        "caminho": caminho,
        "dados": dados,
        "falhas": falhas,
        "nome_arquivo": os.path.basename(caminho),
    }


def obter_falha_auditoria(hardware, nome_arquivo, falha_id):
    """Retorna uma falha pelo indice para tela de detalhe."""
    auditoria = obter_dados_auditoria(hardware, nome_arquivo)
    if not auditoria:
        return None, None

    for falha in auditoria["falhas"]:
        indice = falha.get("indice", falha.get("id"))
        if str(indice) == str(falha_id):
            return auditoria, falha
    return auditoria, None


def executar_scan_cognitivo(hardware, caminho_alvo):
    """Scan GPU + analise IA em um unico fluxo (opcao 3 do CLI)."""
    caminho_alvo = (caminho_alvo or "").strip()
    if not caminho_alvo or not os.path.isdir(caminho_alvo):
        return False, "Caminho invalido.", None, None, None

    caminho_log = _rodar_motor_gpu(hardware, caminho_alvo)
    if not caminho_log:
        return False, "Scan sem relatorio.", None, None, None

    nome_log = os.path.basename(caminho_log)
    ok_ia, msg_ia, caminho_md, caminho_txt = analisar_relatorio_ia(caminho_log)
    if not ok_ia:
        return False, f"Scan OK, mas IA falhou: {msg_ia}", nome_log, None, None

    return True, "Scan cognitivo concluido.", nome_log, caminho_md, caminho_txt


def reanalisar_ultimo_relatorio(hardware):
    """Re-analisa o ultimo JSON da GPU (opcao 4 do CLI)."""
    caminho = obter_ultimo_relatorio_json(hardware)
    if not caminho:
        return False, "Nenhum relatorio JSON encontrado.", None, None
    return analisar_relatorio_ia(caminho)


def imprimir_ultimo_parecer(hardware):
    """Envia ultimo parecer .md para impressora (opcao 5 do CLI, Windows)."""
    from app.ui.scan_ia_local.executar_scan_ia import imprimir_relatorio

    caminho = obter_ultimo_parecer_md(hardware)
    if not caminho:
        return False, "Nenhum parecer Markdown encontrado."

    if os.name != "nt":
        return False, "Impressao automatica disponivel apenas no Windows."

    if imprimir_relatorio(caminho):
        return True, f"Enviado para impressao: {os.path.basename(caminho)}"
    return False, "Falha ao enviar para impressora."
