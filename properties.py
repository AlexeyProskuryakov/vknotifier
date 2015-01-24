# coding=utf-8
import logging
import os
import sys

__author__ = '4ikist'


def module_path():
    if hasattr(sys, "frozen"):
        return os.path.dirname(
            unicode(sys.executable, sys.getfilesystemencoding())
        )
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))


log_file = os.path.join(module_path(), 'result.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_file)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s[%(levelname)s] %(name)s : %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

logging.getLogger('requests.packages.urllib3.connectionpool').propagate = False

certs_path = os.path.join(module_path(), 'cacert.pem')

vk_access_credentials = {'client_id': '4252682',
                         'scope': 'friends,photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,messages,notifications',
                         'redirect_uri': 'https://oauth.vk.com/blank.html',
                         'display': 'mobile',
                         'v': '5.8',
                         'response_type': 'token'}

not_recognised_message = u'Я не понимаю что ты написал(а) :( Попробуй написать по-другому [%s]\n' #with message text
will_not_notify = u'Хорошо, не буду напоминать, но ты всегда можешь меня об этом попросить:)'
will_notify = u"Я напомню тебе про: %s. В следующие дату(ы) и время: \n%s\n Согласен(на)? " #with text, date, and notification type
notify_string = u"Напоминаю тебе: %s" #with notification text
can_not_recognise_utc = u"Не могу распознать твое UTC, напиши мне его"
