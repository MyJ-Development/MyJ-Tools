FROM python:3.10.6

WORKDIR .

run pip3 install mysql-connector-python

ENV TZ="America/Santiago"

COPY . .

CMD [ "python3", "log_mikrotik.py"]
