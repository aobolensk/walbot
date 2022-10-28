FROM python:3.11

WORKDIR /walbot
ADD . /walbot

RUN apt-get update
RUN apt-get install ffmpeg --no-install-recommends -y
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
