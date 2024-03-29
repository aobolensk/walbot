FROM python:3.11-alpine

WORKDIR /walbot
ADD . /walbot

RUN apk add --no-cache \
    build-base \
    linux-headers \
    bash \
    git \
    ffmpeg
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
