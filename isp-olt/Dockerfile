FROM python:3.8.5

WORKDIR /code

COPY src/requirements.txt .

run pip3 install -r requirements.txt

COPY src/ .

CMD [ "python3", "ispolt.py"]
