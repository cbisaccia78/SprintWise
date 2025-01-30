from flask import Flask

from src.settings import Config
from src.routes.model_routes import model_bp

def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        config = Config()

    app.register_blueprint(model_bp, url_prefix='/models')

    return app

if __name__ == '__main__':
    app = create_app() # need to change to migrations instead of create_app
    app.run()