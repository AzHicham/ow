# encoding: utf-8

import os

CELERY_BROKER_URL = os.getenv(
    "OW_CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//"
)

SQLALCHEMY_DATABASE_URI = "postgresql://ow:ow@localhost:5432/ow"
SQLALCHEMY_TRACK_MODIFICATIONS = False

REDIS_HOST = os.getenv("OW_REDIS_HOST", "localhost")
REDIS_PORT = 6379
# index of the database use in redis, between 0 and 15 by default
REDIS_DB = 0
REDIS_PASSWORD = None

# configuration of celery, don't edit
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"

UPLOAD_FOLDER = "/tmp"

# logger configuration
LOGGER = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)5s] [%(process)5s] [%(name)25s] %(message)s"
        },
        "instance": {
            "format": "%(name)s: [%(asctime)s] [%(levelname)5s] [%(process)5s] [%(task_id)s] %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG"},
        "celery": {"level": "INFO"},
        "sqlalchemy.engine": {
            "handlers": ["default"],
            "level": "WARN",
            "propagate": True,
        },
        "sqlalchemy.pool": {
            "handlers": ["default"],
            "level": "WARN",
            "propagate": True,
        },
        "sqlalchemy.dialects.postgresql": {
            "handlers": ["default"],
            "level": "WARN",
            "propagate": True,
        },
    },
}
