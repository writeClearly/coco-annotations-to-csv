FROM python:3.9-slim as build

ARG APP_PATH=/usr/local/app
ARG VENV_PATH=${APP_PATH}/env

WORKDIR ${APP_PATH}
ENV PATH="${VENV_PATH}/bin:$PATH"
COPY requirements.txt .
RUN python -m venv ${VENV_PATH}
RUN pip install --upgrade pip && \
    pip install --no-cache --upgrade \
    setuptools wheel &&     \
    pip install --no-cache -r ${APP_PATH}/requirements.txt


FROM python:3.9-slim 

ARG APP_PATH=/usr/local/app
ARG VENV_PATH=${APP_PATH}/env

WORKDIR ${APP_PATH}
COPY --from=build ${VENV_PATH} ${VENV_PATH}
COPY coco2csv .

ENV PATH="${VENV_PATH}/bin:${APP_PATH}:$PATH"
