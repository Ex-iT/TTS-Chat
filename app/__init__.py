from flask import Flask
from flask_cors import CORS
from flask_squeeze import Squeeze

from app.config import config
from app.routes.api import bp as api_bp
from app.routes.main import bp as main_bp

squeeze = Squeeze()

def create_app():
    app = Flask(__name__, static_folder=str(config.STATIC_DIR), static_url_path="")
    CORS(app)
    squeeze.init_app(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)

    return app
