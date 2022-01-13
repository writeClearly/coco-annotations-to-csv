FROM python:3.9-slim

ARG APP_PATH=/usr/local/app
ARG VENV_PATH=${APP_PATH}/env

WORKDIR ${APP_PATH}

RUN python -m venv ${VENV_PATH}

COPY requirements.txt coco2csv ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir  \
    setuptools wheel
RUN pip install --no-cache -r ${APP_PATH}/requirements.txt
ENV PATH="${VENV_PATH}/bin:${APP_PATH}:$PATH"

# coco2csv -s http://localhost:8000/slim_coco.zip -d $(pwd)