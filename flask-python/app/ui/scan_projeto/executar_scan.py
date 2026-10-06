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

"""Motor de varredura de codigo e geracao de relatorio de vulnerabilidades.

Este modulo executa o scan por assinatura em arquivos de projeto, exibe
progresso no terminal, consolida estatisticas e salva resultado em JSON.
"""

import os
import json
import datetime
from colorama import Fore, Style

from app.utils.log_sistema import get_logger
from app.utils.progresso_scan import notificar_progresso
from app.utils.tempo import (
    obter_timestamp,
    obter_timestamp_sistema,
    obter_timestamp_utc_brasil,
)

# Paleta padronizada via Colorama (mais consistente no Windows).
COR_CRITICO = Fore.MAGENTA + Style.BRIGHT
COR_ALTO = Fore.RED + Style.BRIGHT
COR_MEDIO = Fore.YELLOW + Style.BRIGHT
COR_BAIXO = Fore.GREEN + Style.BRIGHT
COR_SEPARADOR = Fore.WHITE

_log = get_logger("scan_engine")


def salvar_log_json(dados_scan):
    """
    Salva o resultado de scan em arquivo JSON no diretorio de logs.

    Args:
        dados_scan: Dicionario consolidado com metadados e vulnerabilidades.

    Returns:
        str: Caminho completo do arquivo gerado.
    """
    # Agora centralizando em logs/generic/reports
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    pasta_logs = os.path.join(base_path, "logs", "generic", "reports")
    
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs, exist_ok=True)

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"report_{timestamp}.json"
    caminho_completo = os.path.join(pasta_logs, nome_arquivo)

    try:
        with open(caminho_completo, "w", encoding="utf-8") as f:
            json.dump(dados_scan, f, indent=4, ensure_ascii=False)
    except OSError:
        _log.exception("Falha ao gravar relatorio JSON: %s", caminho_completo)
        raise
    _log.info("Relatorio de scan gravado: %s", caminho_completo)
    return caminho_completo
    
from .filtros.regras_seguranca import (
    obter_assinaturas_vulnerabilidade, 
    obter_extensoes_permitidas,
    obter_diretorios_ignorados,
    ordenar_por_severidade,
)

def contar_total_arquivos(caminho_alvo, extensoes, ignorados):
    """Conta arquivos candidatos ao scan para calcular progresso.

    Args:
        caminho_alvo: Diretorio raiz a ser escaneado.
        extensoes: Extensoes permitidas para leitura.
        ignorados: Diretorios que devem ser ignorados.
    """
    total = 0
    for raiz, pastas, arquivos in os.walk(caminho_alvo):
        pastas[:] = [p for p in pastas if p not in ignorados]
        for arquivo in arquivos:
            if any(arquivo.endswith(ext) for ext in extensoes):
                total += 1
    return total

def exibir_progresso(atual, total):
    """Renderiza barra de progresso textual no terminal."""
    if total == 0:
        return
    largura_barra = 40
    progresso = int((atual / total) * largura_barra)
    percentual = int((atual / total) * 100)
    
    barra = "█" * progresso + "-" * (largura_barra - progresso)
    
    # \r (Carriage Return) faz o cursor voltar ao início da linha para sobrescrever
    print(f"\r{Fore.YELLOW}Progresso: |{barra}| {percentual}% ({atual}/{total})", end="", flush=True)

