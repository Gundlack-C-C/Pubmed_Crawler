# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter, PythonItemExporter
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime

import sys


class BeerFirebasePipeline(object):
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
        self.update_items = {}

    def _get_exporter(self, **kwargs):
        return PythonItemExporter(binary=False, **kwargs)

    def open_spider(self, spider):
        # Initialize the app with a service account, granting admin privileges
        self.app = firebase_admin.initialize_app(
            self.cred, {'databaseURL': self.databaseURL})

        # As an admin, the app has access to read and write all data, regradless of Security Rules
        ref = db.reference(self.db)
        self.data = ref.get()
        self.t_change = t = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if self.data == 'None':
            self.data = []

    def close_spider(self, spider):
        ref = db.reference(self.db)
        ref.update(self.update_items)

    def process_item(self, item, spider):
        ie = self._get_exporter()
        exported = ie.export_item(item)

        db_item = list(filter(lambda x: x['name'] ==
                              exported['name'], self.data.values()))
        db_item = db_item[0] if len(db_item) > 0 else None

        t = self.t_change
        if db_item == None:
            # Create new Entry
            ref = db.reference(self.db)
            key = ref.push().key

            exported['key'] = key
            exported['created'] = t
            exported['changed'] = t

            ref.update({key: exported})
        else:
            # Update Entry
            key = db_item['key']
            exported['changed'] = t
            exported['created'] = db_item['created'] if 'created' in db_item else t
            self.update_items[key] = exported

        return exported


class JSONPipeline(object):
    @ classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        file_settings = crawler.settings.getdict("FILE_SETTINGS")
        if not file_settings:
            raise "Database is not configured"

        path = file_settings['out']
        return cls(path)

    def __init__(self, path="data_export.json"):
        self.file = open(path, 'wb')
        self.exporter = JsonItemExporter(
            self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
