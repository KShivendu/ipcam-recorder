FROM python:3-alpine

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD [ "echo" , "'Hello World'" ]