def gerar_estatisticas_scan(relatorio):
    """
    Processa resultado do scan e imprime resumo consolidado no terminal.
    """
    total_falhas = len(relatorio["vulnerabilidades"])
    resumo_tipos = {}
    severidade_por_tipo = {}

    # Contabilização funcional por tipo de vulnerabilidade
    for falha in relatorio["vulnerabilidades"]:
        tipo = falha["tipo"]
        resumo_tipos[tipo] = resumo_tipos.get(tipo, 0) + 1
        severidade_por_tipo[tipo] = falha.get("severidade", "BAIXO")

    print(Fore.BLUE + "======================================================")
    print(Fore.CYAN + f"📊 RESUMO DO SCAN: {relatorio['projeto']}")
    print(Fore.BLUE + "======================================================")
    
    if total_falhas == 0:
        print(Fore.GREEN + "✅ Nenhuma vulnerabilidade crítica detectada nos padrões atuais.")
    else:
        print(Fore.RED + f"⚠️  Total de Ocorrências: {total_falhas}")
        print(
            f"{COR_CRITICO}🛑 CRÍTICO{Style.RESET_ALL} {COR_SEPARADOR}| "
            f"{COR_ALTO}🔴 ALTO{Style.RESET_ALL} {COR_SEPARADOR}| "
            f"{COR_MEDIO}🟠 MÉDIO{Style.RESET_ALL} {COR_SEPARADOR}| "
            f"{COR_BAIXO}🟢 BAIXO{Style.RESET_ALL}"
        )
        print("-" * 54)
        # Ajuste dinamico para manter o resumo alinhado independentemente
        # do tamanho do nome da vulnerabilidade.
        largura_coluna = max((len(tipo) for tipo in resumo_tipos.keys()), default=30) + 2

        def estilo_por_severidade(severidade):
            sev = str(severidade).upper()
            if sev in ["CRÍTICO", "CRITICO", "ALTA", "ALTO"]:
                if sev in ["CRÍTICO", "CRITICO"]:
                    return "🛑", COR_CRITICO
                return "🔴", COR_ALTO
            if sev in ["MÉDIO", "MEDIO", "MÉDIA", "MEDIA"]:
                return "🟠", COR_MEDIO
            return "🟢", COR_BAIXO

        for tipo, qtd in resumo_tipos.items():
            severidade = severidade_por_tipo.get(tipo, "BAIXO")
            icone, cor = estilo_por_severidade(severidade)
            print(
                f"{cor}{icone} {tipo:<{largura_coluna}}"
                f"{COR_SEPARADOR} --> {qtd:>3} encontrados{Style.RESET_ALL}"
            )
    
    print(Fore.BLUE + "======================================================\n" + Style.RESET_ALL)

