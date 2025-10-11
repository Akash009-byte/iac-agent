# agent prototype

This is a fastapi prototype generated using WeDAA, you can find documentation and help at [WeDAA Docs](https://www.wedaa.tech/docs/introduction/what-is-wedaa/)

## Prerequisites

- python version >= 3

## Project Structure

## Dependencies

This application is configured to work with external component(s).

Docker compose files are provided for the same to get started quickly.

Component details:

- mongoDB: `docker compose -f docker/mongodb.yml up -d`

On launch, agent will refuse to start if it is not able to connect to any of the above component(s).

## Get Started

Run the `./start.sh` script to quickly get started.

Or

Manually Step:

1. Create a new virtual env

```
python -m venv .venv
```

2. Activate the virtual environment

```
source .venv/bin/activate
```

3. Install the requirements for project

```
pip install -r requirements.txt
```

4. Enter the `app/` directory, Run the FastAPI application:

```
gunicorn -c gunicorn_dev_config.py main:app
```

Open [http://localhost:5001/management/health/readiness](http://localhost:5001/management/health/readiness) to view it in your browser.

## Containerization

Build the docker image: `docker build -t agent:latest .`

Start the container: `docker run -d -p 5001:5001 agent:latest`
