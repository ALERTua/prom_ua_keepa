import os
import sys

from global_logger import Log
from collections import namedtuple
from bs4 import BeautifulSoup
import common_tools as tools
LOG = Log.get_logger()

Query = namedtuple('Query', ('name', 'url', 'price_per_volume_trigger'))
Product = namedtuple('Product', ('url', 'name', 'price', 'volume', 'price_per_volume'))

BASE = 'https://kiev.prom.ua'
QUERIES = [
    Query(
        name='Talisker',
        url=f'{BASE}/search?search_term=talisker+10&category=20401',
        price_per_volume_trigger=1300,
    ),
    Query(
        name='Ardbeg',
        url=f'{BASE}/search?search_term=ardbeg&category=20401',
        price_per_volume_trigger=1400,
    ),
    Query(
        name='Laphroaig',
        url=f'{BASE}/search?search_term=laphroaig&category=20401',
        price_per_volume_trigger=1300,
    ),

]


def process_query(query):
    soup = BeautifulSoup(tools.get_html(query.url), 'html.parser')

    product_gallery = soup.find('div', attrs={'data-qaid': 'product_gallery'})
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
            price_per_volume_ = tools.price_per_volume(product_volume, product_price)
            if float(price_per_volume_) <= float(price_per_volume_trigger):
                message = f"""Name: {product_name}
Price: {product_price}
URL: {product_link}
Price per liter: {price_per_volume_}"""
                LOG.green(message)
                tools.telegram_notify(message)
        else:
            product_volume = None
            price_per_volume_ = None

        product = Product(url=product_link, name=product_name, price=product_price, volume=product_volume,
                          price_per_volume=price_per_volume_)
        # noinspection PyTypeChecker
        LOG.printer(product)
        output.append(product)
    if price_per_volume_trigger:
        output.sort(key=lambda f: f.price_per_volume)
    else:
        output.sort(key=lambda f: f.price)
    return output


def main():
    args = sys.argv[1:]

    output = {}
    for query in QUERIES:
        try:
            output[query] = process_query(query)
        except Exception as e:
            message = f"""Query FAILED:
{query}
{type(e)}
{str(e)}"""
            LOG.green(message)
            tools.telegram_notify(message)

    if args and 'silent' in args:
        return

    msgs = []
    for query, products in output.items():
        lowest = products[0]  # type: Product
        msg = f"""Lowest of '{query.name}'
{query.url}
{lowest.name} @ {lowest.price}
{lowest._asdict().get('price_per_volume', 'unknown')} ppv
{lowest.url}
trigger on {query.price_per_volume_trigger} ppv"""
        msgs.append(msg)
    _msgs = "\n\n".join(msgs)
    LOG.green(_msgs)
    tools.telegram_notify(_msgs)

    if args and 'pause' in args:
        os.system('pause')
    return output


if __name__ == '__main__':
    LOG.verbose = True
    output_ = main()
    print("")
