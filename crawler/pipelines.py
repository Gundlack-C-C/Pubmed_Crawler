# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter
import os


class JSONPipeline(object):
    @ classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        file_settings = crawler.settings.getdict("FILE_SETTINGS")
        if not file_settings or 'out' not in file_settings.keys():
            raise "FILE_SETTINGS missing or incomplete for JSONPipeline"

        path = file_settings.get('out', './.out/pubmed_result.json')
        overwrite = file_settings.get('overwrite', True)
        return cls(path, overwrite)

    def __init__(self, path="data_export.json", overwrite=False):
        if not os.path.exists(os.path.abspath(os.path.dirname(path))):
            os.makedirs(os.path.abspath(os.path.dirname(path)))

        if overwrite and os.path.isfile(path):
            os.remove(path)

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
