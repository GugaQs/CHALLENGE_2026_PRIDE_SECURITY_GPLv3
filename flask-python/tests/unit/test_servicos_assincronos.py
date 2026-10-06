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

"""Testes unitarios dos servicos assincronos web."""

from app.web.services import ia_local_service, modulos_service, scan_service


def test_scan_background_conclui_com_redirect(tmp_path, monkeypatch):
    """Worker de scan salva status concluido e URL de redirecionamento."""
    log_path = tmp_path / "report_01.json"
    log_path.write_text("{}", encoding="utf-8")
    atualizacoes = []

    def falso_engine(_caminho, progress_callback=None, silent=False):
        assert silent is True
        if progress_callback:
            progress_callback({"percentual": 30, "mensagem": "fase 1"})
        return str(log_path)

    monkeypatch.setattr(scan_service, "rodar_engine_scan", falso_engine)
    monkeypatch.setattr(
        scan_service, "atualizar_job", lambda _job_id, payload: atualizacoes.append(payload)
    )

    scan_service._executar_scan_background("job_scan", str(tmp_path))

    assert any(item.get("percentual") == 30 for item in atualizacoes)
    final = atualizacoes[-1]
    assert final["status"] == "concluido"
    assert final["nome_log"] == "report_01.json"
    assert final["redirect_url"] == "/scan/logs/report_01.json"


def test_cognitivo_background_progressao_em_duas_fases(tmp_path, monkeypatch):
    """Cognitivo evolui de scan para IA e encerra com sucesso."""
    log_json = tmp_path / "gpu_report.json"
    log_json.write_text("{}", encoding="utf-8")
    parecer_md = tmp_path / "gpu_report_AI_PREMIUM.md"
    parecer_md.write_text("# Parecer", encoding="utf-8")
    atualizacoes = []

    def falso_rodar_motor(_hardware, _caminho, progress_callback=None, silent=False):
        assert silent is True
        if progress_callback:
            progress_callback({"percentual": 50, "atual": 5, "total": 10, "mensagem": "scan"})
        return str(log_json)

    monkeypatch.setattr(ia_local_service, "_rodar_motor_gpu", falso_rodar_motor)
    monkeypatch.setattr(
        ia_local_service,
        "analisar_relatorio_ia",
        lambda _json: (True, "ok", str(parecer_md), None),
    )
    monkeypatch.setattr(
        ia_local_service,
        "atualizar_job",
        lambda _job_id, payload: atualizacoes.append(payload),
    )

    ia_local_service._executar_cognitivo_background("job_ia", "amd", str(tmp_path))

    assert any(item.get("percentual") == 42 for item in atualizacoes)
    assert any(item.get("percentual") == 90 for item in atualizacoes)
    final = atualizacoes[-1]
    assert final["status"] == "concluido"
    assert final["percentual"] == 100
    assert final["redirect_url"].endswith("/gpu_report_AI_PREMIUM.md")


def test_scan_docker_background_preenche_extra(monkeypatch):
    """Worker de containers persiste artefatos no campo extra."""
    atualizacoes = []
    artefatos = [{"nome": "Dockerfile", "caminho_relativo": "Dockerfile"}]

    monkeypatch.setattr(
        modulos_service,
        "executar_scan_containers",
        lambda _caminho, progress_callback=None: (True, "ok", artefatos),
    )
    monkeypatch.setattr(
        modulos_service, "atualizar_job", lambda _job_id, payload: atualizacoes.append(payload)
    )

    modulos_service._scan_docker_background("job_docker", ".")

    final = atualizacoes[-1]
    assert final["status"] == "concluido"
    assert final["percentual"] == 100
    assert final["extra"] == {"artefatos": artefatos}
