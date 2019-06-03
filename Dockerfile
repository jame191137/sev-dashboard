FROM python:2.7

ADD . /code
WORKDIR /code

RUN apt update
RUN apt install -y mongodb
RUN mkdir -p /data/db
RUN chown -R `id -un` /data/db

ADD requirements.txt /code
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install mysql-client
RUN pip install -r requirements.txt
ENV ISENV=pro
EXPOSE 7000
CMD ["python","app.py"]
