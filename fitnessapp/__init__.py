import os
import logging
from flask import Flask
from flask_mail import Mail
from flask_pymongo import PyMongo
from oauthlib.oauth2 import WebApplicationClient

from .insert_db_data import insertexercisedata, insertfooddata
from dotenv import load_dotenv
from celery import Celery, Task

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)



def make_celery(app) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app(test_config=None):
    # Create and configure the app
    load_dotenv()
    app = Flask(__name__, template_folder='templates')
    app.secret_key = 'secret'

    # MongoDB Configuration
    app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/test'
    app.config['MONGO_CONNECT'] = False
    mongo = PyMongo(app)
    app.mongo = mongo

    # Mail Configuration
    app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER", None)
    app.config['MAIL_PORT'] = os.environ.get("MAIL_PORT", None)
    app.config['MAIL_USE_SSL'] = os.environ.get("MAIL_USE_SSL", True)
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME", None)
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD", None)

    # Google OAuth Configuration
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID", None)
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    app.config['GOOGLE_DISCOVERY_URL'] = os.environ.get("GOOGLE_DISCOVERY_URL", None)
    app.config['GOOGLE_SIGN_IN_REDIRECT_URI'] = os.environ.get("GOOGLE_SIGN_IN_REDIRECT_URI", None)

    mail = Mail(app)
    app.mail = mail

    # OAuth Client Setup
    oauthclient = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])
    app.oauthclient = oauthclient

    # Insert Data into Database
    insertfooddata()
    insertexercisedata()

    # Register Blueprints
    from . import application
    from .views import auth
    app.register_blueprint(application.bp)
    app.register_blueprint(auth.bp)

    # Celery Configuration
    app.config.from_mapping(
    CELERY=dict(
        broker_url='amqp://guest:guest@localhost//',  # RabbitMQ broker URL
        result_backend='rpc://',  # Use RPC for result backend
    ),
    )
   
    celery = make_celery(app)  # Initialize Celery with the app
   
    celery.autodiscover_tasks(['fitnessapp'])
    
    celery.conf.update(app.config)

    celery.conf.timezone = 'America/New_York'
    celery.conf.beat_schedule = {
        'send-task-reminder-email-every-5-seconds': {
            'task': 'fitnessapp.tasks.send_task_reminder_email',  # Adjust the path as needed
            'schedule': 5.0,  # Runs every 5 seconds
        },
    }


    return app
