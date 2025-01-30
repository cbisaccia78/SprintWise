from threading import Thread

from flask import Flask

from .database import create_db
from .settings import config
from .worker import TaskWorker

from .routes.task_routes import task_bp
from .routes.project_routes import project_bp

def create_app(config=None):
    app = Flask(__name__)
    
    if not config:
        config = config

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    create_db(app)

    app.register_blueprint(task_bp, url_prefix='/tasks')
    app.register_blueprint(project_bp, url_prefix='/projects')

    worker = TaskWorker()

    worker_thread = Thread(target=worker.start).start()

    def shutdown_thread():
        worker.stop()
        worker_thread.join()

    app.teardown_appcontext(lambda exception: shutdown_thread())

    return app