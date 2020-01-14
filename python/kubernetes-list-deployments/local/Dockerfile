FROM python:3.6.6-alpine3.8

WORKDIR /app

COPY publish-deployments.py /app
COPY requirements.txt /app

RUN apk --no-cache add \
    build-base \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev && \
    pip install -r requirements.txt

ENTRYPOINT ./publish-deployments.py