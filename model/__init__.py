# encoding: utf-8

from datetime import datetime

import flask_sqlalchemy
from sqlalchemy.dialects.postgresql import INTERVAL


class SQLAlchemy(flask_sqlalchemy.SQLAlchemy):
    def init_app(self, app):
        super(SQLAlchemy, self).init_app(app)
        app.config.setdefault("SQLALCHEMY_POOLCLASS", None)

    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(app, options)

        options["pool_pre_ping"] = True

        def _setdefault(optionkey, configkey):
            value = app.config[configkey]
            if value is not None:
                options[optionkey] = value

        _setdefault("poolclass", "SQLALCHEMY_POOLCLASS")
        return options


db = SQLAlchemy()  # type: SQLAlchemy


class TimestampMixin(object):
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), default=None, onupdate=datetime.utcnow)


class Job(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    task_uuid = db.Column(db.Text)
    status = db.Column(
        db.Enum("pending", "running", "done", "failed", name="job_state")
    )
    result = db.Column(db.JSON)
    error = db.Column(db.Text)

    # metrics = db.relationship('Metric', backref='job', lazy='dynamic', cascade='delete')

    def __repr__(self):
        return "<Job %r>" % self.id

    @classmethod
    def get(cls, id=None):
        if id:
            return cls.query.filter_by(id=id).first()
        return cls.query.all()


class Metric(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    duration = db.Column(INTERVAL)

    def __repr__(self):
        return "<Metric {}>".format(self.id)
