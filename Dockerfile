FROM python:3.6-slim-jessie

RUN apt-get update && apt-get -y install binutils gcc make

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["python"]

CMD ["-m", "pfeffernusse"]
