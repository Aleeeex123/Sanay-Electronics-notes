from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.db import init_db, close_db
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app