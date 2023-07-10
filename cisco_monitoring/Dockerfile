FROM python:3.8.5

WORKDIR /code

run pip3 install telegram
run pip3 install python-telegram-bot

ENV TZ="America/Santiago"

COPY cisco_monitoring/ .

CMD [ "python3", "cisco_monitoring.py"]
