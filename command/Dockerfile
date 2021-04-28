FROM python:3.8.5

WORKDIR /code

run pip3 install telegram
run pip3 install python-telegram-bot
run pip3 install pysnmp
run pip3 install PyTelegramBotAPI

ENV TZ="America/Santiago"

COPY switch/ .

CMD [ "python3", "command.py"]
