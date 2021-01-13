FROM python:3.8.5

WORKDIR /code

COPY radius/requirements.txt .
ENV TZ=America/Santiago
run pip3 install -r requirements.txt

COPY radius/ .

CMD [ "python3", "radiussync.py"]
