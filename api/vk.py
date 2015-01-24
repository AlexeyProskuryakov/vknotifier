# coding=utf-8
from datetime import datetime
import json
import urlparse
from requests import Session
from lxml import html

from properties import *
import properties

__author__ = '4ikist'

log = logger.getChild("vk_api")


class APIException(Exception):
    pass


class VK_API():
    def __init__(self, login, pwd):
        self.session = Session()
        self.session.verify = certs_path
        self.base_url = 'https://api.vk.com/method/'
        self.login = login
        self.pwd = pwd
        self.__get_access_token(login, pwd)

    def __form_lp_server_address(self, ts=None):
        if ts is None:
            self.lp_server_params = self.get('messages.getLongPollServer')

        self.lp_server_connection = 'http://%s?act=a_check&key=%s&ts=%s&wait=25&mode=0' % (
            self.lp_server_params.get('server'),
            self.lp_server_params.get('key'),
            self.lp_server_params.get('ts') if ts is None else ts)

    def __get_access_token(self, login, pwd):
        if (not hasattr(self, 'access_expires') and not hasattr(self, 'last_auth')) or (
                    self.last_auth - datetime.now()).total_seconds() > self.access_expires:
            auth = self.__auth__(login, pwd)
            self.access_token = auth['access_token']
            self.user_id = auth['user_id']
            self.access_expires = auth['expires_in']
            self.last_auth = datetime.now()

        return self.access_token

    def __auth__(self, vk_login, vk_pass):
        log.info('auth...')
        result = self.session.get('https://oauth.vk.com/authorize', params=vk_access_credentials)
        doc = html.document_fromstring(result.content)
        inputs = doc.xpath('//input')
        form_params = {}
        for el in inputs:
            form_params[el.attrib.get('name')] = el.value
        form_params['email'] = vk_login
        form_params['pass'] = vk_pass
        form_url = doc.xpath('//form')[0].attrib.get('action')
        # process second page
        result = self.session.post(form_url, form_params)
        doc = html.document_fromstring(result.content)
        # check if at bad place
        bad_place_result = self.process_bad_place(doc,'http://vk.com', result.cookies)
        if bad_place_result:
            result = bad_place_result
            doc = html.document_fromstring(result.content)
        # if already login
        if 'OAuth Blank' not in doc.xpath('//title')[0].text:
            submit_url = doc.xpath('//form')[0].attrib.get('action')
            log.info('will submiting to url: \n%s \nand have this page:\n%s'%(submit_url, result.content))
            result = self.session.post(submit_url, cookies=result.cookies)

        # retrieving access token from url
        parsed_url = urlparse.urlparse(result.url)
        if 'error' in parsed_url.query:
            log.error('error in authenticate \n%s' % parsed_url.query)
            raise APIException(dict([el.split('=') for el in parsed_url.query.split('&')]))

        fragment = parsed_url.fragment
        access_token = dict([el.split('=') for el in fragment.split('&')])
        log.info('auth was successful')
        return access_token

    def process_bad_place(self, doc, url, cookies):
        h4s = doc.xpath('//h4[@class="sub_header"]')
        if h4s:
            if h4s[0].text == u'Проверка безопасности':
                submit_url_postfix = doc.xpath('//form')[0].attrib.get('action')
                result = self.session.post("%s%s"%(url, submit_url_postfix), data={'code':self.login[1:-2]})
                log.info('after processing bad place i have this result:\n%s'%result.content)
                return result


    def get(self, method_name, **kwargs):
        params = dict({'access_token': self.__get_access_token(self.login, self.pwd), 'v':properties.vk_access_credentials['v']}, **kwargs)
        result = self.session.get('%s%s' % (self.base_url, method_name), params=params)
        result_object = json.loads(result.content)
        if 'error' in result_object:
            if result_object['error']['error_code'] == 14:
                kwargs['captcha_key'] = raw_input(
                    "please input what you see at [%s]" % result_object['error']['captcha_img'])
                kwargs['captcha_sid'] = result_object['error']['captcha_sid']
                return self.get(method_name, **kwargs)
            raise APIException(result_object)
        return result_object['response']

    def mark_as_read(self, messages):
        messages_str = ','.join([str(m) for m in messages])
        result = self.get('messages.markAsRead', **{'message_ids': messages_str})
        if result != 1:
            log.error('can not mark as read messages %s' % messages_str)

    def get_messages(self):
        self.__form_lp_server_address()
        log.info('will retrieve messages')
        while True:
            result = self.session.get(self.lp_server_connection)
            result = json.loads(result.content)
            if result.get('failed') == 2:
                self.__form_lp_server_address()
            else:
                self.__form_lp_server_address(ts=result.get('ts'))
            read_messages = []
            if 'updates' not in result:
                log.warn("i have this result: %s"%result)
                continue
            for update in result['updates']:
                if update[0] == 4 and update[2] in (1, 17, 33, 49) and update[2] != 3:
                    message_id = update[1]
                    from_id = update[3]
                    text = update[-1]
                    tstamp = update[4]
                    read_messages.append(message_id)
                    yield {'from': from_id, 'text': text.lower(), 'timestamp': tstamp}
            if read_messages:
                self.mark_as_read(read_messages)

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
