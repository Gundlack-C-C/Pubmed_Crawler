# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst


def remove_brewery_description(x):
    if x.startswith("Webauftritt"):
        return ''
    else:
        return x.strip()


def join_properties(x):
    properties = dict()
    for prop in x:
        for key, value in prop.items():
            properties[key] = value
    return properties


class BeerItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(
        output_processor=Join(),
        input_processor=MapCompose(str.strip)
    )
    short = scrapy.Field(
        output_processor=Join(),
        input_processor=MapCompose(str.strip)
    )
    description = scrapy.Field(
        output_processor=Join(),
        input_processor=MapCompose(
            remove_brewery_description,
            str.strip
        )
    )
    url = scrapy.Field(
        output_processor=Join()
    )
    color = scrapy.Field(
        output_processor=Join()
    )
    price = scrapy.Field(
        output_processor=Join()
    )
    url_img = scrapy.Field(
        output_processor=Join()
    )
    properties = scrapy.Field(
        output_processor=join_properties
    )
