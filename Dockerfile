FROM ubuntu:latest
FROM python:3.8
RUN apt-get update
RUN yes | apt-get install tesseract-ocr
RUN yes | apt-get install libtesseract-dev
COPY requirements.txt /tmp

WORKDIR /tmp
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY *.gz /tmp

RUN pip install en_core_web_sm-3.0.0.tar.gz
WORKDIR /home/TTRecord

COPY Bloomberg.py /home/TTRecord/
COPY Savills.py /home/TTRecord/
COPY Elcomercio.py /home/TTRecord
COPY HelperFunctions.py /home/TTRecord
COPY Urcacp.py /home/TTRecord
COPY config.yaml /home/TTRecord
