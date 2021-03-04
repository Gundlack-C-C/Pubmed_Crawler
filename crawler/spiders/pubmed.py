# -*- coding: utf-8 -*-
import scrapy

from ..items import Article
from scrapy.loader import ItemLoader

base_url = "https://pubmed.ncbi.nlm.nih.gov"

class PubmedPeekSpider(scrapy.Spider):
    name = 'peek'
    page_size = 10
    max_pages = 10000/page_size

    def __init__(self, query='', ** kwargs):
        self.start_urls = [f'{base_url}/?term={query}']
        self.query = query
        super().__init__(**kwargs)

    def parse(self, response):
        urls = []
        total = 0
        # Get all other pages if on first page
        if response.url.find('page=') < 0:
            total = response.css(
                "div.results-amount span.value::text")[0].get()
            total = int(total.replace(",", ""))
            pages = round(total/self.page_size)

            for i in range(min(pages, self.max_pages)):
                urls.append(f'{response.url}&page={i}')

        yield({"total": total, "urls": urls})


class PubmedSpider(scrapy.Spider):
    name = 'items'
    max_pages = 1000
    page_size = 10

    def __init__(self, url="", ** kwargs):
        assert len(url) > 0, "No urls to crawl"
        self.start_urls = url
        super().__init__(**kwargs)

    def parse(self, response):
        # Get all articles from response
        for item in response.css('article'):
            loader = ItemLoader(item=Article(), selector=item)

            title = item.css("a.docsum-title *::text").getall()
            loader.add_value("title", "".join(title))

            short = item.css("div.full-view-snippet *::text").getall()
            loader.add_value("short", "".join(short))

            url = item.css("a.docsum-title::attr(href)")[0].get()
            loader.add_value("url", f'{base_url}{url}')

            loader.add_css("_id", "a.docsum-title::attr(data-article-id)")
            loader.add_css("journal", "span.full-journal-citation::text")

            yield loader.load_item()
