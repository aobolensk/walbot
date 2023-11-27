FROM python:3.11

WORKDIR /walbot
ADD . /walbot

RUN apt-get update && \
    apt-get install ffmpeg --no-install-recommends -y && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements-extra.txt
