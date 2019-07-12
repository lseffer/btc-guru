FROM python:3.7-slim

RUN useradd -ms /bin/bash guru \
    && apt-get update \
    && apt-get install -y git netcat build-essential

COPY requirements.txt /requirements.txt
COPY entrypoint.sh /entrypoint.sh

RUN python3 -m pip install -U pip setuptools \
    && python3 -m pip install -U -r /requirements.txt

USER guru
WORKDIR /home/guru
ENV PYTHONPATH="${PYTHONPATH}:/home/guru/btc_guru"

EXPOSE 5001

ENTRYPOINT ["/entrypoint.sh"]
CMD ["jobrunner"]
