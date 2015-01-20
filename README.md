vknotifier
==========

Funny notifications from vk 

ATTENTION
==========
Do not use for your real account in vk! Because it will read your messages and will send some messages in russian language to any another account which want to tell you :) 

At first:
==========
git clone https://github.com/AlexeyProskuryakov/vknotifier.git

At next: 
==========
create file with name 
properties.py like this with login credentials in vk and mongo connection address:

```python
# coding=utf-8
import logging
import os
import sys


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

vk_login = 'vk_login_notifier'
vk_pass = 'vk_pass_notifier'

vk_access_credentials = {'client_id': 'app_id_in_vk',
                         'scope': 'friends,messages,notifications',
                         'redirect_uri': 'https://oauth.vk.com/blank.html',
                         'display': 'mobile',
                         'v': '4.104',
                         'response_type': 'token'}

mongo_adress = 'mongodb://<mongo_lab_user_name>:<mongo_lab_pass>@dbh44.mongolab.com:27447/notifier'

notifications_types = ['low', 'normal', 'high']
notifications_types_represent = {
    'low': u'',
    'normal': u'за 1 час и в это же время',
    'high': u'за 1 день и за 1 час',
}
not_recognised_message = u'Я не понимаю что ты написал(а) :( Попробуй написать по-другому [%s]' #with message text
will_not_notify = u'Хорошо, не буду напоминать'
will_notify = u"Я напомню тебе про: %s в [%s] %s" #with text, date, and notification type
notify_string = u"Напоминаю тебе: %s" #with notification text

```
START
==========
python core/engine.py

