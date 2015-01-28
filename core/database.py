import pymongo
from datetime import datetime, timedelta
from core import types

__author__ = '4ikist'

time_step = 5


class DataBaseHandler(object):
    def __init__(self, host=None, port=None, address=None, db_name=None, truncate=False):
        if host and port:
            self.db = pymongo.MongoClient(host=host, port=port)[db_name]
        elif address:
            self.db = pymongo.MongoClient(host=address)[db_name]
        else:
            raise Exception('not database credentials included!')

        self.notifications = self.db['notifications']
        self.error_messages = self.db['error_messages']
        self.timezones = self.db['timezones']
        self.users = self.db['users']

        if len(self.users.index_information()) <= 1:
            self.users.ensure_index([('id', pymongo.ASCENDING)])

        if len(self.timezones.index_information()) <= 1:
            self.timezones.ensure_index([('user', pymongo.ASCENDING), ('city', pymongo.ASCENDING)])

        if len(self.error_messages.index_information()) <= 1:
            self.error_messages.ensure_index([('user', pymongo.ASCENDING), ('time', pymongo.ASCENDING)])

        if len(self.notifications.index_information()) <= 1:
            self.notifications.ensure_index(
                [('when', pymongo.ASCENDING), ('whom', pymongo.ASCENDING), ('type', pymongo.ASCENDING),
                 ('by', pymongo.ASCENDING)])

        if truncate:
            self.notifications.remove(multi=True)
            self.error_messages.remove(multi=True)
            self.users.remove(multi=True)


    def get_utc(self, user=None, city=None):
        if user:
            q = {'user': user}
        elif city:
            q = {'city': city}
        else:
            return
        result = self.timezones.find_one(q)
        return result['utc'] if result else None

    def set_utc(self, utc, user, city=None):
        found_user = self.timezones.find_one({'user': user})
        if found_user:
            self.timezones.update({'_id': found_user['_id']}, {'$set': {'utc': utc}})
        else:
            self.timezones.save({'user': user, 'utc': utc})

        if city:
            found_city = self.timezones.find_one({'city': city})
            if not found_city:
                self.timezones.save({'city': city, 'utc': utc})


    def get_user(self, user_id):
        return self.users.find_one({'id': user_id})

    def set_user(self, user_data):
        def save_user(user):
            if not self.get_user(user['id']):
                self.users.save(user)

        if isinstance(user_data, list):
            for user in user_data:
                save_user(user)
        else:
            save_user(user_data)

    def persist_error(self, user, message, **kwargs):
        to_save = {'user': user, 'message': message, 'time': datetime.utcnow()}
        to_save.update(kwargs)
        self.error_messages.save(to_save)

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
        element['declared_when'] = element['when']
        element['when'] = element['when'] - td
        return element

    def get_to_notify(self, near_date=None):
        """
        forming notifications objects
        :param near_date: some datetime
        :return:
        """
        now = near_date or datetime.utcnow()
        result = []
        for type, td in types.iteritems():
            gte = now + td
            lte = now + td + timedelta(seconds=time_step)
            crsr = self.notifications.find(
                {'when': {'$gte': gte, '$lte': lte}, 'type': type})
            result.extend([self._transform_date(el, td) for el in crsr])
        return result

    def will_notify(self, when, whom, type, message, by):
        element = {'when': when, 'whom': whom, 'type': type, 'message': message, 'by': by}
        result = self.notifications.save(element)
        return result

    def remove(self, element_id):
        if element_id:
            return self.notifications.update({'_id': element_id}, {'$set': {'deleted': True}})
        return None

