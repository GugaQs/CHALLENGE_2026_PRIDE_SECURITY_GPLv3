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

"""Visualizacao e navegacao dos relatórios JSON de scan."""

import os
import json
import re
import subprocess
from collections import defaultdict

from colorama import Fore, Style
from app.utils.helpers import limpar_tela
from app.utils.log_sistema import get_logger

# Paleta padronizada via Colorama.

_log = get_logger("listar_falhas")
COR_CRITICO = Fore.MAGENTA + Style.BRIGHT
COR_ALTO = Fore.RED + Style.BRIGHT
COR_MEDIO = Fore.YELLOW + Style.BRIGHT
COR_BAIXO = Fore.GREEN + Style.BRIGHT
COR_NEUTRO = Fore.WHITE

_CWE_EM_TEXTO = re.compile(r"CWE[-\s]?(\d+)", re.IGNORECASE)
_CVE_EM_TEXTO = re.compile(r"\b(CVE-\d{4}-\d+)\b", re.IGNORECASE)


def _cve_ids_em_referencias(referencias):
    """Extrai identificadores CVE citados em qualquer string da lista."""
    ids = set()
    for ref in referencias:
        if not isinstance(ref, str):
            continue
        for m in _CVE_EM_TEXTO.finditer(ref):
            ids.add(m.group(1).upper())
    return sorted(ids)


def _imprimir_cves_codigo_e_link(referencias):
    """Uma linha por CVE: codigo oficial + URL de detalhe no NVD."""
    cves = _cve_ids_em_referencias(referencias)
    if not cves:
        return
    print(f"{Fore.WHITE}📛 CVE — codigo e ficha no NVD:{Style.RESET_ALL}")
    for cve in cves:
        url = f"https://nvd.nist.gov/vuln/detail/{cve}"
        print(f"{Fore.CYAN}- {cve} — {url}{Style.RESET_ALL}")
    print()


def _numeros_cwe_em_referencias(referencias):
    """Extrai IDs numericos de CWE citados nas referencias (ex.: CWE-79)."""
    ids = set()
    for ref in referencias:
        if not isinstance(ref, str):
            continue
        for m in _CWE_EM_TEXTO.finditer(ref):
            ids.add(int(m.group(1)))
    return sorted(ids)


def _imprimir_links_nvd_mitre(referencias):
    """
    Para cada CWE citado: codigo + link NVD (lista de CVEs com esse CWE)
    + link MITRE (definicao da fraqueza).
    """
    nums = _numeros_cwe_em_referencias(referencias)
    if not nums:
        return
    print(
        f"{Fore.WHITE}🛡️ CWE — codigo e links (NVD por tipo de falha + MITRE):"
        f"{Style.RESET_ALL}"
    )
    print(
        f"{Fore.WHITE}   CWE classifica o tipo de erro; use o NVD para ver CVEs "
        f"que carregam esse CWE.{Style.RESET_ALL}"
    )
    for n in nums:
        cwe = f"CWE-{n}"
        url_nvd = (
            "https://nvd.nist.gov/vuln/search/results?"
            "form_type=Advanced&search_type=all&"
            f"cwe_id={cwe}"
        )
        url_mitre = f"https://cwe.mitre.org/data/definitions/{n}.html"
        print(f"{Fore.CYAN}- {cwe} — NVD (lista de CVEs): {url_nvd}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}- {cwe} — MITRE (definicao): {url_mitre}{Style.RESET_ALL}")
    print()


def obter_diretorio_logs():
    """Retorna o caminho absoluto da pasta de logs."""
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    return os.path.join(base, "logs", "generic", "reports")

