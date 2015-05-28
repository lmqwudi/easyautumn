#-*- coding:utf-8 -*-


from base import Website, EngineFactory
from sqlalchemy import func

from util import log
logger = log.LogService().getLogger()

def insert_website(website):
    try:
        session = EngineFactory.get_boring_session()
        session.add(website)
        session.commit()
        return web.id
    except Exception as e:
        logger.error('insert website error, ' + str(e))
        session.rollback()
        return None
    finally:
        session.remove()


def delete_web(site_id):
    try:
        session = EngineFactory.get_boring_session()
        res = session.query(Website)\
            .filter(Website.id == site_id)\
            .delete()
        session.commit()
        return res
    except Exception as e:
        logger.error('delete website error, ' + str(e))
        session.rollback()
        return None
    finally:
        session.remove()


#def update_url(tag_id, **kwargs):
#    try:
#        session = EngineFactory.get_ec_session()
#        tag_keys = ['tag_name', 'tag_summary', 'tag_status']
#        tag = {k: kwargs[k] for k in tag_keys if kwargs.get(k, None) is not None} 
#        res = session.query(Tag)\
#            .filter(Tag.tag_id == tag_id)\
#            .update(tag)
#        session.commit()
#        return res
#    except Exception as e:
#        logger.error('update tag error, ' + str(e))
#        session.rollback()
#        return None
#    finally:
#        session.remove()
#

#def get_url_list(**kwargs):
#    try:
#        session = EngineFactory.get_ec_session()
#        keys = ['store_id', 'tag_status']
#        p = {k: kwargs[k] for k in keys if kwargs.get(k, None) is not None}
#        start = kwargs.get('start', 0)
#        end = kwargs.get('end', None)
#        id_list = session.query(Tag.tag_id)\
#            .filter_by(**p)\
#            .filter(Tag.tag_status != -1)\
#            .order_by(Tag.add_time.desc())\
#            .all()[start:end]
#        return [i[0] for i in id_list]
#    except Exception as e:
#        logger.error('get tag id list error, ' + str(e))
#        session.rollback()
#        return None
#    finally:
#        session.remove()


def get_website_by_id(site_id):
    try:
        session = EngineFactory.get_boring_session()
        website = session.query(Website)\
           .filter(Website.id == site_id)\
           .limit(1)\
           .all()
        return format_website(website[0])
    except Exception as e:
        logger.error('get web site by id error, ' + str(e))
        return None
    finally:
        session.remove()


def count():
    try:
        session = EngineFactory.get_boring_session()
        count = session.query(func.count(Website.id))\
            .all()
        return count[0][0]
    except Exception as e:
        logger.error('get website count error' + str(e))
        return 0
    finally:
        session.remove()


def format_website(website):
    if website is None:
        return {}
    data = {
        'id': website.id,
        'url': website.url,
        'add_time': str(website.add_time),
        }
    return data
