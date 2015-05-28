# -*-coding:utf-8 -*-

from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime, Float, Text 
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import mapper 
from sqlalchemy import exc
from sqlalchemy.pool import QueuePool


from conf.config import DB_HOST_CONFIG


class LookLively(object):
    """Ensures that MySQL connections checked out of the pool are alive."""
    def checkout(self, dbapi_con, con_record, con_proxy):
        try:
            try:
                dbapi_con.ping(False)
            except TypeError:
                dbapi_con.ping()
        except dbapi_con.OperationalError, ex:
            if ex.args[0] in (2006, 2013, 2014, 2045, 2055):
                raise exc.DisconnectionError()
            else:
                raise


class EngineFactory():

    engines = dict()
    session = None
    conn = None

    @classmethod
    def make_engine(cls, db_key):
        if not cls.engines.get(db_key, None):
            db_host_config = DB_HOST_CONFIG[db_key]
            cls.engines[db_key] = create_engine(
                db_host_config['host_url'],
                listeners=[LookLively()],
                poolclass=QueuePool,
                **db_host_config['kws']
                )

        return cls.engines[db_key]

    @classmethod
    def get_session(cls, db_key):
        if not cls.engines.get(db_key, None):
            cls.make_engine(db_key)
        if cls.session is None:
            cls.session = scoped_session(sessionmaker(bind=cls.engines[db_key]))
        return cls.session

    @classmethod
    def get_boring_session(cls):
        db_key = 'boring'
        if not cls.engines.get(db_key, None):
            cls.make_engine(db_key)
        if cls.session is None:
            cls.session = scoped_session(sessionmaker(bind=cls.engines[db_key]))
        return cls.session

    @classmethod
    def get_connection(cls):
        db_key = 'boring'
        if not cls.engines.get(db_key, None):
            cls.make_engine(db_key)
        if cls.conn is None:
            conn = cls.engines[db_key].connect()
        return conn    

metadata = MetaData()

website = Table(
    'website', metadata,
    Column('id', Integer, nullable=False, autoincrement=True, primary_key=True),
    Column('url', String(255), nullable=True, default=None),
    Column('add_time', DateTime, nullable=True, default=None),
    )

class Website(object):
    pass


mapper(Website, website)
