# coding:utf-8
__author__ = '4ikist'
import unittest
from core.database import DataBaseHandler

from datetime import datetime, timedelta


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        from start import load_config

        _, db_credentials = load_config('../properties.sample.cfg')
        db_credentials['truncate'] = True
        self.db = DataBaseHandler(**db_credentials)

    def test_simple(self):
        now = datetime.now()
        self.db.will_notify(now + timedelta(seconds=1), '@test', 1, 'foo bar baz')
        self.db.will_notify(now + timedelta(seconds=2), '@test', 1, 'foo')
        self.db.will_notify(now + timedelta(seconds=100), '@test', 1, 'bar')

        result = self.db.get_to_notify()
        assert len(result) == 2

        assert result[0]['when'] == now + timedelta(seconds=1)
        assert result[1]['when'] == now + timedelta(seconds=2)

        self.db.set_done(result[0]['_id'])
        self.db.set_done(result[1]['_id'])

        in_db = list(self.db.notifications.find())
        for el in in_db:
            if el.get('message') != 'bar':
                assert el.get('deleted')
                assert el.get('deleted').get('when')
                assert el.get('deleted').get('whom')
                assert el.get('deleted').get('type')
                assert el.get('deleted').get('message')

    def test_with_different_types(self):
        now = datetime.now()
        self.db.will_notify(now + timedelta(seconds=2), '@test', 1, 'first type')
        self.db.will_notify(now + timedelta(seconds=2, hours=1), '@test', 2, 'second type')
        self.db.will_notify(now + timedelta(seconds=2, days=1), '@test', 3, 'third type')
        result = self.db.get_to_notify()

        assert len(result) == 3

        assert result[0]['when'] == now + timedelta(seconds=2)
        assert result[1]['when'] == now + timedelta(seconds=2)
        assert result[2]['when'] == now + timedelta(seconds=2)

        self.db.set_done(result[0]['_id'])
        self.db.set_done(result[1]['_id'])
        self.db.set_done(result[2]['_id'])

        assert self.db.notifications.find_one({'message': 'second type'}).get('type') == 1
        assert self.db.notifications.find_one({'message': 'third type'}).get('type') == 2
        assert self.db.notifications.find_one({'message': 'first type'}) is None











