# coding:utf-8
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from database import DataBaseHandler, time_step
from api import get_api
from after_retrievers import after_timedelta
from date_time_retrievers import retrieve_datetime
from text_retrievers import retrieve_notification_message, retrieve_type, retrieve_yes
import properties
from core import types


log = properties.logger.getChild('engine')


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


def form_notification_confirmation(notification, when):
    whens = []
    if notification['type'] == 1:
        whens.append(when)
    elif notification['type'] == 2:
        whens.append(when - types[2])
        whens.append(when)
    elif notification['type'] == 3:
        whens.append(when)
        whens.append(when - types[2])
        whens.append(when - types[3])

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
    def __init__(self, api_credentials, db_credentials):
        super(TalkHandler, self).__init__()
        self.api = get_api(**api_credentials)
        self.db = DataBaseHandler(**db_credentials)

    def run(self):
        self.loop()

    def loop(self):
        talked_users = {}
        for message in self.api.get_messages():
            try:
                user_id = message['from']
                log.info('receive message: %s\nfrom %s' % (message['text'], user_id))
                # wait confirmation of notification
                if user_id in talked_users:
                    if retrieve_yes(message['text']):
                        log.info('user %s say yes' % user_id)
                        self.api.send_message(user_id, u':)')
                        self.db.will_notify(**talked_users.get(user_id))
                    else:
                        log.info('user %s say not' % user_id)
                        self.api.send_message(user_id, properties.will_not_notify)
                        self.db.persist_error(user_id, message['text'], reject_confirm=True)

                    del talked_users[user_id]
                else:  # processing text for notification
                    notification = recognise_notification_query(message['text'])
                    if notification:
                        notification = normalize_notification_type(notification)
                        when_to_show = notification['when']  # когда должна быть
                        notification['when'] = form_when_on_timestmap(notification['when'], message['timestamp'])
                        log.debug('\nwhen to show: %s\nwhen notify: %s\ntimestamp: %s' % (
                            when_to_show,
                            notification['when'],
                            datetime.fromtimestamp(message['timestamp']))
                        )
                        notification['whom'] = user_id
                        talked_users[user_id] = notification
                        log.info('from user %s imply notification %s' % (user_id, notification))
                        self.api.send_message(user_id, form_notification_confirmation(notification, when_to_show))
                    else:
                        log.info('from user %s notification not implied' % (user_id))
                        self.api.send_message(user_id, properties.not_recognised_message % message['text'])
                        self.db.persist_error(user_id, message['text'])
            except Exception as e:
                log.exception(e)


def is_all_notified(notifications):
    for notification in notifications:
        if not notification.get('done'):
            return False
    return True


class NotificatonIniter(Thread):
    def __init__(self, api_credentials, db_credentials):
        super(NotificatonIniter, self).__init__()
        self.api = get_api(**api_credentials)
        self.db = DataBaseHandler(**db_credentials)

    def run(self):
        self.loop()

    def loop(self):
        while True:
            try:
                result = self.db.get_to_notify()
                if result:
                    Notificator(self.api, self.db, result).start()
                sleep(time_step)
            except Exception as e:
                log.exception(e)


class Notificator(Thread):
    def __init__(self, api, db, notifications):
        super(Notificator, self).__init__()
        self.api = api
        self.db = db
        self.notifications = notifications

    def run(self):
        while 1:
            for notification in self.notifications:
                if datetime.now() > notification['when'] and 'done' not in notification:
                    self.api.send_message(notification['whom'],
                                          properties.notify_string % (
                                              notification['message'] or u'... блин, ты не указал о чем напоминать :('))
                    self.db.set_done(notification['_id'])
                    notification['done'] = True

            if is_all_notified(self.notifications):
                break
