# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.request import urlopen
from ..items import Article
from scrapy.loader import ItemLoader

base_url = "https://pubmed.ncbi.nlm.nih.gov"
db = 'pubmed'


def getIDs(term):
    term = term.replace(' ', "%20")
    url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db={db}&term={term}&retmax=100000&sort=relevance&retmode=json'

    ref_data = urlopen(url)
    data_raw = ref_data.read()

    data = json.loads(data_raw)

    results = data['esearchresult']
    return results['idlist']


def getXmlArticlesUrl(ids):
    return f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={",".join(ids)}&retmode=xml&rettype=abstract'


class PubmedPeekSpider(scrapy.Spider):
    name = 'peek'
    page_size = 10
    max_pages = 10000/page_size

    def __init__(self, query='', ** kwargs):
        self.start_urls = [f'{base_url}/?term={query}']
        self.query = query
        super().__init__(**kwargs)

    def parse(self, response):
        total = 0

        total_dom = response.css("div.results-amount span.value::text")
        if(len(total_dom) > 0):
            total = int(total_dom[0].get().replace(",", ""))

        yield({"total": total, "url": response.url, "query": self.query})


class PubmedSpider(scrapy.Spider):
    name = 'pubmed'

    def __init__(self, query='', page_size=100, ** kwargs):
        ids = getIDs(query)
        ids_batched = [ids[i*page_size:(i+1)*page_size]
                       for i in range(0, round(len(ids)/page_size))]
        self.ids = ids
        self.start_urls = [getXmlArticlesUrl(ids) for ids in ids_batched]
        self.query = query
        super().__init__(**kwargs)

    def parse(self, response):
        # Get all articles from response
        for item in response.xpath('PubmedArticle'):
            loader = ItemLoader(item=Article(), selector=item)

            # Get Pubmed ID
            _id = item.xpath("MedlineCitation/PMID/text()").extract_first()
            loader.add_value("_id", _id)
            loader.add_value("url", f'{base_url}/{_id}/')

            article = item.xpath('MedlineCitation/Article')
            # Get Article Content
            title = article.xpath("ArticleTitle/text()").extract_first()
            short = article.xpath("Abstract").extract_first()

            loader.add_value("title", title)
            loader.add_value("short", short)

            # Get Journal Info
            journal = article.xpath('Journal')
            journal_title = journal.xpath('Title/text()').extract_first()
            journal_year = journal.xpath(
                'JournalIssue/PubDate/Year/text()').extract_first()
            journal_month = journal.xpath(
                'JournalIssue/PubDate/Month/text()').extract_first()

            loader.add_value(
                "journal", f"{journal_title}, {journal_year}-{journal_month}")

            yield loader.load_item()
