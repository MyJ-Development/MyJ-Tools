FROM python:3.10.6

WORKDIR .

COPY . .

run pip3 install mysql-connector-python

ENV TZ="America/Santiago"

CMD [ "python3", "ktepon_sync.py"]