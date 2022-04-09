# coding: utf-8
import json

import docker
from celery import chain
from celery.utils.log import get_task_logger

import model
from ow import celery

logger = get_task_logger(__name__)


@celery.task()
def finish_job(job_id):
    logger.info(f"Job with id={job_id} finished !!")
    job = model.Job.query.get(job_id)
    if job.status != "failed":
        job.status = "done"
    model.db.session.commit()


@celery.task()
def process_dockerfile(docker_filepath, job_id):
    logger.info(f"Start processing job with id={job_id}  !!")

    job = model.Job.query.get(job_id)
    job.status = "running"
    model.db.session.commit()

    try:
        image_tag = f"image-{job_id}"
        context_dir = f"/tmp/{job_id}"
        tasks = [
            build_image.si(docker_filepath, image_tag, job_id, context_dir),
            scan_image.si(image_tag, job_id),
            run_image.si(image_tag, job_id),
            finish_job.si(job_id),
        ]
        chain(*tasks).apply_async()
    except Exception as e:
        job.status = "failed"
        job.error = f"{e}"
        logger.error(f"{e}")
        model.db.session.commit()
        raise


@celery.task()
def build_image(docker_filepath, image_tag, job_id, context_dir="/tmp"):
    logger.info(f"Building dockerfile for job with id={job_id}")
    job = model.Job.query.get(job_id)

    try:
        client = docker.from_env()
        client.images.build(
            path=context_dir,
            fileobj=open(docker_filepath, "rb"),
            pull=True,
            tag=image_tag,
        )
        return image_tag
    except Exception as e:
        job.status = "failed"
        job.error = f"{e}"
        logger.error(f"{e}")
        model.db.session.commit()
        raise


@celery.task()
def scan_image(image_tag, job_id):
    logger.info(f"Scanning docker image for job with id={job_id}")
    job = model.Job.query.get(job_id)
    print("scan_image NOT IMPLEMENTED")
    # use docker scan ?


@celery.task()
def run_image(image_tag, job_id):
    logger.info(f"Running docker image for job with id={job_id}")

    job = model.Job.query.get(job_id)
    try:
        client = docker.from_env()
        client.containers.run(
            image_tag, detach=False, volumes=[f"/tmp/{job_id}/data:/data"]
        )
        # Store result perf.json into database
        with open(f"/tmp/{job_id}/data/perf.json", "r") as file:
            job.result = json.load(file)
            model.db.session.commit()
        # remove folder /tmp/{job_id}
    except Exception as e:
        job.status = "failed"
        job.error = f"{e}"
        logger.error(f"{e}")
        model.db.session.commit()
        raise
