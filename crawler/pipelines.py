# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter, PythonItemExporter


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
