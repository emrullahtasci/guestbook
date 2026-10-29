import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask

from .models import db
from .routes import bp


def setup_logging(app):
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"), maxBytes=1_000_000, backupCount=3
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    # Flask reuses the same logger object, so drop a handler left by an earlier app
    for old in [h for h in app.logger.handlers if isinstance(h, RotatingFileHandler)]:
        app.logger.removeHandler(old)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)


def create_app(config=None):
    app = Flask(__name__)
    # Needed for flash messages; set a real value in .env outside local dev
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///messages.db"
    )
    if config:
        app.config.update(config)

    setup_logging(app)
    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    app.logger.info("Application started")
    return app
