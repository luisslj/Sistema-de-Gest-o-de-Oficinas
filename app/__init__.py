import os
import secrets

from flask import Flask

from .database import init_app
from .routes import main


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=app.instance_path + "/participantes.sqlite3",
    )
    if test_config is not None:
        app.config.update(test_config)
    init_app(app)
    app.register_blueprint(main)
    return app
