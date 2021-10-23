FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN echo "INSTALLING requirements\n"

COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 

RUN mkdir /app
WORKDIR /app
COPY ./app /app