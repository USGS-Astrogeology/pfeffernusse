FROM python:3

RUN mkdir -p /usr/src/app
RUN mkdir /var/log/gunicorn
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["gunicorn"]

CMD ["--error-logfile", "-", "--access-logfile", "-", "--capture-output", "--log-level", "debug", "--bind", "0.0.0.0:8080", "-t", "60", "pfeffernusse.wsgi"]
