FROM python:3.11

WORKDIR /walbot
ADD . /walbot

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt
