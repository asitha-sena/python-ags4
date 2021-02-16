FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip install python-ags4

COPY ./app /app

