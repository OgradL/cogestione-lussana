
import os
import dotenv
from datetime import timedelta
from flask import Flask

DB_NAME = f"{__name__}.sqlite"

def create_app():

    app = Flask(__name__, instance_relative_config=True)

    app.template_folder = os.path.join(app.root_path, "templates")
    app.static_folder = os.path.join(app.root_path, "static")


    dotenv.load_dotenv()
    app.config.from_mapping(
        SECRET_KEY = os.getenv("secret_key"),
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}",
    )
    app.permanent_session_lifetime = timedelta(days=7)

    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        from cogestione.db import init_app
        init_app(app)

    from . import auth
    from . import core
    from . import admin

    app.register_blueprint(auth.bp)
    app.register_blueprint(core.bp)
    app.register_blueprint(admin.bp)

    @app.route("/ping")
    def ping():
        return "pong"

    return app
