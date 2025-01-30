from threading import Thread

from flask import Flask

from src.settings import config
from src.worker import AIWorker
from src.routes.model_routes import model_bp

def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        config = config

    app.register_blueprint(model_bp, url_prefix='/models')

    worker = AIWorker()

    Thread(target=worker.start).start()
    def shutdown_thread():
        worker.stop()  # Assuming the worker has a stop method to terminate the thread gracefully
        worker_thread.join()

    worker_thread = Thread(target=worker)
    worker_thread.start()
    app.teardown_appcontext(lambda exception: shutdown_thread())

    return app

if __name__ == '__main__':
    app = create_app() # need to change to migrations instead of create_app
    app.run()