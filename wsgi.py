# coding:utf-8
__author__ = '4ikist'
import sys
import os
from core.web_logger import messages

def application(env, start_response):
    sys.stderr.write('app ')
    start_response('200 OK', [('Content-Type','text/html')])
    return messages

if __name__ == '__main__':
    environ = dict(os.environ.items())
    environ['wsgi.input'] = sys.stdin
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once'] = True

    if environ.get('HTTPS', 'off') in ('on', '1'):
        environ['wsgi.url_scheme'] = 'https'
    else:
        environ['wsgi.url_scheme'] = 'http'

    from start import main
    main()
    from wsgiref.simple_server import make_server
    srv = make_server('localhost',8080,application)
    srv.serve_forever(3)