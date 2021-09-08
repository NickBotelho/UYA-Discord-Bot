FROM python:3.8-slim-buster as build-image

ARG FUNCTION_DIR=/code
RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

RUN pip install -r requirements.txt

CMD python main.py
