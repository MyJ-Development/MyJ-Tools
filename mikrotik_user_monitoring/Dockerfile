FROM python:3.10.6

WORKDIR .

COPY . .

run pip3 install mysql-connector-python
run pip3 install telegram
run pip3 install python-telegram-bot
run pip3 install PyTelegramBotAPI

ENV TZ="America/Santiago"

CMD [ "python3", "mikrotik_user_monitoring.py"]