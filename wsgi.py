# coding:utf-8
__author__ = '4ikist'
import sys


def application(env, start_response):
    sys.stderr.write('app ')
    start_response('200 OK', [('Content-Type','text/html')])
    return ["Hello World"]

if __name__ == '__main__':
    from start import main
    main()
    from wsgiref.simple_server import make_server
    srv = make_server('localhost',8080,application)
    srv.serve_forever(3)