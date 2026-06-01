"""Flask application factory."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

db = SQLAlchemy()


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application.

    Parameters
    ----------
    config_name : str | None
        One of 'development', 'production', or None (uses 'default').

    Returns
    -------
    Flask
        The configured Flask application instance.
    """
    flask_app = Flask(__name__)

    # Load configuration
    config_name = config_name or 'default'
    flask_app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(flask_app)

    # Enable CORS for frontend dev server (Vite :5173)
    CORS(flask_app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

    # Register models with SQLAlchemy (import side-effect)
    with flask_app.app_context():
        import app.models  # noqa: F401

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.recipe_search import recipe_bp
    from app.routes.blindbox import blindbox_bp
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(recipe_bp)
    flask_app.register_blueprint(blindbox_bp)

    return flask_app
