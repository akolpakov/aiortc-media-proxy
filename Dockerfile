FROM python:3-stretch

RUN apt-get update
RUN apt-get install -y ffmpeg

# Install python requirements

COPY ./requirements.txt  /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy files

RUN mkdir /app
COPY app.py /app/
COPY aiortc_media_proxy /app/aiortc_media_proxy

EXPOSE 80
WORKDIR /app

CMD python /app/app.py
