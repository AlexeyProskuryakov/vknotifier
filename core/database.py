import pymongo
from properties import mongo_address

__author__ = '4ikist'


class DataBaseHandler(object):
    def __init__(self, host=None, port=None, address=mongo_address):
        if host and port:
            self.db = pymongo.MongoClient(host, port)['notifier']
        elif address:
            self.db = pymongo.MongoClient(host=address)['notifier']

        self.collection = self.db['notifications']
        self.error_collection = self.db['errors']
        if len(self.collection.index_information()) <= 1:
            self.collection.ensure_index([('when', pymongo.ASCENDING), ('whom', pymongo.ASCENDING)])

        if len(self.error_collection.index_information()) <= 1:
            self.error_collection.ensure_index([('when', pymongo.ASCENDING), ('whom', pymongo.ASCENDING)])

    def set_done(self, notification_id):
        self.collection.update({'_id': notification_id}, {'$set': {'done': True}})

    def get_elements(self, from_time, to_time, element_type):
        crsr = self.collection.find({'when': {'$gte': from_time, '$lte': to_time}, 'type': element_type, 'done': False, 'deleted':False})
        return [el for el in crsr]

    def get_all_elements(self, to_time):
        crsr = self.collection.find({'when':{'$lte':to_time}, 'done':False, 'deleted':False})
        return [el for el in crsr]

    def save(self, element):
        element['done'] = False
        result = self.collection.save(element)
        return result

    def remove(self, element_id):
        if element_id:
            return self.collection.update({'_id':element_id}, {'$set':{'deleted':True}})
        return None

    def save_error_parsed(self, element):
        result = self.error_collection.save(element)
        return result