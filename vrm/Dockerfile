FROM python:3.8.5

WORKDIR /code

run pip3 install telegram
run pip3 install python-telegram-bot
run pip3 install pysnmp
run pip3 install PyTelegramBotAPI
run pip3 install asterisk
run pip3 install asterisk-ami

ENV TZ="America/Santiago"

COPY vrm/ .

CMD [ "python3", "vrm-monitor.py"]
