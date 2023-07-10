FROM python:3.11.4

WORKDIR /code

run pip3 install telegram
run pip3 install python-telegram-bot

ENV TZ="America/Santiago"

COPY cisco_monitoring/ .


# Cmd ls
CMD [ "python", "cisco_monitoring.py"]
