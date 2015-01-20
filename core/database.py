import pymongo
from datetime import datetime, timedelta
from properties import mongo_address, mongo_db_name
from core import types

__author__ = '4ikist'


class DataBaseHandler(object):
    def __init__(self, host=None, port=None, address=mongo_address, db_name=mongo_db_name, truncate=False):
        if host and port:
            self.db = pymongo.MongoClient(host=host, port=port)[db_name]
        elif address:
            self.db = pymongo.MongoClient(host=address)[db_name]

        self.notifications = self.db['notifications']
        self.utc = self.db['utc']

        if len(self.utc.index_information())<=1:
            self.utc.ensure_index([('user', pymongo.ASCENDING),('city', pymongo.ASCENDING)])

        if len(self.notifications.index_information()) <= 1:
            self.notifications.ensure_index(
                [('when', pymongo.ASCENDING), ('whom', pymongo.ASCENDING), ('type', pymongo.ASCENDING)])

        if truncate:
            self.notifications.remove({}, multi=True)

    def get_utc(self, user=None, city=None):
        query = {}
        if user:
            query['user'] = user
        elif city:
            query['city'] = city
        return self.utc.find_one(query)

    def set_utc(self, user, city, utc):
        if self.utc.find_one({'user':user}):
            self.utc.update({'user':user}, {'$set':{'utc':utc}})
        else:
            self.utc.save({'user':user,'utc':utc})

        if not self.utc.find_one({'city':city}):
            self.utc.save({'city':city, 'utc':utc})

    def set_done(self, notification_id):
        notification = self.notifications.find_one({'_id': notification_id})
        notification_type = notification['type']
        if notification_type > 1:
            self.notifications.update({'_id': notification_id}, {'$set': {'type': notification_type - 1}})
        else:
            self.notifications.update({'_id': notification_id},
                                   {'$unset': {'type': 1, 'when': 1, 'whom': 1, 'message': 1},
                                    '$set': {'deleted': notification}}
            )

    def _transform_date(self, element, td):
        element['when'] = element['when'] - td
        element['declared_when'] = element['when']
        return element

    def get_to_notify(self):
        now = datetime.now()
        result = []
        for type, td in types.iteritems():
            crsr = self.notifications.find(
                {'when': {'$gte': now + td, '$lte': now + td + timedelta(minutes=1)}, 'type': type})
            result.extend([self._transform_date(el, td) for el in crsr])
        return result

    def will_notify(self, when, whom, type, message):

        element = {'when': when, 'whom': whom, 'type': type, 'message': message}
        result = self.notifications.save(element)
        return result

    def remove(self, element_id):
        if element_id:
            return self.notifications.update({'_id': element_id}, {'$set': {'deleted': True}})
        return None

