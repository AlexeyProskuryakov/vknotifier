# coding=utf-8
import calendar
import re
import datetime
from properties import notifications_types

__author__ = '4ikist'
months = [el.lower() for el in
          [u'Января', u'Февраля', u'Марта', u'Апреля', u'Мая', u'Июня', u'Июля', u'Августа', u'Сентября', u'Октября',
           u'Ноября',
           u'Декабря']]
month_left_reg = re.compile('\d{1,2}')
month_right_reg = re.compile('\d{4}')

week_days = [u'понедельник', u'вторник', u'среду', u'четверг', u'пятницу', u'субботу', u'воскресенье']

date_regexp = re.compile(u'\d{2,4}[-./]\d{2}[-./]\d{2,4}')
date_semicolon_regexp = re.compile('[-./]')
time_regexp = re.compile(u'\d{1,2}\:\d{2}')
after_regexp = re.compile(u'через (\d*) (секунду?ы?|часа?о?в?|день|дня|дней|месяца?е?в?|недель?и?|года?|лет|минут?ы?)')
powers = [
    {'name': u'сек', 'power': 1},
    {'name': u'мин', 'power': 60},
    {'name': u'час', 'power': 60 * 60},
    {'name': u'дня', 'power': 60 * 60 * 24},
    {'name': u'ден', 'power': 60 * 60 * 24},
    {'name': u'дне', 'power': 60 * 60 * 24},
    {'name': u'нед', 'power': 60 * 60 * 24 * 7},
    {'name': u'лет', 'power': 60 * 60 * 24 * 365},
    {'name': u'год', 'power': 60 * 60 * 24 * 365},
]
type_regexp = re.compile(u'!{1,3}')


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.datetime(year, month, day)


def next_weekday(weekday, now):
    days_ahead = (weekday - now.weekday()) + 7
    date = now + datetime.timedelta(days_ahead)
    return date.year, date.month, date.day


def this_weekday(weekday, now):
    days_ahead = (weekday - now.weekday())
    if days_ahead <= 0:
        days_ahead += 7
    date = now + datetime.timedelta(days_ahead)
    return date.year, date.month, date.day


def __find_date_with_month(tokens, now):
    for i in range(len(tokens)):
        if tokens[i] in months:
            month_id = None
            for j in range(len(months)):
                if tokens[i] == months[j]:
                    month_id = j + 1
                    break
            if i > 1:
                found_day = month_left_reg.findall(tokens[i - 1])
                if len(found_day) > 0:
                    day = int(found_day[0])
                else:
                    continue
                if i < len(tokens) - 2:
                    found_year = month_right_reg.findall(tokens[i + 1])
                    if len(found_year) > 0:
                        year = int(found_year[0])
                    else:
                        year = now.year
                else:
                    year = now.year
                return year, month_id, day, i
    return None


def __find_date_after(tokens, now):
    for i in range(len(tokens) - 2):
        one = tokens[i]
        two = tokens[i + 1]
        three = tokens[i + 2]
        s = '%s %s %s' % (one, two, three)
        found_after = after_regexp.findall(s)
        if len(found_after) > 0:
            count = int(found_after[0][0])
            power_name = found_after[0][1]
            if u'мес' in power_name:
                return add_months(now, count), i + 2
            else:
                for el in powers:
                    if el['name'] in power_name:
                        power = el['power']
                        date = now + datetime.timedelta(seconds=power * count)
                        return date, i + 2
    return None


def __find_date_next(tokens, now):
    for i, el in enumerate(tokens):
        if el == u'завтра':
            date = now + datetime.timedelta(days=1)
        elif el == u'послезавтра':
            date = now + datetime.timedelta(days=2)
        elif el == u'сегодня':
            date = now
        else:
            continue
        return date.year, date.month, date.day, i


def __find_with_week_day(tokens, now):
    for i in range(len(tokens)):
        if tokens[i] in week_days:
            week_day_index = None
            for j in range(len(week_days)):
                if tokens[i] == week_days[j]:
                    week_day_index = j
                    break
            if i > 1 and tokens[i - 1] == u'следующий':
                res = list(next_weekday(week_day_index, now))
                res.append(i)
                return tuple(res)
            else:
                res = list(this_weekday(week_day_index, now))
                res.append(i)
                return tuple(res)
    return None


def __find_date_format(tokens):
    for i, el in enumerate(tokens):
        if date_regexp.match(el):
            date_tokens = date_semicolon_regexp.split(el)
            if len(date_tokens[0]) == 4:
                year = int(date_tokens[0])
                day = int(date_tokens[2])
            elif len(date_tokens[0]) == 2:
                day = int(date_tokens[0])
                year = int(date_tokens[2])
            else:
                continue
            month = int(date_tokens[1])
            return year, month, day, i
    return None


def __find_time(tokens):
    for i, el in enumerate(tokens):
        if time_regexp.match(el):
            time_tokens = el.split(':')
            hour = int(time_tokens[0])
            minute = int(time_tokens[1])
            return hour, minute, i
    return None


date_founders = [__find_date_with_month, __find_with_week_day, __find_date_next]


def _find_date(message_tokens, now):
    now = datetime.datetime.fromtimestamp(now)
    tokens = message_tokens
    date = __find_date_format(tokens)
    for el in date_founders:
        date = el(tokens, now)
        if date:
            break
    time = __find_time(tokens)
    #fucking spaghetti:
    #if not recognised date than trying find "через ... ..."
    if not date:
        date_result = __find_date_after(tokens, now)
        #if not recognised this trying that time was recognised and message like this "Напомни мне в ..:.. то-то"
        if not date_result:
            #if not time - raising
            if not time:
                raise ParseException()
            else:
                return datetime.datetime(now.year, now.month, now.day, time[0], time[1]), time[2]

        #if recognised this and not time than message like this: "Напомни мне через ... [минут/секунд]"
        elif not time:
            return date_result

        #else similar message with "... в ..:.."
        else:
            date = date_result[0].year, date_result[0].month, date_result[0].day, date_result[1]
    if not time:
        time = (now.hour, now.minute, 0)
    return datetime.datetime(date[0], date[1], date[2], time[0], time[1]), time[2] or date[3]


def _find_type(message):
    f_type = type_regexp.findall(message)
    if len(f_type) > 0:
        i_type = len(f_type[-1])
        if i_type > 3:
            i_type = 3
        return notifications_types[i_type - 1]
    return notifications_types[0]


def process_message(message, message_date):
    message.lower()
    notification_type = _find_type(message)
    message_tokens = message.split()
    date, since = _find_date(message_tokens, message_date)
    text = ' '.join(message_tokens[since + 1:])
    return date, text, notification_type


reject_words = [u'нет', u'отмена', u'нифига', u'нихуя', u'отнюдь', u'не']


def is_reject_message(message):
    message.lower()
    for word in reject_words:
        if word in message:
            return True
    return False



class ParseException(Exception):
    pass

