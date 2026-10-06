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

"""Visualizacao e navegacao dos relatórios JSON de scan - VERSÃO NVIDIA GEFORCE (DETALHADA)."""

import os
import json
import re
import subprocess
from colorama import Fore, Style
from app.utils.helpers import limpar_tela

_CWE_EM_TEXTO = re.compile(r"CWE[-\s]?(\d+)", re.IGNORECASE)
_CVE_EM_TEXTO = re.compile(r"\b(CVE-\d{4}-\d+)\b", re.IGNORECASE)

def _imprimir_cves_codigo_e_link(referencias):
    ids = set()
    for ref in referencias:
        if not isinstance(ref, str): continue
        for m in _CVE_EM_TEXTO.finditer(ref):
            ids.add(m.group(1).upper())
    if not ids: return
    print(f"{Fore.WHITE}📛 CVE — código e ficha no NVD:{Style.RESET_ALL}")
    for cve in sorted(ids):
        print(f"{Fore.CYAN}- {cve} — https://nvd.nist.gov/vuln/detail/{cve}{Style.RESET_ALL}")
    print()

def _imprimir_links_nvd_mitre(referencias):
    ids = set()
    for ref in referencias:
        if not isinstance(ref, str): continue
        for m in _CWE_EM_TEXTO.finditer(ref):
            ids.add(int(m.group(1)))
    if not ids: return
    print(f"{Fore.WHITE}🛡️ CWE — código e links (NVD + MITRE):{Style.RESET_ALL}")
    for n in sorted(ids):
        cwe = f"CWE-{n}"
        print(f"{Fore.CYAN}- {cwe} — NVD: https://nvd.nist.gov/vuln/search/results?form_type=Advanced&search_type=all&cwe_id={cwe}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}- {cwe} — MITRE: https://cwe.mitre.org/data/definitions/{n}.html{Style.RESET_ALL}")
    print()

def obter_diretorio_logs_nvidia():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    return os.path.join(base, "logs", "nvidia", "reports")

def ler_json_log(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

def apresentar_tabela_logs_nvidia():
    pasta = obter_diretorio_logs_nvidia()
    if not os.path.exists(pasta) or not os.listdir(pasta):
        print(Fore.RED + "\n⚠️ Base de dados NVIDIA vazia.")
        return None
    arquivos = [f for f in os.listdir(pasta) if f.endswith('.json')]
    print(f"\n{Fore.GREEN}📋 SELECIONE UM RELATÓRIO GEFORCE SCAN:{Style.RESET_ALL}")
    for i, nome in enumerate(arquivos, 1):
        print(f"{Fore.GREEN}{i}{Style.RESET_ALL} - {nome}")
    try:
        indice = int(input(Fore.GREEN + "Digite o número (0 p/ sair): "))
        return os.path.join(pasta, arquivos[indice - 1]) if indice > 0 else None
    except: return None

def abrir_arquivo_no_editor(caminho_arquivo):
    if not os.path.exists(caminho_arquivo): return
    if os.name == 'nt': os.startfile(caminho_arquivo)
    else: subprocess.run(['xdg-open', caminho_arquivo], check=False)

def navegar_falhas_nvidia(caminho_log):
    dados = ler_json_log(caminho_log)
    if not dados: return
    falhas = dados.get("vulnerabilidades", [])
    
    while True:
        limpar_tela()
        print(f"\n{Fore.GREEN}🟢 ANÁLISE NVIDIA GEFORCE: {dados.get('projeto', 'Desconhecido')}{Style.RESET_ALL}")
        print("=" * 120)
        template = "{:<4} | {:<14} | {:<30} | {:<35}"
        print(Fore.GREEN + Style.BRIGHT + template.format("ID", "SEVERIDADE", "VULNERABILIDADE", "ARQUIVO") + Style.RESET_ALL)
        print("-" * 120)

        for f in falhas:
            sev = str(f.get('severidade', '-')).upper()
            cor = Fore.GREEN if sev in ["CRÍTICO", "ALTO"] else Fore.YELLOW
            print(cor + template.format(
                f.get('indice', '-'), f"🛑 {sev}" if sev in ["CRÍTICO", "ALTO"] else f"🟠 {sev}",
                f.get('tipo', 'Desconhecido')[:30], f.get('arquivo', '-')
            ) + Style.RESET_ALL)

        print("=" * 120)
        opcao = input(f"\n{Fore.GREEN}[ID]{Style.RESET_ALL} Ver Detalhes | {Fore.GREEN}[0]{Style.RESET_ALL} Voltar: ").strip()
        if opcao == '0': break
        
        for f in falhas:
            if str(f.get('indice', '')) == opcao:
                limpar_tela()
                print(Fore.GREEN + Style.BRIGHT + "📋 DETALHES DA FALHA SELECIONADA (MODO NVIDIA GEFORCE)" + Style.RESET_ALL)
                print("=" * 110)
                print(f"{Fore.YELLOW}ID{' ':<16}: {f.get('indice')}")
                print(f"{Fore.GREEN}Severidade{' ':<8}: 🛑 {f.get('severidade')}")
                print(f"{Fore.YELLOW}Tipo{' ':<14}: {f.get('tipo')}")
                print(f"{Fore.YELLOW}Arquivo{' ':<11}: {f.get('arquivo')}")
                print(f"{Fore.YELLOW}Linha{' ':<13}: {f.get('linha')}")
                print(f"{Fore.YELLOW}Padrão{' ':<12}: {f.get('padrao_detectado')}")
                print("-" * 110)
                print(f"\n{Fore.MAGENTA}📖 EXPLICAÇÃO & CORREÇÃO:")
                print(f"{Fore.WHITE}{f.get('descricao')}{Style.RESET_ALL}\n")
                
                referencias = f.get('referencias', [])
                if referencias:
                    print(f"{Fore.WHITE}🔗 REFERÊNCIAS TÉCNICAS:")
                    for ref in referencias:
                        print(f"{Fore.CYAN}- {ref}{Style.RESET_ALL}")
                    print()
                    _imprimir_cves_codigo_e_link(referencias)
                    _imprimir_links_nvd_mitre(referencias)
                
                print(f"{Fore.WHITE}💻 TRECHO DO CÓDIGO:")
                print(f"{Fore.CYAN}Linha {f.get('linha')}: {f.get('codigo').strip()}{Style.RESET_ALL}\n")
                
                abrir_arquivo_no_editor(f.get('caminho_completo'))
                input(Fore.GREEN + "Enter para voltar..." + Style.RESET_ALL)
                break
