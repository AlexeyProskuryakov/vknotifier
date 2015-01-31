# coding:utf-8
from core.engine import VKEventHandler
from start import load_config

__author__ = '4ikist'
if __name__ == '__main__':
    api_credentials, _ = load_config('../properties.cfg')
    VKEventHandler(api_credentials,1).start()