# coding:utf-8
from Queue import Queue
from collections import defaultdict
import unittest
from unittest.case import skip

from api import VK_API
from core.database import DataBaseHandler
from core.engine import imply_whom_user_id, TalkHandler, NotificatonIniter, Notificator
import properties

__author__ = '4ikist'

users = [{
             'id': 181495567,
             'first_name': 'Mikhail',
             'last_name': 'Eliseykin',
             'nickname': '',
             'domain': 'id181495567',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {
             'id': 11444843,
             'first_name': 'Milana',
             'last_name': 'Yuzhakova',
             'nickname': '',
             'domain': 'yumillana',
             'city': {
                 'id': 110,
                 'title': 'Пермь'
             },
             'online': 0
         }, {
             'id': 13091556,
             'first_name': 'Mira',
             'last_name': 'Hong',
             'deactivated': 'banned',
             'domain': 'id13091556',
             'online': 0
         }, {
             'id': 1028972,
             'first_name': 'Nadya',
             'last_name': 'Grigorenko',
             'nickname': '',
             'domain': 'nadyagrigorenko',
             'city': {
                 'id': 24,
                 'title': 'Балашиха'
             },
             'online': 0
         }, {
             'id': 1205180,
             'first_name': 'Nata',
             'last_name': 'Lusik',
             'nickname': '',
             'domain': 'id1205180',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {
             'id': 202860505,
             'first_name': 'Natalia',
             'last_name': 'Suarez',
             'nickname': '',
             'domain': 'ok',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {
             'id': 42488,
             'first_name': 'Natalka',
             'last_name': 'Proglyadova',
             'nickname': '',
             'domain': 'bellosnezka',
             'city': {
                 'id': 2,
                 'title': 'Санктъ-Петербургъ'
             },
             'online': 0
         }, {
             'id': 37031,
             'first_name': 'Nina',
             'last_name': 'Obraztsova',
             'nickname': '',
             'domain': 'id37031',
             'city': {
                 'id': 2,
                 'title': 'Санктъ-Петербургъ'
             },
             'online': 0
         }, {
             'id': 172789581,
             'first_name': 'Olga',
             'last_name': 'Beloglazova',
             'nickname': '',
             'domain': 'id172789581',
             'online': 0
         }, {
             'id': 138104,
             'first_name': 'Olga',
             'last_name': 'Kukoba',
             'nickname': '',
             'domain': 'id138104',
             'city': {
                 'id': 2,
                 'title': 'Санктъ-Петербургъ'
             },
             'online': 0
         }, {
             'id': 545796,
             'first_name': 'Olga',
             'last_name': 'Turbina',
             'nickname': '',
             'domain': 'olgakeen',
             'online': 0
         }, {
             'id': 1878034,
             'first_name': 'Olga',
             'last_name': 'Vronskaya',
             'nickname': '',
             'domain': 'olga_vronskaya',
             'city': {
                 'id': 2,
                 'title': 'Санктъ-Петербургъ'
             },
             'online': 1
         }, {
             'id': 19500260,
             'first_name': 'Omario',
             'last_name': 'Noor',
             'nickname': '#SwagGerBoy#',
             'domain': 'id19500260',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {
             'id': 150581129,
             'first_name': 'Oxana',
             'last_name': 'Montana',
             'nickname': '',
             'domain': 'id150581129',
             'online': 0
         }, {
             'id': 118672638,
             'first_name': 'Patricia',
             'last_name': 'Brunini',
             'nickname': '',
             'domain': 'patribruni',
             'online': 0
         }, {
             'id': 3744520,
             'first_name': 'Robert',
             'last_name': 'Trollebo',
             'nickname': '',
             'domain': 'robert.trollebo',
             'city': {
                 'id': 3302,
                 'title': 'Trondheim'
             },
             'online': 0
         }, {
             'id': 4066802,
             'first_name': 'Roman',
             'last_name': 'Pivovar',
             'deactivated': 'deleted',
             'domain': 'id4066802',
             'online': 0
         }, {
             'id': 2242722,
             'first_name': 'Ruslan',
             'last_name': 'Murashko',
             'nickname': '',
             'domain': 'playflock',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {
             'id': 57606,
             'first_name': 'Sasha',
             'last_name': 'Bizayeva',
             'nickname': '',
             'domain': 'id57606',
             'city': {
                 'id': 1802375,
                 'title': 'Miami'
             },
             'online': 0
         }, {
             'id': 53393103,
             'first_name': 'Shoakbar',
             'last_name': 'Shomahsudov',
             'nickname': '',
             'domain': 'shoakbar',
             'city': {
                 'id': 194,
                 'title': 'Ташкентъ'
             },
             'online': 0
         }, {
             'id': 55289535,
             'first_name': 'Sonny',
             'last_name': 'Wahjudiомъ',
             'nickname': '',
             'domain': 'id55289535',
             'city': {
                 'id': 1904426,
                 'title': 'Surabaya'
             },
             'online': 0
         }, {
             'id': 56339469,
             'first_name': 'Steen',
             'last_name': 'Jensen',
             'nickname': '',
             'domain': 'frydenlund',
             'city': {
                 'id': 17640,
                 'title': 'Esbjerg'
             },
             'online': 0
         }, {
             'id': 47913112,
             'first_name': 'Stepan',
             'last_name': 'Stetsiv',
             'nickname': '',
             'domain': 'stetsiv',
             'city': {
                 'id': 295,
                 'title': 'London'
             },
             'online': 1
         }, {
             'id': 198261,
             'first_name': 'Sveta',
             'last_name': 'Snegireva',
             'nickname': '',
             'domain': 'svit',
             'city': {
                 'id': 2,
                 'title': 'Санктъ-Петербургъ'
             },
             'online': 0
         }, {
             'id': 1352328,
             'first_name': 'Svetlana',
             'last_name': 'Samokhvalova',
             'nickname': '',
             'domain': 's.naumchik',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {
             'id': 328668,
             'first_name': 'Sweet',
             'last_name': 'Pie',
             'nickname': 'Apple',
             'domain': 'id328668',
             'city': {
                 'id': 151,
                 'title': 'Уфа'
             },
             'online': 0
         }, {
             'id': 352773,
             'first_name': 'S&#237;lvia',
             'last_name': 'Vilar&#243;',
             'nickname': '',
             'domain': 'id352773',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {
             'id': 10334844,
             'first_name': 'Timo',
             'last_name': 'Cinema',
             'nickname': '',
             'domain': 'timocinema',
             'city': {
                 'id': 2,
                 'title': 'Санктъ-Петербургъ'
             },
             'online': 0
         }, {
             'id': 51521563,
             'first_name': 'Tina',
             'last_name': 'Brandon',
             'nickname': '',
             'domain': 'id51521563',
             'online': 0
         }, {
             'id': 205387401,
             'first_name': 'Tom',
             'last_name': 'Cruise',
             'nickname': '',
             'domain': 'tomcruise',
             'city': {
                 'id': 5331,
                 'title': 'Los Angeles'
             },
             'online': 0
         }, {
             'id': 36525286,
             'first_name': 'Tony',
             'last_name': 'Alfian',
             'nickname': '',
             'domain': 'id36525286',
             'city': {
                 'id': 5266854,
                 'title': 'Reutlingen'
             },
             'online': 0
         }, {
             'id': 9566155,
             'first_name': 'Valery',
             'last_name': 'Kuleshova',
             'nickname': '',
             'domain': 'l_a_b_e_ll_a_v_i_t_a',
             'city': {
                 'id': 292,
                 'title': 'Одесса'
             },
             'online': 0
         }, {
             'id': 15154234,
             'first_name': 'Vasiliy',
             'last_name': 'Tolstov',
             'deactivated': 'deleted',
             'domain': 'id15154234',
             'online': 0
         }, {
             'id': 8355786,
             'first_name': 'Vassilissa',
             'last_name': 'Belokopytova',
             'nickname': '',
             'domain': 'batsilisa',
             'city': {
                 'id': 2,
                 'title': 'Санктъ-Петербургъ'
             },
             'online': 0
         }, {
             'id': 771303,
             'first_name': 'Vera',
             'last_name': 'Petukhova',
             'nickname': '',
             'domain': 'vera.petukhova',
             'online': 0
         }, {
             'id': 228237457,
             'first_name': 'Veronika',
             'last_name': 'Veronika',
             'nickname': '',
             'domain': 'veronisha91',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {
             'id': 11402947,
             'first_name': 'Vesna',
             'last_name': 'Vukicevic',
             'nickname': '',
             'domain': 'id11402947',
             'city': {
                 'id': 22016,
                 'title': 'Nik&#353;i&#263;'
             },
             'online': 0
         }, {
             'id': 83902160,
             'first_name': 'Via',
             'last_name': 'X-Press',
             'deactivated': 'banned',
             'domain': 'id83902160',
             'online': 0
         }, {
             'id': 144659,
             'first_name': 'Victory',
             'last_name': 'Shakhova-Kogan',
             'nickname': '',
             'domain': 'id144659',
             'online': 0
         }, {
             'id': 1520313,
             'first_name': 'Vikoss',
             'last_name': 'Куксовой',
             'nickname': '',
             'domain': 'id1520313',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             },
             'online': 0
         }, {'id': 10130611,
             'first_name': 'Откуда',
             'last_name': 'Куда',
             'sex': 2,
             'nickname': '<>',
             'domain': 'from_to_where',
             'city': {
                 'id': 1,
                 'title': 'Москва'
             }},
         {'id': 1,
          'first_name': 'Test',
          'last_name': 'Test',
          'sex': 2,
          'nickname': '<>',
          'domain': 'test_test',
          'city': {
              'id': 1,
              'title': 'Москва'
          }},
         {'id': 2,
          'first_name': 'Test_woman',
          'last_name': 'Test',
          'sex': 1,
          'nickname': '<>',
          'domain': 'test_test_woman',
          'city': {
              'id': 1,
              'title': 'Москва'
          }}]

from datetime import datetime, timedelta, time


def gen_date_time_str(date, type=1):
    tds = [{'seconds': 0}, {'hours': 1}, {'days': 1}]
    whens = []
    for i in range(type):
        whens.append((date - timedelta(**tds[i])).strftime("%d.%m.%Y %H:%M"))
    return u'\n'.join(whens)


class API_Fake(VK_API):
    def __init__(self, ):
        VK_API.__init__(self, None, None, test_mode=True)
        self.users = dict([(user['id'], user) for user in users])
        self.messages = defaultdict(list)
        self.test_messages = []

    def get(self, method_name, **kwargs):
        if method_name == 'friends.get':
            return {'count': 123, 'items': users}
        elif method_name == 'users.get':
            return [self.users.get(kwargs['user_ids'])]

    def send_message(self, user_id, text):
        self.messages[user_id].append(text)

    def add_test_message(self, message):
        self.test_messages.append(message)

    def get_messages(self):
        for message in self.test_messages:
            if 'text' in message:
                message['text'] = message['text'].lower()
            yield message


class TestEngine(unittest.TestCase):
    def setUp(self):
        from start import load_config

        _, db_credentials = load_config('../properties.sample.cfg')
        db_credentials['truncate'] = True
        self.db = DataBaseHandler(**db_credentials)
        self.api = API_Fake()

    def test_imply_whom_user_id(self):
        api = API_Fake()
        by_user_info = api.get('users.get', **{'user_ids': 10130611})[0]

        assert imply_whom_user_id(
            u'для меня, natalka proglyadova, id37031, robert.trollebo, shoakbar напомни через 5 минут: выпей яду сука',
            by_user_info,
            api) \
               == {
            10130611: api.get('users.get', **{'user_ids': 10130611})[0],
            42488: api.get('users.get', **{'user_ids': 42488})[0],
            37031: api.get('users.get', **{'user_ids': 37031})[0],
            3744520: api.get('users.get', **{'user_ids': 3744520})[0],
            53393103: api.get('users.get', **{'user_ids': 53393103})[0],
        }

    def check_notification_create(self, scenario):
        for user_messages in scenario['user_messages']:
            for message in user_messages['messages']:
                self.api.add_test_message({'from': user_messages['from'], 'text': message})
        th = TalkHandler(api=self.api, db=self.db)
        th.loop()
        for system_messages in scenario['system_messages']:
            for i, message in enumerate(system_messages['messages']):
                api_message = self.api.messages[system_messages['for']][i]
                self.assertEqual(api_message, message, '\n%s\n%s\n not equal' % (api_message, message))

    def check_notification_send(self, scenario):
        for notification in scenario['notifications']:
            result = self.db.get_to_notify(
                notification['time'] - timedelta(hours=self.db.get_utc(notification['by'])) - timedelta(seconds=2))

            self.assertEqual(len(result),1, 'result has no one len')

            notificator = Notificator(self.api, self.db, result,
                                      when_notify=notification['time'] + timedelta(seconds=1))
            notificator.start()
            notificator.join()

            api_message = self.api.messages[notification['for']][-1]
            message = notification['message']
            self.assertEqual(api_message, message, '\n%s\n%s\n not equal' % (api_message, message))

    def test_engine(self):
        date_time = datetime.combine((datetime.now() + timedelta(days=1)).date(), time(12, 30))
        scenario = {
            'user_messages': [
                {'from': 1, 'messages': [u'Для меня, id2 напомни завтра в 12:30, что: тест', u'Да']},

            ],

            'system_messages': [
                {'for': 1,
                 'messages': [

                     properties.will_notify % (
                         u'тебе, Test_woman Test [test_test_woman]',
                         u'тест',
                         u'ую',
                         u'у',
                         gen_date_time_str(date_time),
                         u'ен'),

                     u':)'
                 ]
                },
            ],

            'notifications': [{'time': date_time,
                               'message': properties.notify_string % (u'тест', u'сам'),
                               'for': 1,
                               'by': 1},

                              {'time': date_time,
                               'message': properties.notify_string % (u'тест', u'Test Test'),
                               'for': 2,
                               'by': 1}]

        }

        self.check_notification_create(scenario)
        self.check_notification_send(scenario)


    def test_engine_for_some_users(self):
        date_time = datetime.combine((datetime.now() + timedelta(days=1)).date(), time(20, 30))
        scenario = {
            'user_messages': [
                {'from': 2, 'messages': [u'Для меня напомни завтра в 20:30, что: тест!!!', u'Да']},

            ],

            'system_messages': [
                {'for': 2,
                 'messages': [

                     properties.will_notify % (
                         u'тебе',
                         u'тест!!!',
                         u'ие',
                         u'ы',
                         gen_date_time_str(date_time, 3),
                         u'на'),

                     u':)'
                 ]
                },
            ],

            'notifications': [{'time': date_time - timedelta(days=1),
                               'message': properties.notify_string % (u'тест!!!', u'сам'),
                               'for': 2,
                               'by': 2},

                              {'time': date_time - timedelta(hours=1),
                               'message': properties.notify_string % (u'тест!!!', u'сам'),
                               'for': 2,
                               'by': 2},
                              {'time': date_time,
                               'message': properties.notify_string % (u'тест!!!', u'сам'),
                               'for': 2,
                               'by': 2}]

        }

        self.check_notification_create(scenario)
        self.check_notification_send(scenario)