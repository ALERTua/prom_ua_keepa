FROM python:3
MAINTAINER Alexey Rubasheff <alexey.rubasheff@gmail.com>

ENV DELAY_SEC=""
ENV TELEGRAM_CHAT_ID=""
ENV TELEGRAM_BOT_API_KEY=""

COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

COPY prom_ua_keepa /app

WORKDIR /app

CMD [ "python", "__main__.py"]