# coding=utf-8
from datetime import datetime, timedelta
from threading import Thread
import time

from src.api.vk import VK_API
from src.core.database import DataBaseHandler
from src.core.message_processing import ParseException, is_reject_message
from src.core.notifications import NotificationsHandler
from src.properties import logger, notifications_types_represent
from src.core.message_processing import process_message


__author__ = '4ikist'

log = logger.getChild('engine')
notification_time_window = 10


class Provider(Thread):
    def __init__(self, notify_handler, api, process_function, is_reject_function):
        super(Provider, self).__init__()
        self.notify_handler = notify_handler
        self.process = process_function
        self.is_reject = is_reject_function
        self.api = api
        self.sent_results = {}

    def run(self):
        while 1:
            self.api.add_followers_to_friends()
            messages = self.api.get_new_messages()
            for message in messages:
                try:
                    date, text, notification_type = None, None, None
                    if message['from'] in self.sent_results:
                        if is_reject_message(message['text']):
                            self.notify_handler.delete_notification(self.sent_results[message['from']])
                            del self.sent_results[message['from']]
                            try:
                                date, text, notification_type = self.process(message['text'], message['date'])
                            except ParseException:
                                self.api.send_message(message['from'], u'Хорошо, не буду напоминать')
                                continue

                    if not date and not text and not notification_type:
                        date, text, notification_type = self.process(message['text'], message['date'])
                    send_text = u"Напоминаю тебе: %s" % text
                    result_message = u"Я напомню тебе про: %s в [%s] %s" % (
                        text, date.isoformat(sep='|'), notifications_types_represent[notification_type])
                    self.api.send_message(message['from'], result_message)
                    notification_id = self.notify_handler.add_notification(when=date, whom=message['from'],
                                                                           text=send_text,
                                                                           notification_type=notification_type)
                    self.sent_results[message['from']] = notification_id
                except ParseException as e:
                    result = self.api.send_message(message['from'], u'Я не могу распознать то что ты написал(а) :( '
                                                                    u'Попробуй написать по-другому [%s]' % message[
                                                                        'text'])
                    log.error('send that message not recognised to: %s with result: %s' % (message['from'], result))
                    self.notify_handler.add_error(message['text'], message['from'])
            time.sleep(5)


class Notifier(Thread):
    def __init__(self, notify_handler, api):
        super(Notifier, self).__init__()
        self.notify_handler = notify_handler
        self.api = api

    def run(self):
        is_first = True
        while 1:
            if is_first:
                notifications = self.notify_handler.get_all_notifications()
                start = 0
                end = datetime.now()
            else:
                end = datetime.now()
                start = datetime.now() - timedelta(seconds=notification_time_window)
                notifications = self.notify_handler.get_notifications(start, end)

            for notification in notifications:
                sender = NotificationSender(notification, self.notify_handler, self.api)
                sender.start()
            time.sleep(notification_time_window)
            is_first = False


class NotificationSender(Thread):
    def __init__(self, notification, notification_engine, api):
        super(NotificationSender, self).__init__()
        self.notification = notification
        self.api = api
        self.notification_engine = notification_engine

    def run(self):
        while 1:
            if self.notification['when'] <= datetime.now():
                result = self.api.send_message(self.notification['whom'], self.notification['text'])
                self.notification_engine.set_notification_done(self.notification['_id'])
                break
            else:
                time.sleep(5)


if __name__ == '__main__':
    api = VK_API()
    db = DataBaseHandler()
    notification_handler = NotificationsHandler(db)

    provider = Provider(notification_handler, api, process_message, is_reject_message)
    provider.start()

    notifier = Notifier(notification_handler, api)
    notifier.start()

    provider.join()