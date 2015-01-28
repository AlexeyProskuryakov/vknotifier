# coding:utf-8
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from database import DataBaseHandler, time_step
from api import get_api
from after_retrievers import after_timedelta
from date_time_retrievers import retrieve_datetime
from text_retrievers import retrieve_notification_message, retrieve_type, retrieve_yes, \
    retrieve_utc, retrieve_set_utc, retrieve_mentioned
import properties
from core import types, timezones


log = properties.logger.getChild('engine')


def get_user_timezone(user_info, db):
    utc_by_user = db.get_utc(user=user_info['id'])
    if not utc_by_user:
        city = user_info['city']
        if not city:
            return None
        utc_by_city = db.get_utc(city=city['id'])
        if not utc_by_city:
            utc = timezones.get_utc(city['title'])
            if utc:
                db.set_utc(utc=utc, user=user_info['id'], city=city['id'])
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


def form_notification_confirmation(notification, user_info, db, utc):
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

    if notification['whom'] == user_info['id']:
        whom = u'тебе'
    else:
        def form_name(user_identity, by_id):
            if user_identity == by_id:
                return u'тебе'
            user_info = db.get_user(user_identity)
            return u'%s %s [%s]' % (user_info['first_name'], user_info['last_name'], user_info['domain'])

        if isinstance(notification['whom'], list):
            whom = ', '.join([form_name(ui, user_info['id']) for ui in notification['whom']])
        else:
            whom = form_name(notification['whom'], user_info['id'])

    one_when = len(whens) == 1
    result = properties.will_notify % (whom,
                                       notification['message'],
                                       u'ую' if one_when else u'ие',
                                       u'у' if one_when else u'ы',
                                       u'\n'.join([d.strftime("%d.%m.%Y %H:%M") for d in whens]),
                                       u'ен' if int(user_info['sex']) == 2 else u'на'
    )
    return result


def normalize_notification_type(notification):
    if datetime.utcnow() > (notification['when'] - types[notification['type']]):
        notification['type'] -= 1
        return normalize_notification_type(notification)
    return notification


def imply_whom_user_id(text, by_user_info, api):
    mentioned = retrieve_mentioned(text)
    if mentioned:
        friends = api.get('friends.get',
                          **{'user_id': by_user_info['id'],
                             'fields': 'nickname, domain, city'})['items'] + [by_user_info]

        results = {}

        def comparison(friend_info, user_identity):
            def similarity(one, two):
                result = 0
                lone = len(one)
                ltwo = len(two)
                max_len = lone if lone >= ltwo else ltwo
                for i in range(max_len):
                    result += 1 if lone >= i + 1 and ltwo >= i + 1 and one[i] == two[i] else 0
                return float(result) / max_len

            if 'domain' in user_identity:
                return 2 if user_identity['domain'] and \
                            user_identity['domain'] in (friend_info['domain'].lower(), friend_info.get('nickname')) \
                    else 0

            if 'id' in user_identity:
                return 2 if friend_info['id'] == int(user_identity['id']) else 0

            if 'name' in user_identity:
                names = user_identity['name']
                if names == [u'меня'] and friend_info['id'] == by_user_info['id']:
                    return 2
                fn = friend_info['first_name'].lower()
                ln = friend_info['last_name'].lower()
                if len(names) == 2:
                    return max(similarity(names[0], fn) + similarity(names[1], ln),
                               similarity(names[1], fn) + similarity(names[0], ln))
                else:
                    return max(similarity(names[0], fn), similarity(names[0], ln))

        for user_identity in mentioned:
            sim_list = [{'id': fi['id'], 'cmp': comparison(fi, user_identity), 'data': fi} for fi in friends]
            sim_list.sort(key=lambda x: x['cmp'])
            friend = sim_list[-1]
            if friend['cmp'] > 1.0:
                results[friend['id']] = friend['data']
            else:
                log.warn('friend %s \nseems bad recognised for identity:\n%s' % ( friend, user_identity))
        return results


stop_iteration = 'STOP'
continue_iteration = 'CONTINUE'

state_utc_estimation = 'utc_estimation'
state_notification_confirmation = 'notification_confirmation'


class StateHandler(object):
    def __init__(self):
        self.current_states = {}

    def set_state(self, identity, state, data=None):
        self.current_states[identity] = {'state': state, 'data': data}

    def get_state(self, identity):
        state = self.current_states.get(identity)
        if state:
            return state['state']

    def get_data(self, identity):
        state = self.current_states.get(identity)
        if state:
            return state['data']

    def remove_state(self, identity):
        if identity in self.current_states:
            del self.current_states[identity]


