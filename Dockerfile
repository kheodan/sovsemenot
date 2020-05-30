FROM python:3.6.10-alpine3.10

ADD app.py /opt

RUN apk add build-base && pip install discord.py==0.16.12 asyncio aiohttp==1.0.5

WORKDIR /opt

CMD [ "python3", "app.py" ]
