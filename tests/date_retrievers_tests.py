# coding:utf-8
__author__ = '4ikist'

import unittest
import datetime

from core.date_time_retrievers import normal_date, month_day_number_date, without_year_date, at_weekday_date, \
    vocable_month2_date, vocable_month_date, tomorrow_date, time_retriever

from core.after_retrievers import after_timedelta


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

    # def test_at_week_day(self):
    #     assert at_weekday_date(u'в этот понедельник') == datetime.datetime(2015, 1, 19).date()
    #     assert at_weekday_date(u'в понедельник') == datetime.datetime(2015, 1, 19).date()
    #     assert at_weekday_date(u'во вторник') == datetime.datetime(2015, 1, 20).date()
    #     assert at_weekday_date(u'в следующий вторник') == datetime.datetime(2015, 1, 27).date()
    #     assert at_weekday_date(u'в эту пятницу') == datetime.datetime(2015, 1, 16).date()
    #     assert at_weekday_date(u'в следующую пятницу') == datetime.datetime(2015, 1, 23).date()

    def test_vocable_month(self):
        assert vocable_month_date(u'5 февраля') == datetime.datetime(2015, 2, 5).date()
        assert vocable_month_date(u'5 февраля 2014 года') == datetime.datetime(2014, 2, 5).date()
        assert vocable_month_date(u'5 февраля 2014') == datetime.datetime(2014, 2, 5).date()
        assert vocable_month_date(u'21 февраля') == datetime.datetime(2015, 2, 21).date()

    def test_vocable_month2(self):
        assert vocable_month2_date(u'тогда в январе 5 числа 2015 года мы будем отдыхать') == datetime.datetime(2015, 1,5).date()
        assert vocable_month2_date(u'где-то в январе, 15 числа') == datetime.datetime(2015, 1,15).date()
        assert vocable_month2_date(u'а в январе 5 числа 2015, я хотел бы пожениться') == datetime.datetime(2015, 1,5).date()

    def test_tomorrow(self):
        assert tomorrow_date(u'а завтра будет хорошо') == (datetime.datetime.now()+datetime.timedelta(days=1)).date()
        assert tomorrow_date(u'послезавтра') == (datetime.datetime.now()+datetime.timedelta(days=2)).date()
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

        assert after_timedelta(u"через 1 час") == datetime.timedelta(seconds=1*3600)
        assert after_timedelta(u"через 2 часа") == datetime.timedelta(seconds=2*3600)
        assert after_timedelta(u"через 5 часов") == datetime.timedelta(seconds=5*3600)

        assert after_timedelta(u"через 1 день") == datetime.timedelta(seconds=1*3600*24)
        assert after_timedelta(u"через 2 дня") == datetime.timedelta(seconds=2*3600*24)
        assert after_timedelta(u"через 5 дней") == datetime.timedelta(seconds=5*3600*24)

        assert after_timedelta(u"через 1 месяц") == datetime.timedelta(seconds=1*3600*24*30)
        assert after_timedelta(u"через 2 месяца") == datetime.timedelta(seconds=2*3600*24*30)
        assert after_timedelta(u"через 5 месяцев") == datetime.timedelta(seconds=5*3600*24*30)

        assert after_timedelta(u"через 1 неделю") == datetime.timedelta(seconds=1*3600*24*7)
        assert after_timedelta(u"через 2 недели") == datetime.timedelta(seconds=2*3600*24*7)
        assert after_timedelta(u"через 5 недель") == datetime.timedelta(seconds=5*3600*24*7)

        assert after_timedelta(u"через 1 год") == datetime.timedelta(seconds=1*3600*24*365)
        assert after_timedelta(u"через 2 года") == datetime.timedelta(seconds=2*3600*24*365)
        assert after_timedelta(u"через 5 лет") == datetime.timedelta(seconds=5*3600*24*365)

    def test_time_retrievers(self):
        assert time_retriever(u"в 12:20") == datetime.time(12,20)
        assert time_retriever(u"в 1:20") == datetime.time(1,20)
        assert time_retriever(u"в 12:20") == datetime.time(12,20)
        assert time_retriever(u"в 22:20") == datetime.time(22,20)
        assert time_retriever(u"в 24:20") == None
        assert time_retriever(u"в 23:60") == None





