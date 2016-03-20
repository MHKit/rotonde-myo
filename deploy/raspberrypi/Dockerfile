FROM resin/raspberrypi-python:latest

RUN sudo apt-get update && \
    sudo apt-get -y upgrade && \
    sudo apt-get install unzip && \
    sudo apt-get install libevent-dev && \
    sudo apt-get install python-all-dev && \
    pip install websocket-client && \
    pip install enum && \
    pip install PySerial

ADD https://github.com/MHKit/rotonde-pyoconnect/archive/master.zip /tmp
RUN unzip /tmp/master.zip -d /usr/local/ && mv /usr/local/rotonde-pyoconnect-master /usr/local/rotonde-pyoconnect


WORKDIR "/usr/local/rotonde-pyoconnect/"
CMD ["/usr/local/bin/python", "main.py"]
