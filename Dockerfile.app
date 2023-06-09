FROM python:3.11-rc-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
# install mysql  client
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade setuptools
RUN pip install --no-cache-dir --upgrade pip
USER root
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
EXPOSE 8000
ENV LISTEN_PORT=8000

CMD ["sh", "-c", "/app/nuclei_backend/storage_service/ipfs daemon --init --enable-pubsub-experiment 2>&1 | tee ipfs.log & uvicorn nuclei_backend:app --host=0.0.0.0 --port=8000 --workers=4"]
