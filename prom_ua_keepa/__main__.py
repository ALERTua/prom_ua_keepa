import os
import sys
import time
from collections import namedtuple

from bs4 import BeautifulSoup
from global_logger import Log

import common_tools as tools

LOG = Log.get_logger()

Query = namedtuple('Query', ('name', 'url', 'price_per_volume_trigger'))
Product = namedtuple('Product', ('url', 'name', 'price', 'volume', 'price_per_volume'))

BASE = 'https://kiev.prom.ua'
QUERIES = [
    Query(
        name='Talisker',
        url=f'{BASE}/search?search_term=talisker+10&category=20401',
        price_per_volume_trigger=1500,
    ),
    Query(
        name='Ardbeg',
        url=f'{BASE}/search?search_term=ardbeg&category=20401',
        price_per_volume_trigger=1500,
    ),
    Query(
        name='Laphroaig',
        url=f'{BASE}/search?search_term=laphroaig&category=20401',
        price_per_volume_trigger=1500,
    ),

]


def process_query(query):
    LOG.debug(f"Processing query {query}")
    html = tools.get_html(query.url)
    LOG.debug(f"got html for {query}")
    soup = BeautifulSoup(html, 'html.parser')

    product_gallery = soup.find('div', attrs={'data-qaid': 'product_gallery'})
    if not product_gallery:
        LOG.warning(f"Couldn't find product gallery. This may be an error or an empty result set.")
        return

    product_blocks = product_gallery.find_all('div', attrs={'data-qaid': 'product_block'})
    product_blocks = [i for i in product_blocks if hasattr(i, 'text') and i.text]
    price_per_volume_trigger = query.price_per_volume_trigger

    output = []
    for block in product_blocks:
        product_name = block.find('span', attrs={'data-qaid': 'product_name'})
        product_name = product_name.text

        product_presence_obj = block.find('span', attrs={'data-qaid': 'product_presence'})
        product_presence_text = product_presence_obj.text
        product_presence = product_presence_text == 'В наличии'
        # product_presence = product_presence_text != 'Нет в наличии'
        if not product_presence:
            LOG.printer(f"skipping item '{product_name}' as presence is '{product_presence_text}'")
            continue

        product_link = block.find('a', attrs={'data-qaid': 'product_link'})
        product_link = product_link.attrs.get('href')
        product_link = f'{BASE}{product_link}' if product_link else 'Unknown URL'

        product_price = block.find('span', attrs={'data-qaid': 'product_price'})
        if not product_price:
            continue

        product_price = int(tools.extract_number(product_price.text))

        if price_per_volume_trigger:
            product_volume = tools.liters(product_name)
            if not product_volume:
                continue

            price_per_volume_ = tools.price_per_volume(product_volume, product_price)
            if float(price_per_volume_) <= float(price_per_volume_trigger):
                message = f"""Trigger for [{product_name}]({product_link})
Price: {product_price} ({price_per_volume_} per liter)"""
                LOG.green(message)
                tools.telegram_notify(message, disable_notification=False)
        else:
            product_volume = None
            price_per_volume_ = None

        product = Product(url=product_link, name=product_name, price=product_price, volume=product_volume,
                          price_per_volume=price_per_volume_)
        # noinspection PyTypeChecker
        LOG.printer(product)
        output.append(product)
    if price_per_volume_trigger:
        output.sort(key=lambda f: f.price_per_volume if f.price_per_volume else 0)
    else:
        output.sort(key=lambda f: f.price)
    return output


def main():
    args = sys.argv[1:]

    output = {}
    for query in QUERIES:
        if os.getenv('PROM_UA_DEBUG', False):
            output[query] = process_query(query)
        else:
            try:
                output[query] = process_query(query)
            except Exception as e:
                message = f"""Query FAILED:
    {query}
    {type(e)}
    {str(e)}"""
                LOG.green(message)
                tools.telegram_notify(message, disable_notification=True)

    if args and 'silent' in args:
        return

    msgs = []
    for query, products in output.items():
        if not products:
            continue

        lowest = products[0]  # type: Product
        msg = f"""Lowest of [{query.name}]({query.url})
[{lowest.name}]({lowest.url}) @ {lowest.price} ({lowest._asdict().get('price_per_volume', 'unknown')} ppv)
trigger on {query.price_per_volume_trigger} ppv"""
        msgs.append(msg)
    _msgs = "\n\n".join(msgs)
    LOG.green(_msgs)
    # tools.telegram_notify(_msgs, disable_notification=True)

    if args and 'pause' in args:
        os.system('pause')
    return output


if __name__ == '__main__':
    LOG.verbose = True
    DELAY_SEC = os.getenv('DELAY_SEC', 60 * 60 * 8)
    DELAY_SEC = int(DELAY_SEC)
    while True:
        output_ = main()
        LOG.debug(f"sleeping {DELAY_SEC} seconds")
        time.sleep(DELAY_SEC)
