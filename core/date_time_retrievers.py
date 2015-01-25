# coding:utf-8
__author__ = '4ikist'
import re
from datetime import datetime, timedelta, time


months = [re.compile(u'января?е?'),
          re.compile(u'февраля?е?'),
          re.compile(u'марта?е?'),
          re.compile(u'апреля?е?'),
          re.compile(u'мая?е?'),
          re.compile(u'июня?е?'),
          re.compile(u'июля?е?'),
          re.compile(u'августа?е?'),
          re.compile(u'сентября?е?'),
          re.compile(u'октября?е?'),
          re.compile(u'ноября?е?'),
          re.compile(u'декабря?е?')]


def _get_month_number(month_name):
    for i, el in enumerate(months):
        if el.match(month_name):
            return i + 1


week_days = [u'понедельник', u'вторник', u'среду', u'четверг', u'пятницу', u'субботу', u'воскресенье']


def normal_date(text):
    found_date = re.findall("\d{1,2}\.\d{1,2}\.\d{4}", text, re.IGNORECASE)
    if found_date:
        return datetime.strptime(found_date[0], '%d.%m.%Y').date()


def without_year_date(text):
    found_date = re.findall("\d{1,2}\.\d{1,2}", text, re.IGNORECASE)
    if found_date:
        return datetime.strptime('%s.%s' % (found_date[0], datetime.utcnow().year), '%d.%m.%Y').date()


def month_day_number_date(text):
    matched = re.findall(u"(\d{1,2})\sчисла\s*(этого|текущего|следую?щего)?(\s+месяца)?", text, re.IGNORECASE)
    if matched:
        now = datetime.utcnow()
        groups = matched[0]
        if u'след' in groups[1]:
            month = now.month + 1
        else:
            month = now.month
        day = int(groups[0])
        year = now.year
        return datetime(year, month, day).date()


def at_weekday_date(text):
    matched = re.findall(
        u'во?\s(это?т?у?|следующ(ий|ее|ую))?\s?(понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье)',
        text, re.IGNORECASE)
    if matched:
        now = datetime.utcnow()
        now_wd = now.weekday()
        groups = matched[0]
        next = False
        if groups[0] is not None and u'след' in groups[0]:
            next = True
        wd = week_days.index(groups[2])
        if now_wd > wd:
            days_plus = (7 - now_wd) + wd
        else:
            days_plus = wd - now_wd
        days_plus += 7 if next else 0
        return (now + timedelta(days_plus)).date()


def vocable_month_date(text):
    matched = re.findall(
        u"(\d{1,2})\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s?((\d{4})\s?(года)?)?",
        text,
        re.IGNORECASE)
    if matched:
        now = datetime.utcnow()
        groups = matched[0]
        year = int(groups[3]) if groups[3] else now.year
        month = _get_month_number(groups[1])
        day = int(groups[0])
        return datetime(year, month, day).date()


def vocable_month2_date(text):
    matched = re.findall(
        u"в\s(январе|феврале|марте|апреле|мае|июне|июле|августе|сентябре|октябре|ноябре|декабре)[\s,]+((\d{1,2})\sчисла)\s?((\d{4})\s?(года)?)?",
        text,
        re.IGNORECASE)
    if matched:
        now = datetime.utcnow()
        groups = matched[0]
        month = _get_month_number(groups[0])
        day = int(groups[2])
        year = int(groups[4]) if groups[4] else now.year
        return datetime(year, month, day).date()


def month_day_number(text):
    matched = re.findall(u"(\d{1,2})\s(числа)", text, re.IGNORECASE)
    if matched:
        now = datetime.utcnow()
        groups = matched[0]
        month_day_found = int(groups[0])
        month_day = now.day
        if month_day_found > month_day:
            return datetime(now.year, now.month, month_day_found).date()


def tomorrow_date(text):
    matched = re.findall(u"(((после)?завтра)|сегодня)", text, re.IGNORECASE)
    if matched:
        now = datetime.utcnow()
        groups = matched[0]
        if u"сегодня" in groups[0]:
            return now.date()
        else:
            if groups[2]:
                return (now + timedelta(days=2)).date()
            else:
                return (now + timedelta(days=1)).date()


date_retrievers = {
    1: vocable_month_date,
    2: vocable_month2_date,
    3: at_weekday_date,
    4: month_day_number_date,
    5: tomorrow_date,
    6: normal_date,
    7: without_year_date,
    8: month_day_number
}


def time_retriever(text):
    found = re.findall(u"в\s((?:0?[0-9])|(?:1[0-9])|(?:2[0-3])):([0-5][0-9])", text, re.IGNORECASE)
    if found:
        groups = found[0]
        hours = groups[0]
        minutes = groups[1]
        if hours and minutes:
            return time(int(hours), int(minutes))


def retrieve_datetime(text):
    """
    Retrieving from text
    :param text:
    :return:
    """
    for i, date_retriever in date_retrievers.iteritems():
        date = date_retriever(text)
        if date:
            time = time_retriever(text)
            return datetime.combine(date, time)
    today_time = time_retriever(text)
    if today_time:
        return datetime.combine(datetime.utcutcnow().date(), today_time)
    return None
