# -*- coding:utf-8 -*-

import tornado.web
from conf.config import PREFIX
import service.website
from tornado.escape import json_encode
import random


class WebsiteHandler(tornado.web.RequestHandler):
    def get(self):
        default_web = {}
        default_web['id'] = 0
        default_web['url'] = '182.92.233.150:7001'
        count = service.website.count()
        site_id = random.randint(0, count-1)
        website = service.website.get_website_by_id(site_id)
        if website is not None:
            self.finish(self.write(json_encode(website)))
        else:
            self.finish(self.write(json_encode(default_web)))

    def post(self, url):
        p = {
            'url': url
        }
        r = service.website.insert_website(p)
        if r is not None:
            self.finish(self.wrap_response())
        else:
            raise InternalError('Add website Fail')


class WebsiteCountHandler(tornado.web.RequestHandler):
    def get(self):
        count = service.website.count()
        self.finish(self.write(str(count)))


if __name__ == '__main__':
    web = service.website.get_website_by_id(1)
    print web
    print service.website.count()
