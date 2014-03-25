# coding=utf-8
import calendar
import datetime
import unittest
from src.core.message_processing import process_message, ParseException

__author__ = '4ikist'


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def next_weekday(weekday):
    d = datetime.datetime.now()
    days_ahead = (weekday - d.weekday()) + 7
    return d + datetime.timedelta(days_ahead)


def this_weekday(weekday):
    d = datetime.datetime.now()
    days_ahead = (weekday - d.weekday())
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def set_time(date, hours, minutes):
    return datetime.datetime(date.year, date.month, date.day, hours, minutes)


tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
this_wednesday = this_weekday(2)
next_wednesday = next_weekday(2)
today = datetime.datetime.today()

test_messages = [
    # {'message': u"Привет! Напомни мне 20.12.2014 в 9:30 о подарках маме и папе",
    #  'date': datetime.datetime(2014, 12, 20, 9, 30)},
    #
    # {'message': u"Привет! Напомни мне 2014.12.20 в 9:30 о подарках маме и папе",
    #  'date': datetime.datetime(2014, 12, 20, 9, 30)},
    #
    # {'message': u"Привет! Напомни мне 20.12 в 9:30 о подарках маме и папе",
    #  'date': datetime.datetime(today.year, 12, 20, 9, 30)},
    #
    # {'message': u"Привет! Напомни мне 20 декабря в 9:30 о подарках маме и папе",
    #  'date': datetime.datetime(today.year, 12, 20, 9, 30)},
    #
    # {'message': u"Привет! Напомни мне завтра в 9:30 о подарках маме и папе",
    #  'date': set_time(tomorrow, 9, 30)},
    #
    # {'message': u"Привет! Напомни мне в среду в 9:30 о подарках маме и папе",
    #  'date': set_time(this_wednesday, 9, 30)},
    #
    # {'message': u"Привет! Напомни мне в эту среду в 9:30 о подарках маме и папе",
    #  'date': set_time(this_wednesday, 9, 30)},
    #
    # {'message': u"Привет! Напомни мне в следующую среду в 9:30 о подарках маме и папе",
    #  'date': set_time(next_wednesday, 9, 30)},

    # {'message': u"Привет! Напомни мне сегодня в 9:30 о подарках маме и папе",
    #  'date': set_time(today, 9, 30)},

    # {'message': u"Привет! Напомни мне завтра в 9:30 о подарках маме и папе",
    #  'date': set_time(today+datetime.timedelta(days=1), 9, 30)},
    #
    # {'message': u"Привет! Напомни мне послезавтра в 9:30 о подарках маме и папе",
    #  'date': set_time(today+datetime.timedelta(days=2), 9, 30)},

    # {'message': u"Привет! Напомни мне через 5 часов о подарках маме и папе",
    #  'date': today + datetime.timedelta(hours=5)},
    #
    # {'message': u"Привет! Напомни мне через 5 минут о подарках маме и папе",
    #  'date': today + datetime.timedelta(minutes=5)},

    {'message': u"Привет! Напомни мне через 5 дней о подарках маме и папе!",
     'date': today + datetime.timedelta(days=5)},

    # {'message': u"Привет! Напомни мне через 5 недель в 9:30 о подарках маме и папе!!",
    #  'date': set_time(today + datetime.timedelta(days=5 * 7), 9, 30)},
    #
    # {'message': u"Привет! Напомни мне через 5 месяцев в 9:30 о подарках маме и папе !!",
    #  'date': set_time(add_months(today, 5), 9, 30)},

    # {'message': u"Привет! Напомни мне через 5 лет в 9:30 о подарках маме и папе !!!",
    #  'date': datetime.datetime(today.year + 5, today.month, today.day, 9, 30)},
]


class MessageProcessingTest(unittest.TestCase):
    def test_message(self):
        for el in test_messages:
            try:
                date, text, ntype = process_message(el['message'])
            except ParseException as e:
                pass
            print el['message']
            result_date = el['date']
            if date.year == result_date.year and date.month == result_date.month and date.day == result_date.day and \
                            date.hour == result_date.hour and date.minute == result_date.minute:
                print 'OK'
            else:
                print "ERROR [%s] [%s] [%s]" % (str(date), text, ntype)


if __name__ == '__main__':
    unittest.main()