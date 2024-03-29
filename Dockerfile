FROM python:3.8.5

RUN apt-get update && apt-get install -y nmap vim

WORKDIR /code
COPY . /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000