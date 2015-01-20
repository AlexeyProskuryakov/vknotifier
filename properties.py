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
logger.setLevel(logging.INFO)
fh = logging.FileHandler(log_file)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s[%(levelname)s] %(name)s : %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

certs_path = os.path.join(module_path(), 'cacert.pem')

vk_login = ''
vk_pass = ''

vk_access_credentials = {'client_id': '4252682',
                         'scope': 'friends,photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,messages,notifications',
                         'redirect_uri': 'https://oauth.vk.com/blank.html',
                         'display': 'mobile',
                         'v': '4.104',
                         'response_type': 'token'}

mongo_address = ''
mongo_db_name = 'vkntf'

mongo_address_test = ''
mongo_db_name_test = 'vkntf_test'

not_recognised_message = u'''Я не понимаю что ты написал(а) :( Попробуй написать по-другому [%s]\n
Пиши дату в свободной форме, к примеру: "4 января" или "4.01" или "в январе 4 числа", можешь уточнять год.
Можешь назначить завтрашную или послезавтрашнюю дату, написав просто "завтра" или "послезавтра".
Можешь указать день недели и уточнить какой он будет по счету - этот или следующий, например: "в следующий вторник".
Время всегда пиши по-нормальному - с двоеточием между часами и минутами, к примеру: "12:34".
Либо укажи через сколько напомнить, например: "через 10 минут"
О чем напомнить пиши после двоеточия и пробела, то есть для того чтобы завтра я тебе напомнил чтобы ты влюбился и забылся
напиши мне - "в 12:34, завтра: влюбиться и забыться"

Сколько раз напомнить зависит от поставленых подряд восклицательных знаков.
Ни одного или один - во время которое ты указал;
Два - за час + во время которое ты указал;
Три - за день и за час и во время которое ты указал.

''' #with message text
will_not_notify = u'Хорошо, не буду напоминать, но ты всегда можешь меня об этом попросить:)'
will_notify = u"Я напомню тебе про: %s. В следующие дату(ы) и время: \n%s\n Согласен(на)? " #with text, date, and notification type
notify_string = u"Напоминаю тебе: %s" #with notification text
