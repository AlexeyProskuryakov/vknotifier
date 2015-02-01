# coding:utf-8
__author__ = '4ikist'
from setuptools import setup
import os
packages = ['requests==2.2.1','lxml==3.4.0','pymongo==2.6.3']
setup(name='vknotifier',          # <= Put your application name, in this case 'mysite'
       version='1.0',
       description='bot for todo or notifications at vk', # <= Put your description if you want
       author='4ikist',          # <= Your name!!!!
       author_email='example@example.com',
       url='https://pypi.python.org/pypi',
       install_requires=packages,
 )
