# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst


class Article(scrapy.Item):
    _id = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    title = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    short = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    authors = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    url = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    journal = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
