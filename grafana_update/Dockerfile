FROM python:3.8.5

WORKDIR /code

run pip3 install mysql.connector
run pip3 install requests

ENV TZ="America/Santiago"

COPY grafana_update/ .

CMD [ "python3", "grafana_update.py"]
