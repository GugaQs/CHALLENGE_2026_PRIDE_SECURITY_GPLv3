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

"""Fabrica da aplicacao Flask — apenas funcoes."""

import os
import sys
import traceback

# Permite executar este arquivo diretamente no Windows/Powershell sem quebrar imports.
if __name__ == "__main__":
    raiz_projeto = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if raiz_projeto not in sys.path:
        sys.path.insert(0, raiz_projeto)

from flask import Flask, got_request_exception
from flask_wtf.csrf import CSRFProtect

from app.utils.log_sistema import get_logger
from app.web.routes.documentacao_routes import documentacao_bp
from app.web.routes.ia_local_routes import ia_local_bp
from app.web.routes.log_routes import log_bp
from app.web.routes.main_routes import main_bp
from app.web.routes.modulos_routes import modulos_bp
from app.web.routes.scan_routes import scan_bp
from app.web.routes.sobre_routes import sobre_bp


def create_app():
    """Cria e registra blueprints da aplicacao web."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "aspm-pride-2026-dev")
    CSRFProtect(app)
    logger_sistema = get_logger("aspm_web")

    app.register_blueprint(main_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(sobre_bp)
    app.register_blueprint(ia_local_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(modulos_bp)
    app.register_blueprint(documentacao_bp)

    @app.context_processor
    def util_templates():
        """Disponibiliza helper para versionar assets estaticos por mtime."""

        def asset_version(caminho_relativo):
            caminho = os.path.join(app.static_folder, caminho_relativo)
            try:
                return int(os.path.getmtime(caminho))
            except OSError:
                return 1

        return {"asset_version": asset_version}

    def registrar_excecao(sender, exception, **extra):  # pylint: disable=unused-argument
        logger_sistema.exception(
            "Erro Flask: %s\n%s",
            exception,
            traceback.format_exc(),
        )

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https://img.shields.io; "
            "connect-src 'self'; "
            "worker-src blob: 'self';"
        )
        return response

    got_request_exception.connect(registrar_excecao, app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)
