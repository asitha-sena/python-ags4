FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install python-ags4

RUN ags4_cli check --help

COPY ./app /app

