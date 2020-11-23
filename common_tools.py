import os
import re
import requests
from notifiers import get_notifier
from global_logger import Log

CHAT_ID = os.getenv('MYID', 0)
API_TOKEN = os.getenv('TELEGRAM_DEBUG_BOT')
telegram = get_notifier('telegram')

LOG = Log.get_logger()


def get_html(url):
    r = requests.get(url, timeout=10000)
    return r.text


def extract_number(str_):
    return float("".join(re.findall(r'\d+(?:[.,]\d+)?', str_)).replace(',', '.'))


def price_per_volume(volume, price):
    return int(round(float(price) / float(volume), 0))


def liters(str_):
    for exclusion in (' 10', ' 40'):
        str_ = str_.replace(exclusion, '')
    output = re.search('[1|0]([.,])?\d?[.,]?[0]?[\s]?[Lл]?', str_, flags=re.IGNORECASE | re.UNICODE)
    if output:
        return extract_number(output.group())


def telegram_notify(message):
    telegram.notify(message=message, token=API_TOKEN, chat_id=CHAT_ID, disable_web_page_preview=True,
                    disable_notification=False)
    # from telegram_notification.telegram_notifier import basic_notifier
    # basic_notifier(logger_name='prom_ua', token_id=API_TOKEN, chat_id=CHAT_ID, message=message)


if __name__ == '__main__':
    LOG.verbose = True
    telegram_notify('test message')
    # a = liters('Виски Laphroaig Select (Лафройг Селект) 40% 0.7L')
    print("")
