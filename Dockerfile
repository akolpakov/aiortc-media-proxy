FROM python:3

RUN apt-get update && apt-get install -y \
    libavdevice-dev \
    libavfilter-dev \
    libopus-dev \
    libvpx-dev pkg-config

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
