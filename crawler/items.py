# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

def clearWhitespaces(str):
    return " ".join(str.split())

def clearNewline(str):
    return " ".join(str.split("\n"))

class Article(scrapy.Item):
    _id = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    title = scrapy.Field(default="", input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    short = scrapy.Field(default="", input_processor=MapCompose(
        remove_tags, clearNewline, clearWhitespaces, str.strip, ), output_processor=Join())
    authors = scrapy.Field(default="", input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    url = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    journal = scrapy.Field(default="", input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    keywords = scrapy.Field(default=[])
