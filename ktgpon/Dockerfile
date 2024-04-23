FROM python:3.10.6

WORKDIR /code

run pip3 install mysql-connector-python

ENV TZ="America/Santiago"

COPY vrm/ .

CMD [ "python3", "ktgpon_sync.py"]
