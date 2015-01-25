# coding:utf-8
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from database import DataBaseHandler, time_step
from api import get_api
from after_retrievers import after_timedelta
from date_time_retrievers import retrieve_datetime
from text_retrievers import retrieve_notification_message, retrieve_type, retrieve_yes, retrieve_utc
import properties
from core import types, timezones


log = properties.logger.getChild('engine')


def get_user_timezone(user_id, api, db):
    utc_by_user = db.get_utc(user=user_id)
    if not utc_by_user:
        result = api.get('users.get', **{'user_ids': user_id, 'fields': 'timezone,city,country'})
        city = result[0].get('city')
        if not city:
            return None
        utc_by_city = db.get_utc(city=city['id'])
        if not utc_by_city:
            utc = timezones.get_utc(city['title'])
            if utc:
                db.set_utc(utc=utc, user=user_id, city=city['id'])
                return utc
        return utc_by_city
    return utc_by_user


def recognise_notification_date_time(text, user_utc):
    """
    recognising date time from text and returning this date time in utc 0
    :param text: some text containing datetime or after timedelta
    :param user_utc: utc of user which saying this
    :return:
    """
    date_time = retrieve_datetime(text)
    if not date_time:
        after_dt = after_timedelta(text)
        if not after_dt:
            return None
        date_time = datetime.utcnow() + after_dt
    else:
        date_time -= timedelta(hours=user_utc)

    type = retrieve_type(text)
    text = retrieve_notification_message(text)
    return {'when': date_time, 'type': type, 'message': text}


def form_notification_confirmation(notification, utc):
    when = notification['when'] + timedelta(hours=utc)
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


class TalkHandler(Thread):
    def __init__(self, api_credentials, db_credentials):
        super(TalkHandler, self).__init__()
        self.api = get_api(**api_credentials)
        self.db = DataBaseHandler(**db_credentials)

    def run(self):
        self.loop()

    def state_notification_confirm(self, message, talked_users, user_id):
        if retrieve_yes(message['text']):
            log.info('user %s say yes' % user_id)
            self.api.send_message(user_id, u':)')
            self.db.will_notify(**talked_users.get(user_id).get('data'))
        else:
            log.info('user %s say not' % user_id)
            self.api.send_message(user_id, properties.will_not_notify)
            self.db.persist_error(user_id, message['text'], reject_confirm=True)
        del talked_users[user_id]

    def state_utc_recognise(self, message, talked_users, user_id):
        utc = retrieve_utc(message['text'])
        if not utc:
            self.state_utc_not_recognised(talked_users[user_id]['data'], talked_users, user_id)
            return
        self.state_notification_estimate(talked_users[user_id]['data'], talked_users, user_id, utc)

    def state_notification_estimate(self, message, talked_users, user_id, utc):
        notification = recognise_notification_date_time(message['text'], utc)
        if notification:
            notification = normalize_notification_type(notification)
            notification['whom'] = user_id

            log.info('from user %s imply notification %s' % (user_id, notification))
            self.api.send_message(user_id, form_notification_confirmation(notification, utc))

            talked_users[user_id] = {'state': 'notification_confirmation', 'data': notification}
        else:
            log.info('from user %s notification not implied' % (user_id))
            self.api.send_message(user_id, properties.not_recognised_message % message['text'])
            self.db.persist_error(user_id, 'not recognise notification', **message)

    def state_utc_not_recognised(self, message, talked_users, user_id):
        self.db.persist_error(user_id, 'utc error', **message)
        self.api.send_message(user_id, properties.can_not_recognise_utc)
        talked_users[user_id] = {'state': 'utc_estimation', 'data': message}

    def state_notification_recognise(self, message, talked_users, user_id):
        utc = get_user_timezone(user_id, self.api, self.db)
        if not utc:
            self.state_utc_not_recognised(message, talked_users, user_id)
            return
        self.state_notification_estimate(message, talked_users, user_id, utc)

    def loop(self):
        talked_users = {}
        for message in self.api.get_messages():
            try:
                user_id = message['from']
                log.info('receive message: "%s" from %s' % (message['text'], user_id))
                # retrieve confirmation of notification or utc time shift
                if user_id in talked_users:
                    state_flag = talked_users[user_id]
                    if state_flag['state'] == 'notification_confirmation':
                        self.state_notification_confirm(message, talked_users, user_id)
                    elif state_flag['state'] == 'utc_estimation':
                        self.state_utc_recognise(message, talked_users, user_id)
                else:  # processing text for notification
                    self.state_notification_recognise(message, talked_users, user_id)
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
