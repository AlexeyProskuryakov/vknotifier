import datetime
from properties import notifications_types

__author__ = '4ikist'


class NotificationsHandler(object):
    def __init__(self, database):
        self.database = database

    def add_notification(self, when, whom, text, notification_type=notifications_types[0]):
        return self.database.save({'when': when, 'whom': whom, 'text': text, 'type': notification_type})

    def delete_notification(self, notification_id):
        return self.database.remove(notification_id)

    def get_notifications(self, from_time, to_time):
        def get_with_offset(offset_hours, element_type):
            result = []
            to_time_ = to_time + datetime.timedelta(hours=offset_hours)
            normal_notifications = self.database.get_elements(from_time, to_time_, element_type=element_type)
            for el in normal_notifications:
                when = el['when'] - datetime.timedelta(hours=offset_hours)
                if when - from_time < interval:
                    result.append(el)
            return result

        interval = to_time - from_time
        elements = self.database.get_elements(from_time, to_time, element_type=notifications_types[0])
        elements.extend(get_with_offset(1, notifications_types[1]))
        elements.extend(get_with_offset(24, notifications_types[2]))
        return elements

    def get_all_notifications(self):
        return self.database.get_all_elements(datetime.datetime.now())

    def set_notification_done(self, notification_id):
        self.database.set_done(notification_id)

    def add_error(self, message, whom):
        self.database.save_error_parsed({'whom': whom, 'when': datetime.datetime.now(), 'message': message})


