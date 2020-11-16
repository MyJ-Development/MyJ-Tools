FROM python:3.8.5

WORKDIR /code

COPY deudores/requirements.txt .
ENV TZ=America/Santiago
run pip3 install -r requirements.txt

COPY deudores/ .

CMD [ "python3", "deudores.py"]
