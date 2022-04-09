# coding: utf-8
import logging
import sys
from logging import config

import celery
import flask_restful
from celery.signals import setup_logging
from flask import Flask
from redis import Redis

app = Flask(__name__)
app.config.from_object("ow.default_settings")


def configure_logger(app):
    """
    initialize logging
    """
    if 'LOGGER' in app.config:
        logging.config.dictConfig(app.config['LOGGER'])
    else:  # Default is std out
        handler = logging.StreamHandler(stream=sys.stdout)
        app.logger.addHandler(handler)
        app.logger.setLevel('INFO')


configure_logger(app)


# we don't want celery to mess with our logging configuration
@setup_logging.connect
def celery_setup_logging(*args, **kwargs):
    pass


app.config["CELERY_TASK_SERIALIZER"] = "json"

if app.config["REDIS_PASSWORD"]:
    app.config["CELERY_RESULT_BACKEND"] = "redis://:%s@%s:%s/%s" % (
        app.config["REDIS_PASSWORD"],
        app.config["REDIS_HOST"],
        app.config["REDIS_PORT"],
        app.config["REDIS_DB"],
    )
else:
    app.config["CELERY_RESULT_BACKEND"] = "redis://@%s:%s/%s" % (
        app.config["REDIS_HOST"],
        app.config["REDIS_PORT"],
        app.config["REDIS_DB"],
    )

from model import db

db.init_app(app)


def make_celery(app):
    celery_app = celery.Celery(app.import_name, broker=app.config["CELERY_BROKER_URL"])
    celery_app.conf.update(app.config)
    TaskBase = celery_app.Task

    class ContextTask(TaskBase):
        abstract = True

        def __init__(self):
            pass

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app


api = flask_restful.Api(app, catch_all_404s=True)
celery = make_celery(app)

redis = Redis(
    host=app.config["REDIS_HOST"],
    port=app.config["REDIS_PORT"],
    db=app.config["REDIS_DB"],
    password=app.config["REDIS_PASSWORD"],
)


from ow import views