def ler_json_log(caminho_arquivo):
    """Le um arquivo JSON e retorna dicionario com os dados do scan."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        _log.exception("Erro ao ler ou interpretar JSON de relatorio: %s", caminho_arquivo)
        print(Fore.RED + f"Erro ao processar arquivo: {e}")
        return None

def apresentar_tabela_logs():
    """Lista relatorios disponiveis e retorna o caminho selecionado."""
    pasta = obter_diretorio_logs()
    
    if not os.path.exists(pasta) or not os.listdir(pasta):
        _log.warning("Pasta de logs de scan vazia ou inexistente: %s", pasta)
        print(Fore.RED + "\n⚠️ Base de dados de logs vazia." + Style.RESET_ALL)
        return None

    arquivos = [f for f in os.listdir(pasta) if f.endswith('.json')]
    
    if not arquivos:
        _log.warning("Nenhum arquivo JSON de relatorio em %s", pasta)
        print(Fore.RED + "\n⚠️ Nenhum JSON de log encontrado." + Style.RESET_ALL)
        return None
        
    print(f"\n{Fore.YELLOW}📋 SELECIONE UM RELATÓRIO ASPM:{Style.RESET_ALL}")
    print("-" * 50)
    for i, nome in enumerate(arquivos, 1):
        print(f"{Fore.CYAN}{i}{Style.RESET_ALL} - {nome}")
    print("-" * 50)

    try:
        indice = int(input(Fore.YELLOW + "Digite o número (ou 0 para sair): " + Style.RESET_ALL))
        if indice == 0: return None
        return os.path.join(pasta, arquivos[indice - 1])
    except (ValueError, IndexError):
        _log.warning("Selecao invalida na lista de relatorios JSON.")
        print(Fore.RED + "Seleção inválida." + Style.RESET_ALL)
        return None

def _normalizar_severidade(valor):
    """Alinha rotulos de severidade para agrupamento."""
    s = str(valor or "").upper().strip()
    if s in ("CRÍTICO", "CRITICO", "CRÍTICA", "CRITICA"):
        return "CRÍTICO"
    if s in ("ALTO", "ALTA"):
        return "ALTO"
    if s in ("MÉDIO", "MEDIO", "MÉDIA", "MEDIA"):
        return "MÉDIO"
    if s in ("BAIXO", "BAIXA"):
        return "BAIXO"
    return s or "—"


def escolher_por_tipo(falhas):
    """Lista tipos numerados; retorna sublista e texto para cabecalho."""
    if not falhas:
        return [], ""
    grupos = defaultdict(list)
    for f in falhas:
        grupos[f.get("tipo", "Desconhecido")].append(f)
    ordenado = sorted(grupos.items(), key=lambda x: len(x[1]), reverse=True)

    limpar_tela()
    print(f"\n{Fore.CYAN}Tipos de alerta neste relatorio:{Style.RESET_ALL}")
    print(Fore.BLUE + "-" * 62 + Style.RESET_ALL)
    for i, (nome, ocorr) in enumerate(ordenado, 1):
        nome_curto = nome if len(nome) <= 48 else nome[:45] + "..."
        print(f"  {Fore.YELLOW}{i:2}{Style.RESET_ALL}  {nome_curto}  ({len(ocorr)})")
    print(Fore.BLUE + "-" * 62 + Style.RESET_ALL)

    raw = input(
        Fore.CYAN + "Numero do tipo (Enter = voltar sem filtro): " + Style.RESET_ALL
    ).strip()
    if not raw.isdigit():
        return falhas, ""
    idx = int(raw)
    if 1 <= idx <= len(ordenado):
        nome, lst = ordenado[idx - 1]
        return lst, f"Somente tipo: {nome[:55]}"
    return falhas, ""


def escolher_por_gravidade(falhas):
    """Lista severidades padrao; retorna sublista e texto para cabecalho."""
    niveis = ["CRÍTICO", "ALTO", "MÉDIO", "BAIXO"]
    limpar_tela()
    print(f"\n{Fore.CYAN}Gravidade (severidade):{Style.RESET_ALL}")
    print(Fore.BLUE + "-" * 42 + Style.RESET_ALL)
    for i, n in enumerate(niveis, 1):
        c = sum(
            1 for f in falhas if _normalizar_severidade(f.get("severidade")) == n
        )
        print(f"  {Fore.YELLOW}{i}{Style.RESET_ALL}  {n:<10} ({c} falhas)")
    print(Fore.BLUE + "-" * 42 + Style.RESET_ALL)

    raw = input(
        Fore.CYAN + "Numero da gravidade (Enter = voltar sem filtro): " + Style.RESET_ALL
    ).strip()
    if not raw.isdigit():
        return falhas, ""
    idx = int(raw)
    if 1 <= idx <= len(niveis):
        alvo = niveis[idx - 1]
        filtradas = [
            f
            for f in falhas
            if _normalizar_severidade(f.get("severidade")) == alvo
        ]
        return filtradas, f"Somente gravidade: {alvo}"
    return falhas, ""


def abrir_arquivo_no_editor(caminho_arquivo):
    """
    Abre arquivo no editor padrao do sistema operacional.
    """
    if not os.path.exists(caminho_arquivo):
        print(Fore.RED + f"⚠️ Arquivo original não encontrado: {caminho_arquivo}" + Style.RESET_ALL)
        return

    try:
        print(Fore.YELLOW + f"🚀 Abrindo: {os.path.basename(caminho_arquivo)}..." + Style.RESET_ALL)
        if os.name == 'nt':
            os.startfile(caminho_arquivo)
        else:
            subprocess.run(['xdg-open', caminho_arquivo], check=False)
    except Exception as e:
        _log.exception("Falha ao abrir arquivo no editor padrao do SO.")
        print(Fore.RED + f"❌ Falha ao abrir editor: {e}" + Style.RESET_ALL)

def navegar_falhas_detalhadamente(caminho_log, falhas=None, etiqueta_filtro=""):
    """
    Exibe tabela de falhas e permite abrir arquivo-fonte ou JSON bruto.

    Args:
        caminho_log: Caminho do relatorio JSON escolhido pelo usuario.
        falhas: Lista opcional (subconjunto); se None, usa todas do JSON.
        etiqueta_filtro: Texto opcional mostrado quando a lista esta filtrada.
    """
    dados = ler_json_log(caminho_log)
    if not dados:
        return

    if falhas is None:
        falhas = dados.get("vulnerabilidades", []) or dados.get(
            "falhas_encontradas", []
        )
    
    while True:
        limpar_tela()
        print(f"\n{Fore.GREEN}ANÁLISE DO PROJETO: {dados.get('projeto', 'Desconhecido')}{Style.RESET_ALL}")
        timestamp_execucao = dados.get('timestamp_utc_global', dados.get('timestamp', 'Data não disponível'))
        print(f"Executado em (UTC): {timestamp_execucao}")
        if etiqueta_filtro:
            print(f"{Fore.YELLOW}Filtro ativo: {etiqueta_filtro}{Style.RESET_ALL}")
        print("=" * 120)
        
        # Cabeçalho formatado da tabela
        template = "{:<4} | {:<14} | {:<30} | {:<25} | {:<35}"
        print(Fore.YELLOW + Style.BRIGHT + template.format("ID", "SEVERIDADE", "VULNERABILIDADE", "MOMENTO (UTC)", "ARQUIVO") + Style.RESET_ALL)
        print("-" * 120)

        if not falhas:
            print(Fore.GREEN + "✅ Nenhuma vulnerabilidade mapeada neste JSON." + Style.RESET_ALL)
        
        # Lista as falhas na Tabela
        for falha in falhas:
            sev = str(falha.get('severidade', '-')).upper()
            
            if sev in ["CRÍTICO", "CRÍTICA"]:
                cor = COR_CRITICO
                icone_sev = "🛑"
            elif sev in ["ALTA", "ALTO"]:
                cor = COR_ALTO
                icone_sev = "🔴"
            elif sev in ["MÉDIA", "MÉDIO"]:
                cor = COR_MEDIO
                icone_sev = "🟠"
            elif sev in ["BAIXA", "BAIXO"]:
                cor = COR_BAIXO
                icone_sev = "🟢"
            else:
                cor = COR_NEUTRO
                icone_sev = "⚪"
                
            sev_formatada = f"{icone_sev} {sev}"
            
            tipo_falha = falha.get('tipo', 'Desconhecido')
            timestamp_str = falha.get('timestamp_utc_global', falha.get('timestamp_gmt', '-'))
            
            print(cor + template.format(
                falha.get('indice', falha.get('id', '-')), 
                sev_formatada,
                tipo_falha[:30], 
                timestamp_str,
                falha.get('arquivo', '-')
            ) + Style.RESET_ALL)

        print("=" * 120)
        print(f"\n{Fore.CYAN}Opções de Visualização e Auditoria:{Style.RESET_ALL}")
        
        prompt = (f"{Fore.YELLOW}[ID DA FALHA]{Style.RESET_ALL} Abrir o arquivo exato que contém o problema\n"
                  f"{Fore.YELLOW}[J]{Style.RESET_ALL} Visualizar o arquivo JSON bruto no Editor\n"
                  f"{Fore.RED}[0]{Style.RESET_ALL} Voltar ao Menu Anterior\n"
                  f"{Fore.CYAN}👉 Digite sua escolha: {Style.RESET_ALL}")
        
        opcao = input(prompt).strip().lower()

        if opcao == '0' or opcao == 's':
            break
        elif opcao == 'j':
            abrir_arquivo_no_editor(caminho_log)
            input(f"\n{Fore.GREEN}✔ Arquivo JSON (.json) enviado ao editor do SO. Pressione Enter para voltar...{Style.RESET_ALL}")
        else:
            # Tenta buscar a falha pelo ID para abrir o arquivo dela
            falha_encontrada = None
            for f in falhas:
                if str(f.get('indice', f.get('id', ''))) == opcao:
                    falha_encontrada = f
                    break
            
            if falha_encontrada:
                caminho_arq = falha_encontrada.get('caminho_completo', falha_encontrada.get('caminho'))
                sev = str(falha_encontrada.get('severidade', '-')).upper()
                if sev in ["CRÍTICO", "CRÍTICA"]:
                    cor_sev = COR_CRITICO
                    icone_sev = "🛑"
                elif sev in ["ALTA", "ALTO"]:
                    cor_sev = COR_ALTO
                    icone_sev = "🔴"
                elif sev in ["MÉDIA", "MÉDIO"]:
                    cor_sev = COR_MEDIO
                    icone_sev = "🟠"
                elif sev in ["BAIXA", "BAIXO"]:
                    cor_sev = COR_BAIXO
                    icone_sev = "🟢"
                else:
                    cor_sev = COR_NEUTRO
                    icone_sev = "⚪"

                def linha_detalhe(rotulo, valor, cor_rotulo=Fore.YELLOW, largura=18):
                    print(f"{cor_rotulo}{rotulo:<{largura}}{Style.RESET_ALL} : {valor}")

                print(Fore.BLUE + "=" * 110)
                print(Fore.CYAN + Style.BRIGHT + "📋 DETALHES DA FALHA SELECIONADA")
                print(Fore.BLUE + "=" * 110 + Style.RESET_ALL)
                linha_detalhe("ID", falha_encontrada.get('indice', falha_encontrada.get('id', '-')))
                linha_detalhe(
                    "Severidade",
                    f"{icone_sev} {sev}",
                    cor_rotulo=cor_sev
                )
                linha_detalhe("Tipo", falha_encontrada.get('tipo', 'Desconhecido'))
                linha_detalhe("Confianca", falha_encontrada.get('confianca', '-'))
                linha_detalhe(
                    "Momento (UTC)",
                    falha_encontrada.get('timestamp_utc_global', falha_encontrada.get('timestamp_gmt', '-'))
                )
                linha_detalhe("UTC Brasil", falha_encontrada.get('timestamp_utc_brasil', '-'))
                linha_detalhe("Data Sistema", falha_encontrada.get('timestamp_sistema', '-'))
                linha_detalhe("Arquivo", falha_encontrada.get('arquivo', '-'))
                linha_detalhe("Linha", falha_encontrada.get('linha', '-'))
                linha_detalhe("Padrao detectado", falha_encontrada.get('padrao_detectado', '-'))
                print(Fore.BLUE + "-" * 110 + Style.RESET_ALL)
                
                print(f"\n{Fore.LIGHTMAGENTA_EX}📖 EXPLICAÇÃO & CORREÇÃO:")
                descricao = falha_encontrada.get('descricao', 'Nenhuma descrição técnica disponível para esta vulnerabilidade.')
                print(f"{Fore.WHITE}{descricao}{Style.RESET_ALL}\n")

                arquivo_ref = falha_encontrada.get('arquivo', '-')
                linha_ref = falha_encontrada.get('linha', '-')
                print(f"{Fore.WHITE}📍 REFERÊNCIA NO CÓDIGO:")
                print(f"{Fore.CYAN}- {arquivo_ref}:{linha_ref}{Style.RESET_ALL}\n")

                referencias = falha_encontrada.get('referencias', [])
                if referencias:
                    print(f"{Fore.WHITE}🔗 REFERÊNCIAS TÉCNICAS (CWE/OWASP):")
                    for ref in referencias:
                        print(f"{Fore.CYAN}- {ref}{Style.RESET_ALL}")
                    print()
                    _imprimir_cves_codigo_e_link(referencias)
                    _imprimir_links_nvd_mitre(referencias)
                
                print(f"{Fore.WHITE}💻 TRECHO DO CÓDIGO:")
                codigo_trecho = falha_encontrada.get('codigo_trecho', falha_encontrada.get('codigo', ''))
                linha_falha = falha_encontrada.get('linha', '-')
                print(
                    f"{Fore.CYAN}{Style.BRIGHT}Linha {linha_falha}: "
                    f"{codigo_trecho.strip()[:150]}{Style.RESET_ALL}\n"
                )
                
                abrir_arquivo_no_editor(caminho_arq)
                input(f"\n{Fore.GREEN}✔ Arquivo fonte enviado ao editor do SO. Pressione Enter para voltar...{Style.RESET_ALL}")
            else:
                input(Fore.RED + "\n⚠️ Opção ou ID não encontrado. Pressione Enter para tentar novamente..." + Style.RESET_ALL)


def obter_links_cve_web(referencias):
    """Retorna lista de CVE com URL NVD para templates web."""
    return [
        {"codigo": cve, "url": f"https://nvd.nist.gov/vuln/detail/{cve}"}
        for cve in _cve_ids_em_referencias(referencias or [])
    ]


def obter_links_cwe_web(referencias):
    """Retorna lista de CWE com links NVD e MITRE para templates web."""
    links = []
    for numero in _numeros_cwe_em_referencias(referencias or []):
        cwe = f"CWE-{numero}"
        links.append(
            {
                "codigo": cwe,
                "url_nvd": (
                    "https://nvd.nist.gov/vuln/search/results?"
                    "form_type=Advanced&search_type=all&"
                    f"cwe_id={cwe}"
                ),
                "url_mitre": f"https://cwe.mitre.org/data/definitions/{numero}.html",
            }
        )
    return links


def enriquecer_falhas_para_web(falhas):
    """Anexa links CVE/CWE em cada falha para exibicao na interface web."""
    for falha in falhas:
        referencias = falha.get("referencias") or []
        falha["links_cve"] = obter_links_cve_web(referencias)
        falha["links_cwe"] = obter_links_cwe_web(referencias)
    return falhas
