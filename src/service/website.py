# -*- coding:utf-8 -*-

import db.website
from db.base import Website
import time


def insert_website(params):
    if params.get('add_time', None) is None:
        params['add_time'] = time.strftime("%Y-%m-%d %X", time.localtime())
    website = Website()
    website.url = params.get('url', None)
    tag.add_time = params.get('add_time', None)
    return db.website.insert_website(website)


def get_website_by_id(site_id):
    return db.website.get_website_by_id(site_id)


def count():
    return db.website.count()
