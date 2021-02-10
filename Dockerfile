# FROM python:3-alpine
# FROM ubuntu:latest
FROM jjanzic/docker-python3-opencv

COPY . /app
WORKDIR /app

# RUN apt update && apt install -y gcc python3 python3-pip

RUN pip3 install -r requirements.txt

EXPOSE 8000

# CMD [ "echo" , "'Hello World'" ]