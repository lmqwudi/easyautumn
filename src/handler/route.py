# -*- coding: utf-8 -*-

from handler import (
    index,
    website,
)


index_handlers = [
    (r'/', index.IndexHandler),
    (r'/index', index.IndexHandler),
]


website_handlers = [
    (r'/website', website.WebsiteHandler),
    (r'/website/count', website.WebsiteCountHandler),
]


#about_handlers = [
#    (r'/about', about.IndexHandler),
#]

handlers = (
    index_handlers + website_handlers
)
