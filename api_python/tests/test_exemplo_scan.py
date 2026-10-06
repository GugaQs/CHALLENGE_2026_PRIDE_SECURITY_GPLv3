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
Testes de exemplo (didaticos) — alinhados ao documento Analise_ASPM_Pride_2026.

Como executar (na pasta api_python):
    pip install pytest
    pytest tests/test_exemplo_scan.py -v

Estes testes verificam comportamentos basicos do motor de scan sem precisar
de rede ou banco de dados.
"""

from pathlib import Path

import pytest

# Import apos garantir que o pacote app esta no path (rode pytest da pasta api_python).
from app.ui.scan_projeto.executar_scan import rodar_engine_scan


def test_scan_gera_relatorio_quando_ha_arquivo_compativel(tmp_path):
    """
    Cenario feliz: projeto minimo com arquivo .py que dispara uma assinatura conhecida.

    O scan grava JSON em app/ui/scan_projeto/logs/ e devolve o caminho string.
    """
    projeto = tmp_path / "projeto_minimo"
    projeto.mkdir()
    # Credenciais hardcoded sao uma assinatura das regras (exemplo didatico).
    arquivo_py = projeto / "config.py"
    arquivo_py.write_text('password = "nao_faca_isso_em_producao"\n', encoding="utf-8")

    resultado = rodar_engine_scan(str(projeto))

    assert resultado is not None, "Deveria retornar caminho do JSON gerado"
    assert resultado.endswith(".json"), "Extensao esperada para o relatorio"
    assert Path(resultado).is_file(), "Arquivo de log deve existir no disco"


def test_scan_retorna_none_sem_arquivos_analisaveis(tmp_path):
    """
    Se nao ha .py/.js/etc. no projeto (conforme extensoes permitidas),
    o motor nao gera relatorio e retorna None.
    """
    vazio = tmp_path / "so_txt"
    vazio.mkdir()
    (vazio / "readme.txt").write_text("sem codigo compativel", encoding="utf-8")

    resultado = rodar_engine_scan(str(vazio))

    assert resultado is None


def test_scan_rejeita_projeto_inexistente(tmp_path):
    """
    Documento sugere validacao de caminho — aqui o motor recebe string do usuario.
    rodar_engine_scan pode falhar silenciosamente ao dar os.walk; este teste documenta
    que caminho invalido deve ser tratado na UI (menu ja usa os.path.exists).

    Nota: se os.walk nao encontra arquivos, retorna None (mesmo que pasta exista).
    """
    caminho_falso = str(tmp_path / "nao_existe_xyz")
    resultado = rodar_engine_scan(caminho_falso)
    assert resultado is None
