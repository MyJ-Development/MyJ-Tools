FROM python:3.8.5

WORKDIR /code

run pip3 install telegram
run pip3 install python-telegram-bot

ENV TZ="America/Santiago"

COPY ping/ .

CMD [ "python3", "ping.py"]
