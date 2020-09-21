# -*- coding: utf-8 -*-
import scrapy

from beer.items import BeerItem
from scrapy.loader import ItemLoader


class BierInFrankenSpider(scrapy.Spider):
    name = 'bier_in_franken'
    start_urls = [
        'https://www.hier-gibts-bier.de/de/bier-aus-franken/?p=1&n=48'
    ]

    def parse(self, response):
        for item in response.css('div.product--box'):
            loader = ItemLoader(item=BeerItem(), selector=item)
            loader.add_css("name", "a.product--title::text")
            loader.add_css("short", "div.product--description::text")
            url = item.css("a.product--title::attr(href)").get()

            yield scrapy.Request(
                url,
                callback=self.parse_detail,
                meta={"loader": loader}
            )

        #next_page = response.css('a.paging--next::attr(href)')[0].get()
        # if next_page is not None:
        #   yield response.follow(next_page, self.parse)

    def parse_detail(self, response):
        loader = response.meta.get('loader')
        loader.selector = response

        # Get URL
        loader.add_value("url", response.url)

        # Get Image
        loader.add_css(
            "url_img", "div.product--image-container img::attr(src)"
        )

        # Get Description
        loader.add_css("description", "div.product--description p::text")

        ###
        # Get Properties
        ###

        # Price
        price = response.css(
            "span.price--content meta::attr(content)"
        ).get().strip()
        # Color
        color = response.css(
            "div.hgb-beer-color-badge::attr(style)"
        ).re("(?<=background-color: )(.*)(?= !important)")[0]
        loader.add_value("properties", {"price": price, "color": color})
        # Properties Table
        self.get_properties_table(response, loader)

        # Done
        yield loader.load_item()

    def get_properties_table(self, response, loader):
        properties = dict()
        for prop in response.css("tr.product--properties-row"):
            key = prop.css(
                "td.product--properties-label::text"
            ).get().strip(":")
            value = prop.css("td.product--properties-value::text").get()
            properties[key] = value

        loader.add_value("properties", properties)
        return loader
