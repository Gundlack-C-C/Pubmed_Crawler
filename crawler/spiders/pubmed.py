# -*- coding: utf-8 -*-
import scrapy

from crawler.items import Article
from scrapy.loader import ItemLoader

base_url = "https://pubmed.ncbi.nlm.nih.gov"


class PubmedSpider(scrapy.Spider):
    name = 'pubmed'
    # topics = ['NLP', 'Natural+Language+Processing', '"literature review"',
    #          '"market surveillance', 'literature searching', '"literature search"' '"medical regulation"', '"review literature"']
    max_pages = 1000

    def __init__(self, query='', session_id='', ** kwargs):
        self.start_urls = [f'{base_url}/?term={query}']
        self.session_id = session_id
        super().__init__(**kwargs)

    def parse(self, response):
        for item in response.css('article'):
            loader = ItemLoader(item=Article(), selector=item)

            title = item.css("a.docsum-title *::text").getall()
            loader.add_value("title", "".join(title))
            
            url = item.css("a.docsum-title::attr(href)")[0].get()
            loader.add_value("url", f'{base_url}{url}')
            loader.add_css("short", "div.full-view-snippet::text")
            loader.add_css("_id", "a.docsum-title::attr(data-article-id)")
            loader.add_css("journal", "span.full-journal-citation::text")

            yield loader.load_item()

        #next_page = response.css('a.paging--next::attr(href)')[0].get()
        # if next_page is not None:
        #    yield response.follow(next_page, self.parse)
