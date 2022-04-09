# coding: utf-8

import os

import flask_restful
from flask import request
from werkzeug.utils import secure_filename

import model
from ow import app
from ow.tasks import process_dockerfile


class Index(flask_restful.Resource):
    def get(self):
        response = "API v0"
        return response


class Status(flask_restful.Resource):
    def get(self):
        return {"status": "ok"}


class Job(flask_restful.Resource):
    def get(self, id=None):
        app.logger.info(f'Call on endpoint /job with id={id}')

        query = model.Job.query
        if id:
            query = query.filter(model.Job.id == id)
        jobs = query.order_by(model.Job.created_at.desc())
        jobs = [
            {
                "id": job.id,
                "job_status": job.status,
                "error": job.error,
                "result": job.result,
            }
            for job in jobs
        ]
        return {"jobs": jobs}, 200

    def post(self):
        job = model.Job()
        job.status = "pending"
        model.db.session.add(job)
        model.db.session.commit()

        try:
            file = request.files["file"]
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
        except Exception as e:
            job.status = "failed"
            job.error = f"{e}"
            app.logger.error(f"{e}")
            model.db.session.commit()
            return {"error": f"{e}"}, 500

        process_dockerfile.si(filepath, job.id).delay()
        return {"job": {"id": job.id, "status": job.status}}, 200
