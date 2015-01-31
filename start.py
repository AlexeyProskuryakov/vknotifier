# coding:utf-8
import ConfigParser
import sys

__author__ = '4ikist'

from core.engine import NotificatonIniter, TalkHandler, VKEventHandler


def load_config(prop_file):
    cfg = ConfigParser.RawConfigParser()
    cfg.read(prop_file)

    api_name = dict(cfg.items('main'))['api_name']
    api_credentials = {'api_name': api_name,
                       'login': dict(cfg.items(api_name))['login'],
                       'pwd': dict(cfg.items(api_name))['pwd']}
    print 'api:', api_credentials
    db_credentials = {'address': dict(cfg.items('storage'))['address'],
                      'db_name': dict(cfg.items('storage'))['db_name']}

    print 'db:', db_credentials
    return api_credentials, db_credentials


if __name__ == '__main__':
    api_credentials, db_credentials = load_config(sys.argv[1] if len(sys.argv) > 1 else 'properties.cfg')
    TalkHandler(api_credentials, db_credentials).start()
    NotificatonIniter(api_credentials, db_credentials).start()
    VKEventHandler(api_credentials, refresh_time=3600*3).start()