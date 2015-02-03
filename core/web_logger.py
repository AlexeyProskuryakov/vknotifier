# coding:utf-8
__author__ = '4ikist'

import logging
messages = []
class WebHandler(logging.StreamHandler):

    def emit(self, record):
        msg = self.format(record)
        messages.append(msg)
        return super(WebHandler, self).emit(record)
