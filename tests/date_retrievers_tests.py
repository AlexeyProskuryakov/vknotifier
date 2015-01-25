# coding:utf-8
__author__ = '4ikist'

import unittest
import datetime

from core.date_time_retrievers import normal_date, month_day_number_date, without_year_date, at_weekday_date, \
    vocable_month2_date, vocable_month_date, tomorrow_date, time_retriever, month_day_number

from core.after_retrievers import after_timedelta
from core.engine import recognise_notification_date_time


class DateRetrieversTest(unittest.TestCase):
    # today is 15.01.2015
    def test_month_day_number(self):
        assert month_day_number_date(u"5 числа этого месяца") == datetime.datetime(2015, 1, 5).date()
        assert month_day_number_date(u"5 числа текущего месяца") == datetime.datetime(2015, 1, 5).date()
        assert month_day_number_date(u"5 числа следующего месяца") == datetime.datetime(2015, 2, 5).date()
        assert month_day_number_date(u"15 числа ") == datetime.datetime(2015, 1, 15).date()

    def test_normal_date(self):
        assert normal_date(u'12.12.2015') == datetime.datetime(2015, 12, 12).date()
        assert normal_date(u'1.1.2015') == datetime.datetime(2015, 1, 1).date()
        assert normal_date(u'13.1.2015') == datetime.datetime(2015, 1, 13).date()

    def test_without_year(self):
        assert without_year_date(u'12.12') == datetime.datetime(2015, 12, 12).date()

    def test_at_week_day(self):
        def get_near_weekday(week_day_number, next=False):
            now = datetime.datetime.utcnow()
            now_week_day = now.weekday()
            if now_week_day > week_day_number:
                day_shift = 7 - now_week_day + week_day_number
            else:
                day_shift = week_day_number - now_week_day
            if next:
                day_shift += 7
            return (now + datetime.timedelta(days=day_shift)).date()

        assert at_weekday_date(u'в этот понедельник') == get_near_weekday(0)
        assert at_weekday_date(u'в понедельник') == get_near_weekday(0)
        assert at_weekday_date(u'во вторник') == get_near_weekday(1)
        assert at_weekday_date(u'в следующий вторник') == get_near_weekday(1, True)
        assert at_weekday_date(u'в эту пятницу') == get_near_weekday(4)
        assert at_weekday_date(u'в следующую пятницу') == get_near_weekday(4, True)

    def test_vocable_month(self):
        assert vocable_month_date(u'5 февраля') == datetime.datetime(2015, 2, 5).date()
        assert vocable_month_date(u'5 февраля 2014 года') == datetime.datetime(2014, 2, 5).date()
        assert vocable_month_date(u'5 февраля 2014') == datetime.datetime(2014, 2, 5).date()
        assert vocable_month_date(u'21 февраля') == datetime.datetime(2015, 2, 21).date()

    def test_vocable_month2(self):
        assert vocable_month2_date(u'тогда в январе 5 числа 2015 года мы будем отдыхать') == datetime.datetime(2015, 1,
                                                                                                               5).date()
        assert vocable_month2_date(u'где-то в январе, 15 числа') == datetime.datetime(2015, 1, 15).date()
        assert vocable_month2_date(u'а в январе 5 числа 2015, я хотел бы пожениться') == datetime.datetime(2015, 1,
                                                                                                           5).date()

    def test_tomorrow(self):
        assert tomorrow_date(u'а завтра будет хорошо') == (datetime.datetime.now() + datetime.timedelta(days=1)).date()
        assert tomorrow_date(u'послезавтра') == (datetime.datetime.now() + datetime.timedelta(days=2)).date()
        assert tomorrow_date(u'сегодня') == (datetime.datetime.now()).date()

    def test_after(self):
        assert after_timedelta(u"через 5 сек") == datetime.timedelta(seconds=5)
        assert after_timedelta(u"через 5 секунд") == datetime.timedelta(seconds=5)
        assert after_timedelta(u"через 50 секунд: поцеловать Алину") == datetime.timedelta(seconds=50)
        assert after_timedelta(u"через 2 секунды") == datetime.timedelta(seconds=2)
        assert after_timedelta(u"через 1 секунду") == datetime.timedelta(seconds=1)

        assert after_timedelta(u"через 5 мин") == datetime.timedelta(minutes=5)
        assert after_timedelta(u"через 5 минут") == datetime.timedelta(minutes=5)
        assert after_timedelta(u"через 1 минуту") == datetime.timedelta(minutes=1)
        assert after_timedelta(u"через 2 минуты") == datetime.timedelta(minutes=2)

        assert after_timedelta(u"через 1 час") == datetime.timedelta(seconds=1 * 3600)
        assert after_timedelta(u"через 2 часа") == datetime.timedelta(seconds=2 * 3600)
        assert after_timedelta(u"через 5 часов") == datetime.timedelta(seconds=5 * 3600)

        assert after_timedelta(u"через 1 день") == datetime.timedelta(seconds=1 * 3600 * 24)
        assert after_timedelta(u"через 2 дня") == datetime.timedelta(seconds=2 * 3600 * 24)
        assert after_timedelta(u"через 5 дней") == datetime.timedelta(seconds=5 * 3600 * 24)

        assert after_timedelta(u"через 1 месяц") == datetime.timedelta(seconds=1 * 3600 * 24 * 30)
        assert after_timedelta(u"через 2 месяца") == datetime.timedelta(seconds=2 * 3600 * 24 * 30)
        assert after_timedelta(u"через 5 месяцев") == datetime.timedelta(seconds=5 * 3600 * 24 * 30)

        assert after_timedelta(u"через 1 неделю") == datetime.timedelta(seconds=1 * 3600 * 24 * 7)
        assert after_timedelta(u"через 2 недели") == datetime.timedelta(seconds=2 * 3600 * 24 * 7)
        assert after_timedelta(u"через 5 недель") == datetime.timedelta(seconds=5 * 3600 * 24 * 7)

        assert after_timedelta(u"через 1 год") == datetime.timedelta(seconds=1 * 3600 * 24 * 365)
        assert after_timedelta(u"через 2 года") == datetime.timedelta(seconds=2 * 3600 * 24 * 365)
        assert after_timedelta(u"через 5 лет") == datetime.timedelta(seconds=5 * 3600 * 24 * 365)

        assert after_timedelta(u"через час") == datetime.timedelta(seconds=60 * 60)
        assert after_timedelta(u"через полчаса") == datetime.timedelta(seconds=60 * 30)

    def test_time_retrievers(self):
        assert time_retriever(u"в 12:20") == datetime.time(12, 20)
        assert time_retriever(u"в 1:20") == datetime.time(1, 20)
        assert time_retriever(u"в 12:20") == datetime.time(12, 20)
        assert time_retriever(u"в 22:20") == datetime.time(22, 20)
        assert time_retriever(u"в 24:20") == None
        assert time_retriever(u"в 23:60") == None

    def test_month_day(self):
        now = datetime.datetime.utcnow()
        assert month_day_number(u'%s числа' % (now.day + 1)) == (now + datetime.timedelta(days=1)).date()
        assert month_day_number(u'%s числа' % (now.day - 1)) == None

    def test_all(self):
        assert recognise_notification_date_time(u"31.01.2015 в 12:30", 3)['when'] == datetime.datetime(2015, 1, 31, 12, 30) - datetime.timedelta(hours=3)
        assert recognise_notification_date_time(u"31 числа в 15:12", 4)['when'] == datetime.datetime(2015, 1, 31, 15, 12) - datetime.timedelta(hours=4)



if __name__ == '__main__':
    unittest.main()


