FROM python:3.9.2-alpine3.12

RUN pip3 install --no-cache --upgrade twilio

COPY main.py /

ENTRYPOINT ["/usr/local/bin/python3", "main.py"]