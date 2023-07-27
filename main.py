from win11toast import notify
from rss_parser import Parser
from requests import get
from requests.exceptions import RequestException
from time import sleep
import json
import datetime
import schema

def loadConfig ():
    try:
        with open('config.json') as configFile:
            config = json.load(configFile)
    except:
        print(config)
        notify(
            'RSS Notificator',
            'Cannot load Configuation',
            duration = 'short'
        )
        sleep(15*60)
        Main()
    
    
    if (len(config['rssURL']) == 0): 
        notify(
            'RSS Notificator',
            'No RSS URL found',
            duration = 'short'
        )
        sleep(15*60)
        Main()

    return config

def getData (config):
    print(config)
    try:
        res = get(config['rssURL'], timeout=10)
    except RequestException:
        notify(
            'RSS Notificator',
            'Request Failed',
            duration = 'short'

        )
        sleep(15*60)
        Main()
    if (res.status_code == 404 or len(res.text) == 0):
        notify(
            'RSS Notificator',
            'Data not found',
            duration = 'short'
        )
        sleep(15*60)
        Main()
    return res.text

     
def ParseData(text: str):
    try:
        data = Parser.parse(text, schema=schema.DataSchema)
    except:
        notify(
            'RSS Notificator',
            'Cannot Parse Data',
            duration = 'short'
        )
        sleep(15*60)
        Main()
    return data

def Main():
    config = loadConfig()
    text = getData(config=config)
    data = ParseData(text=text)
    
    for item in data: 
        dataFile = open('./data.txt', 'wr')
        lastPubdate = dataFile.read().split(':')[1]
        itemDate = int(item.pubDate.split(' '))
        day = int(itemDate[0].split('/')[1])
        month = int(itemDate[0].split('/')[0])
        year = int(itemDate[0].split('/')[2])
        hour = int(itemDate[1].split(':')[0])
        min = int(itemDate[1].split(':')[1])
        sec = int(itemDate[1].split(':')[2])
        itemDatetime = datetime.datetime(year, month, day, hour, min, sec)
        if(itemDatetime > lastPubdate): 
            dataFile.write(f'lastPubdate:{itemDatetime}')
        dataFile.close()

        notify(
            'Thông báo từ trường',
            item.title,
            duration = 'short'
        )

Main()
    