def rodar_engine_scan(caminho_alvo, progress_callback=None, silent=False):
    """Executa varredura por assinatura em um diretorio de projeto.

    Args:
        caminho_alvo: Caminho da raiz do projeto informado pelo usuario.
        progress_callback: Funcao opcional para atualizar progresso na web.
        silent: Se True, nao imprime barra no terminal.

    Returns:
        str | None: Caminho do log JSON quando houver scan, ou None quando
        nao houver arquivos compativeis.
    """
    # Carrega as regras das funções
    assinaturas = obter_assinaturas_vulnerabilidade()
    extensoes = obter_extensoes_permitidas()
    ignorados = obter_diretorios_ignorados()

    # 1. Preparação da Barra
    total_arquivos = contar_total_arquivos(caminho_alvo, extensoes, ignorados)
    arquivos_processados = 0

    if total_arquivos == 0:
        _log.warning(
            "Scan sem arquivos compativeis na raiz %s",
            caminho_alvo,
        )
        if not silent:
            print(Fore.RED + "⚠️ Nenhum arquivo compatível encontrado para scan." + Style.RESET_ALL)
        notificar_progresso(progress_callback, 0, 0, "Nenhum arquivo compativel para scan.")
        return None

    # Inicializa a estrutura do log
    relatorio = {
        "schema_version": "ASPM-2026.1",
        "motor_relatorio": "scan_projeto_classico",
        "projeto": os.path.basename(caminho_alvo),
        "caminho_total": caminho_alvo,
        "timestamp_utc_global": obter_timestamp(),
        "timestamp_utc_brasil": obter_timestamp_utc_brasil(),
        "timestamp_sistema": obter_timestamp_sistema(),
        "total_arquivos_analisados": 0,
        "vulnerabilidades": []  # Mantendo 'vulnerabilidades' para manter a sintaxe do seu último exemplo
    }
    
    indice = 1
    _log.info(
        "Iniciando varredura ASPM em %s (%s arquivo(s) candidato(s))",
        caminho_alvo,
        total_arquivos,
    )
    if not silent:
        print(Fore.YELLOW + f"\n🔍 Iniciando varredura em: {caminho_alvo}...\n" + Style.RESET_ALL)
    notificar_progresso(progress_callback, 0, total_arquivos, "Iniciando varredura...")

    for raiz, pastas, arquivos in os.walk(caminho_alvo):
        # Filtro funcional de diretórios
        pastas[:] = [p for p in pastas if p not in ignorados]

        for arquivo in arquivos:
            if any(arquivo.endswith(ext) for ext in extensoes):
                relatorio["total_arquivos_analisados"] += 1
                caminho_file = os.path.join(raiz, arquivo)
                
                try:
                    with open(caminho_file, "r", encoding="utf-8", errors="ignore") as f:
                        for num_linha, linha in enumerate(f, 1):
                            linha_texto = linha.strip()
                            
                            # Varredura funcional pelas assinaturas mapeadas em tuplas
                            for tipo, regra in assinaturas.items():
                                padroes = regra[0]
                                severidade = regra[1]
                                descricao = regra[2] if len(regra) > 2 else "Nenhuma descrição técnica disponível para esta vulnerabilidade."
                                confianca = regra[3] if len(regra) > 3 else "-"
                                referencias = regra[4] if len(regra) > 4 else []
                                
                                for padrao in padroes:
                                    if padrao.lower() in linha_texto.lower():
                                        relatorio["vulnerabilidades"].append({
                                            "indice": indice,
                                            "timestamp_utc_global": obter_timestamp(),
                                            "timestamp_utc_brasil": obter_timestamp_utc_brasil(),
                                            "timestamp_sistema": obter_timestamp_sistema(),
                                            "severidade": severidade,
                                            "confianca": confianca,
                                            "tipo": tipo,
                                            "descricao": descricao,
                                            "referencias": referencias,
                                            "arquivo": arquivo,
                                            "caminho_completo": caminho_file,
                                            "linha": num_linha,
                                            "codigo": linha_texto[:150], # Captura estendida do trecho
                                            "padrao_detectado": padrao
                                        })
                                        indice += 1
                except Exception as e:
                    _log.warning(
                        "Nao foi possivel ler arquivo no scan: %s — %s",
                        caminho_file,
                        e,
                    )
                
                arquivos_processados += 1
                if not silent:
                    exibir_progresso(arquivos_processados, total_arquivos)
                notificar_progresso(
                    progress_callback,
                    arquivos_processados,
                    total_arquivos,
                )

    if not silent:
        print("\n")

    notificar_progresso(
        progress_callback,
        total_arquivos,
        total_arquivos,
        "Finalizando relatorio...",
    )

    relatorio["vulnerabilidades"] = ordenar_por_severidade(relatorio["vulnerabilidades"])

    if not silent:
        gerar_estatisticas_scan(relatorio)

    nome_gerado = salvar_log_json(relatorio)
    _log.info(
        "Scan finalizado: projeto=%s falhas=%s JSON=%s",
        relatorio.get("projeto"),
        len(relatorio.get("vulnerabilidades", [])),
        nome_gerado,
    )
    if not silent:
        print(Fore.GREEN + f"✅ Scan estruturado salvo no disco: {nome_gerado}\n" + Style.RESET_ALL)
    if progress_callback:
        progress_callback(
            {
                "status": "em_andamento",
                "mensagem": "Scan concluido.",
                "percentual": 100,
                "atual": total_arquivos,
                "total": total_arquivos,
                "caminho_log": nome_gerado,
            }
        )
    return nome_gerado