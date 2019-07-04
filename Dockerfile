FROM python:3.7-slim

RUN useradd -ms /bin/bash guru \
    && apt-get update \
    && apt-get install -y git netcat
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -U pip setuptools \
    && python3 -m pip install -U -r /requirements.txt

USER guru
WORKDIR /home/guru
ENV PYTHONPATH="${PYTHONPATH}:${HOME}"

EXPOSE 5001
