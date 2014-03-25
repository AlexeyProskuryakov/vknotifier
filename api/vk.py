from collections import defaultdict
from datetime import datetime
import json
import urlparse
from requests import Session
from lxml import html

from src.properties import *

__author__ = '4ikist'

log = logger.getChild("vk_api")


class APIException(Exception):
    pass


class VK_API():
    def __init__(self):
        self.session = Session()
        self.session.verify = certs_path
        self.base_url = 'https://api.vk.com/method/'
        self.__get_access_token()

    def __get_access_token(self):
        if (not hasattr(self, 'access_expires') and not hasattr(self, 'last_auth')) or (
                self.last_auth - datetime.now()).total_seconds() > self.access_expires:
            auth = self.__auth__()
            self.access_token = auth['access_token']
            self.user_id = auth['user_id']
            self.access_expires = auth['expires_in']
            self.last_auth = datetime.now()

        return self.access_token

    def __auth__(self):
        log.info('authenticate')
        result = self.session.get('https://oauth.vk.com/authorize', params=vk_access_credentials)
        doc = html.document_fromstring(result.content)
        inputs = doc.xpath('//input')
        form_params = {}
        for el in inputs:
            form_params[el.attrib.get('name')] = el.value
        form_params['email'] = vk_login
        form_params['pass'] = vk_pass
        form_url = doc.xpath('//form')[0].attrib.get('action')
        #process second page
        result = self.session.post(form_url, form_params)
        doc = html.document_fromstring(result.content)
        #if already login
        if 'OAuth Blank' not in doc.xpath('//title')[0].text:
            submit_url = doc.xpath('//form')[0].attrib.get('action')
            result = self.session.post(submit_url, cookies=result.cookies)

        #retrieving access token from url
        parsed_url = urlparse.urlparse(result.url)
        if 'error' in parsed_url.query:
            log.error('error in authenticate \n%s' % parsed_url.query)
            raise APIException(dict([el.split('=') for el in parsed_url.query.split('&')]))

        fragment = parsed_url.fragment
        access_token = dict([el.split('=') for el in fragment.split('&')])
        return access_token


    def get(self, method_name, **kwargs):
        params = dict({'access_token': self.__get_access_token()}, **kwargs)
        result = self.session.get('%s%s' % (self.base_url, method_name), params=params)
        result_object = json.loads(result.content)
        if 'error' in result_object:
            raise APIException(result_object)
        return result_object['response']

    def get_new_messages(self):
        batch_count = 100
        params = {'out': 0, 'time_offset': 0, 'preview_length': 0, 'offset': 0}
        last_unread = None
        last_unread_position = None
        unread_messages = []
        unread_users = defaultdict(set)
        #filling unread messages
        while True:
            params['count'] = batch_count
            result = self.get('messages.get', **params)
            for i, message in enumerate(result[1:]):
                if message['read_state'] == 0:
                    unread_messages.append({'from': message['uid'], 'text': message['body'], 'date':message['date']})
                    last_unread = message['mid']
                    last_unread_position = i
                    unread_users[message['uid']].add(message['mid'])
            if last_unread_position < batch_count - 1:
                break
            else:
                params['last_message_id'] = last_unread

        #sending that read
        for user, messages in unread_users.iteritems():
            messages_str = ','.join([str(m) for m in messages])
            result = self.get('messages.markAsRead', **{'message.ids': messages_str, 'user_id': user})
            if result != 1:
                log.error('can not send that messages %s\n for user %s is not read' % (messages_str, str(user)))
        return unread_messages

    def send_message(self, user_id, text):
        params = {'user_id': user_id, 'message': text}
        result = self.get('messages.send', **params)
        return result

    def add_followers_to_friends(self):
        params = {'count': 100, 'filters': 'followers'}
        result = self.get('notifications.get', **params)
        followers = []
        for follower_meta in result['items'][1:]:
            if follower_meta['type'] == 'follow':
                for follower_id in follower_meta['feedback']:
                    followers.append(follower_id['owner_id'])
        for el in followers:
            result = self.get('friends.add', **{'user_id': el})
            if result != 2:
                log.error('error in add to friend for user: %s' % el)


if __name__ == '__main__':
    vk = VK_API()
    print vk.get_new_messages()
    print vk.add_followers_to_friends()
