# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


class BeerPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise "Database is not configured"

        db = db_settings['db']
        cred = db_settings['cred']
        url = db_settings['host']
        return cls(db, cred, url)

    def __init__(self, db, cred, url):
        self.db = db
        self.cred = credentials.Certificate(cred)
        self.databaseURL = url

    def open_spider(self, spider):
        # Initialize the app with a service account, granting admin privileges
        self.app = firebase_admin.initialize_app(
            self.cred, {'databaseURL': self.databaseURL})

        # As an admin, the app has access to read and write all data, regradless of Security Rules
        self.ref = db.reference(self.db)
        data = self.ref.get()
        print(data)

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        return item
