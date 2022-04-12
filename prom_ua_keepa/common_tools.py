import os
import re
import requests
from notifiers import get_notifier
from global_logger import Log

CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 0)
TELEGRAM_BOT_API_KEY = os.getenv('TELEGRAM_BOT_API_KEY')
TELEGRAM_DEFAULT_PARSE_MODE = 'markdown'
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


def telegram_notify(message, token=TELEGRAM_BOT_API_KEY, chat_id=CHAT_ID, parse_mode=TELEGRAM_DEFAULT_PARSE_MODE,
                    disable_web_page_preview=True, disable_notification=False, reply_to_message_id=None, **kwargs):
    """
        "message": {"type": "string", "title": "Text of the message to be sent"},
        "token": {"type": "string", "title": "Bot token"},
        "chat_id": {
            "oneOf": [{"type": "string"}, {"type": "integer"}],
            "title": "Unique identifier for the target chat or username of the target channel "
            "(in the format @channelusername)",
        },
        "parse_mode": {
            "type": "string",
            "title": "Send Markdown or HTML, if you want Telegram apps to show bold, italic,"
            " fixed-width text or inline URLs in your bot's message.",
            "enum": ["markdown", "html"],
        },
        "disable_web_page_preview": {
            "type": "boolean",
            "title": "Disables link previews for links in this message",
        },
        "disable_notification": {
            "type": "boolean",
            "title": "Sends the message silently. Users will receive a notification with no sound.",
        },
        "reply_to_message_id": {
            "type": "integer",
            "title": "If the message is a reply, ID of the original message",
        },
    """
    token = token or TELEGRAM_BOT_API_KEY
    if not TELEGRAM_BOT_API_KEY:
        LOG.error('No Telegram bot API key provided')
        return

    chat_id = chat_id or CHAT_ID
    if not CHAT_ID:
        LOG.error('No Telegram chat ID provided')
        return

    parse_mode = parse_mode or TELEGRAM_DEFAULT_PARSE_MODE
    disable_web_page_preview = disable_web_page_preview or True
    disable_notification = disable_notification or False
    reply_to_message_id = reply_to_message_id or 0
    telegram.notify(message=message, token=token, chat_id=chat_id, disable_web_page_preview=disable_web_page_preview,
                    disable_notification=disable_notification, parse_mode=parse_mode,
                    reply_to_message_id=reply_to_message_id, **kwargs)


if __name__ == '__main__':
    LOG.verbose = True
    telegram_notify('test message')
    # a = liters('Виски Laphroaig Select (Лафройг Селект) 40% 0.7L')
    print("")
