from threading import Thread
import atexit

from flask import Flask

from src.settings import config as cfg
from src.worker import TaskCreatedConsumer
from src.routes.model_routes import model_bp

def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        config = cfg

    app.register_blueprint(model_bp, url_prefix='/models')

    if not config.testing:
        worker = TaskCreatedConsumer()
        worker_thread = Thread(target=worker.start)
        worker_thread.start()

        def shutdown_thread():
            worker.stop()  # Assuming the worker has a stop method to terminate the thread gracefully
            worker_thread.join()

        
        atexit.register(shutdown_thread)

    return app

app = create_app()
