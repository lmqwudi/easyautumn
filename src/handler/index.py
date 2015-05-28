# -*- coding:utf-8 -*-

import tornado.web
from conf.config import PREFIX
from service import index


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            'index.html',
            prefix=PREFIX
        )
