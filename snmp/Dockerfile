FROM python:3.8.5

WORKDIR /code

run pip3 install pysnmp

ENV TZ="America/Santiago"

COPY snmp/ .

CMD [ "python3", "snmp.py"]
