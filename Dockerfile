FROM python:3.8

WORKDIR /walbot
ADD . /walbot

RUN python3 -m pip install -r requirements.txt
