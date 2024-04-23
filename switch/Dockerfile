FROM python:3.8.5

WORKDIR /code

run pip3 install telegram
run pip3 install python-telegram-bot==20.0
run pip3 install pysnmp==4.4.12
run pip3 install PyTelegramBotAPI==4.9.0

ENV TZ="America/Santiago"

COPY switch/ .

CMD [ "python3", "switch.py"]
