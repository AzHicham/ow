# OW

Ow is a web app (REST API) that allow scanning, building & running of Dockerfile.

## API
### /endpoints

#### Get list of jobs
Retrieve a list of jobs regardless of their status ('pending', 'running', 'failed', 'done')
You can also pass an id [int] to retrieve a specific job

    GET /v0/jobs/<id> [id: optional int]
    return {"jobs": [{"id": 1, "job_status": "done", "error": null, "result": {"perf": 0.99}}]}

#### Submit a Dockerfile (scan, build, run)


    POST /v0/jobs
    return {"job": {"id": 1, "status": "pending"}}

##### How to upload Docker file with curl

    curl -F "file=@Dockerfile_test"  http://localhost:5009/v0/jobs


## Settings

You can edit settings ie. postgresql, redis, rabbitmq config in ./ow/default_dettings.py


## How to run
Note: Use Flask only for dev purpose, for 'prod' usage switch to UWSGI

Start docker-compose (if you do not have  local RabbitMq, Redis, Postgres DB)

    cd /path/to/ow
    docker-compose up -d # Run RabbitMq, Redis, Postgres

Init python env

    cd /path/to/ow
    python3 -m venv env # make a virtual env
    source env/bin/activate # activate env
    pip install -r requirements.txt # Install dependencies

Init Database

    cd /path/to/ow
    alembic upgrade head

Start Celery workers

    cd /path/to/ow
    celery -A ow.celery worker # run celery workers

Start Ow App (in another terminal)

    cd /path/to/ow
    FLASK_APP=ow:app PYTHONPATH=. flask run --host=0.0.0.0 -p 5009 # Run Ow web app

Congrats :)


Phase development
