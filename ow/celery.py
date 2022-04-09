# coding: utf-8

import flask_restful
from celery.signals import setup_logging
from flask import Flask
from flask_script import Manager
from redis import Redis

from ow import app


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


celery = make_celery(app)
