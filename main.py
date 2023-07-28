import datetime
import json
from time import sleep

from requests import get
from requests.exceptions import RequestException
from rss_parser import Parser
from win11toast import notify


def load_config():
    try:
        with open('config.json', 'r') as configFile:
            config = json.load(configFile)
    except:
        notify(
            'RSS Notifier',
            'Cannot load Configuration',
            duration='short'
        )
        return None

    if not config['rssURL']:
        notify(
            'RSS Notifier',
            'No RSS URL found',
            duration='short'
        )
        return None
    return config


def get_data(config):
    try:
        res = get(config['rssURL'], timeout=30, headers={
            "Accept": "Accept: text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, /;q=0.8",
            "User-Agent": "Mozilla/5.0"
        })
        if res.status_code == 404 or len(res.text) == 0:
            notify(
                'RSS Notifier',
                'Data not found',
                duration='short'
            )
            return None
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
        data = Parser.parse(text)
        return data
    except:
        notify(
            'RSS Notifier',
            'Cannot Parse Data',
            duration='short'
        )
        return None


def main():
    config = load_config()
    if not config:
        return
    text = get_data(config=config)
    if not text:
        return
    data = parse_data(text=text)
    if not data:
        return

    for item in data.channel.items[::-1]:
        with open('data.txt', 'r') as data_file:
            raw_pubdate = data_file.read().split('>')
        last_pubdate = datetime.datetime.strptime(raw_pubdate[1], '%Y-%m-%d %H:%M:%S')
        item_date = datetime.datetime.strptime(item.pub_date.content, '%m/%d/%Y %H:%M:%S %p')
        if item_date > last_pubdate:
            with open('data.txt', 'w') as data_file:
                data_file.write(f'lastPubdate>{item_date}')
            notify(
                data.channel.title.content,
                item.title.content,
                duration='short',
                on_click=item.link.content
            )
            sleep(20)
        else:
            continue

while True:
    main()

    sleep(60 * 15)
