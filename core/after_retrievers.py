# coding:utf-8
__author__ = '4ikist'

import re
from datetime import timedelta

powers = [
    {'pattern': re.compile(u'секу?н?д?ы?у?'), 'power': 1},
    {'pattern': re.compile(u'мину?т?ы?'), 'power': 60},
    {'pattern': re.compile(u'час(а|ов)?'), 'power': 60 * 60},
    {'pattern': re.compile(u'полчаса'), 'power': 60 * 30},
    {'pattern': re.compile(u'д(ня|ень|ней)'), 'power': 60 * 60 * 24},
    {'pattern': re.compile(u'неде?л?ь?и?ю?'), 'power': 60 * 60 * 24 * 7},
    {'pattern': re.compile(u'месяц(а|ев)?'), 'power': 60 * 60 * 24 * 30},
    {'pattern': re.compile(u'лет'), 'power': 60 * 60 * 24 * 365},
    {'pattern': re.compile(u'года?'), 'power': 60 * 60 * 24 * 365},
]


def _get_power(input):
    for power_el in powers:
        if power_el['pattern'].match(input):
            return power_el['power']


def after_timedelta(text):
    found = re.findall(
        u"через\s?(\d+)?\s(секу?н?д?ы?у?|мину?т?ы?|полчаса|часа?о?в?|дн?е?н?я?й?ь?|неде?л?ь?и?ю?|меся?ц?а?е?в?|года?|лет)", text,
        re.IGNORECASE)
    if found:
        groups = found[0]
        power = _get_power(groups[1])
        count = int(groups[0] or 1)
        if power:
            return timedelta(seconds= count* power)

