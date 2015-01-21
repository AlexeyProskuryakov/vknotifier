# coding:utf-8
__author__ = '4ikist'

import ConfigParser

from core.engine import NotificatonIniter, TalkHandler

if __name__ == '__main__':
    cfg = ConfigParser.RawConfigParser()
    cfg.read('properties.cfg')

    api_name = dict(cfg.items('main'))['api_name']
    api_credentials = {'api_name': api_name,
                       'login': dict(cfg.items(api_name))['login'],
                       'pwd': dict(cfg.items(api_name))['pwd']}
    print 'api:',api_credentials
    db_credentials = {'address': dict(cfg.items('storage'))['address'],
                      'db_name': dict(cfg.items('storage'))['db_name']}

    print 'db:', db_credentials
    TalkHandler(api_credentials, db_credentials).start()
    NotificatonIniter(api_credentials, db_credentials).start()