class TalkHandler(Thread):
    def __init__(self, api_credentials=None, db_credentials=None, api=None, db=None):
        super(TalkHandler, self).__init__()
        self.api = api or get_api(**api_credentials)
        self.db = db or DataBaseHandler(**db_credentials)
        self.states = StateHandler()

    def run(self):
        self.loop()

    def to_notification_confirm(self, message, user_id):
        if retrieve_yes(message['text']):
            log.info('user %s say yes' % user_id)
            self.api.send_message(user_id, u':)')
            self.db.will_notify(**self.states.get_data(user_id))
        else:
            log.info('user %s say not' % user_id)
            self.api.send_message(user_id, properties.will_not_notify)
            self.db.persist_error(user_id, message['text'], reject_confirm=True)
        self.states.remove_state(user_id)

    def to_utc_not_recognised(self, message, user_id):
        self.db.persist_error(user_id, 'utc error', **message)
        self.api.send_message(user_id, properties.can_not_recognise_utc)
        self.states.set_state(user_id, state_utc_estimation, message)

    def to_notification_estimate(self, message, user_info, utc):
        notification = recognise_notification_date_time(message['text'], utc)
        user_id = user_info['id']
        if notification:
            # implying who we will notify
            whom_users = imply_whom_user_id(message['text'], user_info, self.api)
            if whom_users:
                notification['whom'] = whom_users.keys()
                self.db.set_user(whom_users.values())
            else:
                notification['whom'] = user_id
            notification = normalize_notification_type(notification)

            notification['by'] = user_id
            log.info('from user %s \nimply notification %s' % (user_id, notification))
            self.api.send_message(user_id, form_notification_confirmation(notification, user_info, self.db, utc))

            self.states.set_state(user_id, state_notification_confirmation, notification)
        else:
            log.info('from user %s notification not implied' % (user_id))
            self.api.send_message(user_id, properties.not_recognised_message % message['text'])
            self.db.persist_error(user_id, 'not recognise notification', **message)

    def to_notification_recognise(self, message, user_info):
        utc = get_user_timezone(user_info, self.db)
        if not utc:
            self.to_utc_not_recognised(message, user_info['id'])
            return
        self.to_notification_estimate(message, user_info, utc)

    def to_utc_recognise(self, message, user_info):
        utc = retrieve_utc(message['text'])
        user_id = user_info['id']
        if not utc:
            self.to_utc_not_recognised(self.states.get_data(user_id), user_id)
        else:
            self.to_notification_estimate(self.states.get_data(user_id), user_info, utc)

    def to_setting_utc(self, message, user_info):
        set_utc = retrieve_set_utc(message['text'])
        if set_utc is not None:
            user_id = user_info['id']
            self.db.set_utc(set_utc, user=user_id, city=None)
            if self.states.get_state(user_id) == state_utc_estimation:
                self.to_notification_estimate(self.states.get_data(user_id), user_info, set_utc)
            return stop_iteration
        return continue_iteration

    def loop(self):
        for message in self.api.get_messages():
            try:
                user_id = message['from']
                user_info = self.db.get_user(user_id)
                if not user_info:
                    user_info = self.api.get('users.get',
                                             **{'user_ids': user_id, 'fields': 'city, domain, nickname, sex'})
                    if user_info:
                        user_info = user_info[0]
                        self.db.set_user(user_info)
                    else:
                        continue

                log.info('receive message: "%s" from %s' % (message['text'], user_id))

                iteration_state = self.to_setting_utc(message, user_info)
                if iteration_state == stop_iteration:
                    continue

                state = self.states.get_state(user_id)
                if state == state_notification_confirmation:
                    self.to_notification_confirm(message, user_id)
                elif state == state_utc_estimation:
                    self.to_utc_recognise(message, user_info)
                else:
                    self.to_notification_recognise(message, user_info)
            except Exception as e:
                log.exception(e)


def is_all_notified(notifications):
    for notification in notifications:
        if not notification.get('done'):
            return False
    return True


class NotificatonIniter(Thread):
    def __init__(self, api_credentials=None, db_credentials=None, api=None, db=None, near_date=None):
        super(NotificatonIniter, self).__init__()
        self.api = api or get_api(**api_credentials)
        self.db = db or DataBaseHandler(**db_credentials)
        self.near_date = near_date

    def run(self):
        self.loop()

    def loop(self):
        while True:
            try:
                result = self.db.get_to_notify(self.near_date)
                if result:
                    Notificator(self.api, self.db, result).start()
                sleep(time_step)
            except Exception as e:
                log.exception(e)


class Notificator(Thread):
    def __init__(self, api, db, notifications, when_notify=None):
        super(Notificator, self).__init__()
        self.api = api
        self.db = db
        self.notifications = notifications
        self.by_users = {}
        self.now = when_notify

    def notify(self, whom, by, text):
        if whom == by:
            by_str = u'сам'
        else:
            if by not in self.by_users:
                by_obj = self.db.get_user(by)
                self.by_users[by] = by_obj
            else:
                by_obj = self.by_users[by]
            by_str = u'%s %s' % (by_obj['first_name'], by_obj['last_name'])

        self.api.send_message(whom,
                              properties.notify_string % (text or u'... блин, не указано о чем напоминать :(',
                                                          by_str
                              ))

    def run(self):
        while 1:
            for notification in self.notifications:
                now = self.now or datetime.utcnow()
                if now > notification['when'] and 'done' not in notification:
                    if isinstance(notification['whom'], list):
                        for user_id in notification['whom']:
                            self.notify(user_id, notification['by'], notification['message'])
                    else:
                        self.notify(notification['whom'], notification['by'], notification['message'])

                    self.db.set_done(notification['_id'])
                    notification['done'] = True
            sleep(1)
            if is_all_notified(self.notifications):
                break
