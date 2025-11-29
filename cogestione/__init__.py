
import os
import dotenv
from datetime import timedelta
from flask import Flask

DB_NAME = f"{__name__}.sqlite"

def create_app():

    app = Flask(__name__, instance_relative_config=True)

    app.template_folder = os.path.join(app.root_path, "templates")
    app.static_folder = os.path.join(app.root_path, "static")

    project_root = os.path.dirname(app.root_path)
    # upload_folder = os.path.join(project_root, 'uploads')

    dotenv.load_dotenv()
    app.config.from_mapping(
        SECRET_KEY = os.getenv("secret_key"),
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}",
        # UPLOAD_FOLDER = upload_folder,
    )
    app.permanent_session_lifetime = timedelta(days=7)

    os.makedirs(app.instance_path, exist_ok=True)
    # os.makedirs(upload_folder, exist_ok=True)

    # with app.app_context():
    #     from flaskr.db import init_app
    #     init_app(app)

    # from . import auth

    # app.register_blueprint(auth.bp)

    @app.route("/ping")
    def ping():
        return "pong"

    return app
