import asyncio
import datetime
import json
from time import sleep

from requests import get
from requests.exceptions import RequestException
from rss_parser import Parser
from win11toast import notify

import schema


async def load_config():
    try:
        with open('config.json', 'r') as configFile:
            config = json.load(configFile)

            if not config['rssURL']:
                notify(
                    'RSS Notifier',
                    'No RSS URL found',
                    duration='short'
                )

        return config
    except:
        notify(
            'RSS Notifier',
            'Cannot load Configuration',
            duration='short'
        )
        return None


def get_data(config):
    try:
        res = get(config['rssURL'], timeout=30, headers={
            "Accept": "Accept: text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, /;q=0.8",
            "User-Agent": "Chrome/51.0.2704.103"
        })
        if res.status_code == 404 or len(res.text) == 0:
            notify(
                'RSS Notifier',
                'Data not found',
                duration='short'
            )
            return None
        print(res)
        return res.text
    except RequestException:
        notify(
            'RSS Notifier',
            'Request Failed',
            duration='short'

        )
        return None


def parse_data(text: str):
    try:
        data = Parser.parse(text, schema=schema.DataSchema)
        return data
    except:
        notify(
            'RSS Notifier',
            'Cannot Parse Data',
            duration='short'
        )
        return None


async def main():
    config = await load_config()
    if not config: return
    text = get_data(config=config)
    if not text: return
    data = parse_data(text=text)
    if not data: return
    data_file = open('./data.txt', 'r+')
    for item in data:
        raw_pubdate = data_file.read().split('>')
        last_pubdate = datetime.datetime.strptime(raw_pubdate[1], '%Y-%m-%d %H:%M:%S')
        item_date = datetime.datetime.strptime(item.pubDate, '%m/%d/%Y %H:%M:%S %p')
        if item_date > last_pubdate:
            data_file.write(f'lastPubdate>{item_date}')
            notify(
                'Thông báo từ trường',
                item.title,
                duration='short'
            )
        else:
            notify(
                'Thông báo từ trường',
                'Không có thông báo mới',
                duration='short'
            )
    data_file.close()


while True:
    asyncio.run(main())

    sleep(60 * 15)
