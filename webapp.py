# -*- coding:utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.httpclient


from conf import config
from handler import route

settings = config.settings

from tornado.options import define, options
define('port', default=7000, help='run on the given port', type=int)

tornado.httpclient.AsyncHTTPClient.configure(
    "tornado.simple_httpclient.SimpleAsyncHTTPClient", max_clients=5)


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, route.handlers, **settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()
