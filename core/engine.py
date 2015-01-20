# coding:utf-8
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from database import DataBaseHandler
from api.vk import VK_API
from after_retrievers import after_timedelta
from date_time_retrievers import retrieve_datetime
from text_retrievers import retrieve_notification_message, retrieve_type, retrieve_yes
import properties
from core import types

api = VK_API()


def recognise_notification_query(text):
    date_time = retrieve_datetime(text)
    if not date_time:
        after_dt = after_timedelta(text)
        if not after_dt:
            return None
        date_time = datetime.now() + after_dt
    type = retrieve_type(text)
    text = retrieve_notification_message(text)
    return {'when': date_time, 'type': type, 'message': text}


def form_notification_confirmation(notification):
    whens = []
    if notification['type'] == 1:
        whens.append(notification['when'])
    elif notification['type'] == 2:
        whens.append(notification['when'] - types[2])
        whens.append(notification['when'])
    elif notification['type'] == 3:
        whens.append(notification['when'])
        whens.append(notification['when'] - types[2])
        whens.append(notification['when'] - types[3])

    return properties.will_notify % (
        notification['message'], u'\n'.join([d.strftime("%d.%m.%Y %H:%M") for d in whens]))


def normalize_notification_type(notification):
    if datetime.now() > (notification['when'] - types[notification['type']]):
        notification['type'] -= 1
        return normalize_notification_type(notification)
    return notification

def form_when_on_timestmap(when, timestamp):
    shift = (datetime.now() - datetime.fromtimestamp(timestamp)).total_seconds()
    if abs(shift) > 3600:
        return when + timedelta(seconds=shift)
    return when


class TalkHandler(Thread):
    def __init__(self):
        super(TalkHandler, self).__init__()
        self.api = api
        self.db = DataBaseHandler()

    def run(self):
        self.loop()

    def loop(self):
        talked_users = {}
        for message in self.api.get_messages():
            print datetime.fromtimestamp(message['timestamp'])
            user_id = message['from']
            #wait confirmation of notification
            if user_id in talked_users:
                if retrieve_yes(message['text']):
                    self.api.send_message(user_id, u':)')
                    self.db.will_notify(**talked_users.get(user_id))
                else:
                    self.api.send_message(user_id, properties.will_not_notify)

                del talked_users[user_id]
            else: #processing text for notification
                notification = recognise_notification_query(message['text'])
                if notification:
                    notification = normalize_notification_type(notification)
                    notification['when'] = form_when_on_timestmap(notification['when'], message['timestamp'])
                    notification['whom'] = user_id
                    talked_users[user_id] = notification
                    self.api.send_message(user_id, form_notification_confirmation(notification))
                else:
                    self.api.send_message(user_id, properties.not_recognised_message % message['text'])


def is_all_notified(notifications):
    for notification in notifications:
        if not notification.get('done'):
            return False
    return True


class Notificator(Thread):
    def __init__(self):
        super(Notificator, self).__init__()
        self.api = api
        self.db = DataBaseHandler()

    def run(self):
        self.loop()

    def loop(self):
        while True:
            result = self.db.get_to_notify()
            while 1:
                for notification in result:
                    if datetime.now() > notification['when'] and 'done' not in notification:
                        self.api.send_message(notification['whom'], properties.notify_string % (notification['message']))
                        self.db.set_done(notification['_id'])
                        notification['done'] = True

                if is_all_notified(result):
                    break

                sleep(1)


if __name__ == '__main__':
    # get_user_utc(10130611)
    TalkHandler().start()
    Notificator().start()



