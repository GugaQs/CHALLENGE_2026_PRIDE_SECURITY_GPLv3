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

import os
import unittest
import json
import shutil
from app.ui.scan_ia_local.scan_amd.executar_scan import salvar_log_json_amd
from app.ui.scan_ia_local.scan_nvidia.executar_scan import salvar_log_json_nvidia
from app.ui.scan_projeto.executar_scan import salvar_log_json

class TestScanEnginesIntegration(unittest.TestCase):
    def setUp(self):
        self.mock_data = {"test": True, "integration_test": "v1"}
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def test_salvar_log_json_amd_path(self):
        """Verifica se o motor AMD salva no novo path centralizado."""
        caminho = salvar_log_json_amd(self.mock_data)
        self.assertTrue(os.path.isabs(caminho))
        self.assertIn(os.path.join("logs", "amd", "reports"), caminho)
        self.assertTrue(os.path.exists(caminho))
        # Limpeza
        os.remove(caminho)

    def test_salvar_log_json_nvidia_path(self):
        """Verifica se o motor NVIDIA salva no novo path centralizado."""
        caminho = salvar_log_json_nvidia(self.mock_data)
        self.assertTrue(os.path.isabs(caminho))
        self.assertIn(os.path.join("logs", "nvidia", "reports"), caminho)
        self.assertTrue(os.path.exists(caminho))
        # Limpeza
        os.remove(caminho)

    def test_salvar_log_json_generic_path(self):
        """Verifica se o motor padrao salva no novo path centralizado generic."""
        caminho = salvar_log_json(self.mock_data)
        self.assertTrue(os.path.isabs(caminho))
        self.assertIn(os.path.join("logs", "generic", "reports"), caminho)
        self.assertTrue(os.path.exists(caminho))
        # Limpeza
        os.remove(caminho)

if __name__ == "__main__":
    unittest.main()
