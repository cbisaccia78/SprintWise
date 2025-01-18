import os

from flask import Flask

from .database import create_db
from .settings import Config

from .routes.task_routes import task_bp

def create_app(config=None):
    app = Flask(__name__)
    
    if not config:
        config = Config()

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    create_db(app)

    app.register_blueprint(task_bp)
    return app