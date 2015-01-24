# coding:utf-8
__author__ = '4ikist'
import requests
from lxml import html

def get_utc(city_name):
    try:
        result = requests.get('http://www.timeserver.ru/time/search',params={'slctd':0, 'query':city_name})
        doc = html.document_fromstring(result.content)
        span = doc.xpath('//span[@class="main1_utc_offset"]')
        if span:
            value = span[0].text.strip()
            return int(value[3:])
    except Exception as e:
        print e


if __name__ == '__main__':
    print get_utc(u'Бердск')