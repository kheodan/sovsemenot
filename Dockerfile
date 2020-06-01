FROM python:3.6.10-alpine3.10

WORKDIR /opt

COPY app.py /opt
COPY requirements.txt /opt

RUN apk add build-base &&  pip install -r requirements.txt

CMD python app.py -t $TOKEN -c $CHANNEL -e $EXCLUDE
