FROM python:3.10.6

WORKDIR .

COPY . .

run pip3 install mysql-connector-python
run pip3 install laiarturs-ros-api

ENV TZ="America/Santiago"

CMD [ "python3", "mikrotik_olt_sync.py"]