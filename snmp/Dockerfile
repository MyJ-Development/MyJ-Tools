FROM python:3.8.5

WORKDIR /code

run apt-get update && apt-get -y install libsnmp-dev
run pip3 install pysnmp
run pip3 install mysql.connector
run pip3 install easysnmp
run pip3 install requests

ENV TZ="America/Santiago"

COPY snmp/ .

CMD [ "python3", "snmp_test.py"]
