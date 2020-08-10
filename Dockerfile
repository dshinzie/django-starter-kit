FROM python:3.7-stretch

ENV PORT=8080

ENV PATH /env/bin:$PATH

RUN apt-get update
RUN apt-get install -y vim net-tools

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
ADD . /app

WORKDIR /app/starterkit

ARG APP_VERSION
RUN echo "# File managed by Dockerfile" > version.py
RUN echo "APP_VERSION='${APP_VERSION}'" >> version.py

EXPOSE ${PORT}
CMD ["sh", "-c", "gunicorn -c gunicorn.conf.py starterkit.asgi"]
