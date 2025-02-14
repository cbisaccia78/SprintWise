from threading import Thread

from flask import Flask

from src.database import create_db
from src.settings import config as cfg
from src.worker import EstimateCompleteConsumer

from src.routes.task_routes import task_bp
from src.routes.project_routes import project_bp

def create_app(config=None):
    app = Flask(__name__)
    
    if not config:
        config = cfg

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    create_db(app)

    app.register_blueprint(task_bp, url_prefix='/tasks')
    app.register_blueprint(project_bp, url_prefix='/projects')
    if not config.testing:
        worker = EstimateCompleteConsumer()

        worker_thread = Thread(target=worker.start)

        def shutdown_thread():
            worker.stop()
            worker_thread.join()
        
        worker_thread.start()
        app.teardown_appcontext(lambda exception: shutdown_thread())

    return app

app = create_app()