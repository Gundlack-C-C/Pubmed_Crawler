
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Callbacks
from scrapy import signals
from scrapy.signalmanager import dispatcher
from Crawler.crawler.spiders.pubmed import PubmedSpider, PubmedPeekSpider

import logging
import uuid
import binascii
import timeit

logger = logging.getLogger("SessionService")

def empty_fn(x, y):
    pass

def str2hex(text):
    return binascii.hexlify(text.encode()).decode('utf-8')

class SessionPeekService():
    def __init__(self, queries, LOG_ENABLED=False, LOG_LEVEL="INFO"):
        assert isinstance(queries, list)
        # Input Properties
        self.queries = queries

        # Result Properties
        self.results = {}

        # Scrapy Settings
        self.settings = get_project_settings()
        self.settings['SPIDER_MODULES'] = ['Crawler.crawler.spiders']
        self.settings['LOG_ENABLED'] = LOG_ENABLED
        self.settings['LOG_LEVEL'] = LOG_LEVEL
       
        logging.getLogger('scrapy').propagate = LOG_ENABLED
        
    def crawler_results(self, signal, sender, item, response, spider):
        query_id = str2hex(item['query'])
        self.results[query_id] = item

    def get_total(self):
        dispatcher.connect(self.crawler_results, signal=signals.item_passed)

        process = CrawlerProcess(self.settings)
        [process.crawl(PubmedPeekSpider, query) for query in self.queries]
        process.start()

        dispatcher.disconnect(self.crawler_results, signal=signals.item_passed)

class SessionService():
    def __init__(self, query, session_id, LOG_ENABLED=False, LOG_LEVEL="INFO", crawler_process=None):
        assert isinstance(query, str)
        self.query = query
        self.query_id = str2hex(query)
        self.session_id = session_id

        self.settings = get_project_settings()
        self.settings['SPIDER_MODULES'] = ['Crawler.crawler.spiders']
        self.settings['LOG_ENABLED'] = LOG_ENABLED
        self.settings['LOG_LEVEL'] = LOG_LEVEL

        self.result = []

        logging.getLogger('scrapy').propagate = LOG_ENABLED

    def __get_PIPELINES(self):
        return self.settings['ITEM_PIPELINES'] if "ITEM_PIPELINES" in self.settings.keys() else {}

    def enable_JSONPipeline(self, settings=None):
        settings_default = {
            'out': f'./.out/{self.query_id}.json',
            'overwrite': True
        }
        self.settings['SPIDER_MODULES'].append('Crawler.crawler.pipelines')
        PIPELINE = self.__get_PIPELINES()
        PIPELINE['Crawler.crawler.pipelines.JSONPipeline'] = 543
        self.settings['ITEM_PIPELINES'] = PIPELINE
        self.settings['FILE_SETTINGS'] = settings if settings else settings_default
        self.settings['RETRY_TIMES'] = 4
        self.settings['DOWNLOAD_DELAY '] = 0.5
        self.settings['AUTOTHROTTLE_ENABLED'] = True
        self.settings['AUTOTHROTTLE_MAX_DELAY'] = 2.0
        self.settings['AUTOTHROTTLE_START_DELAY'] = 0.5
        self.settings['AUTOTHROTTLE_TARGET_CONCURRENCY'] = 3.0

    def crawler_results(self, signal, sender, item, response, spider):
        self.result.append(dict(item))
    
    def start(self):
        logger.info(f"SessionService [{self.query_id}] START")
        logger.debug(f"Setup crawler for [{self.query}] - [{self.query_id}]")
        logger.debug(self.settings)

        # Query result
        dispatcher.connect(self.crawler_results, signal=signals.item_passed)

        process = CrawlerProcess(settings=self.settings)
        process.crawl(PubmedSpider, query=self.query)
        process.start()

        dispatcher.disconnect(self.crawler_results, signal=signals.item_passed)
        logger.info(f"SessionService [{self.query_id}] READY")

if __name__ == '__main__':
    tic = timeit.default_timer()
    session_id = "SessionService_Test"
    query = "NLP"
    query_id = str2hex(query)

    service = SessionService(
        query=query, session_id=session_id, LOG_ENABLED=False, LOG_LEVEL="DEBUG")
    
    # Write results to JSON file
    settings_JSON = {
        'out': f'./.out/{session_id}.{query_id}.json',
        'overwrite': True
    }
    service.enable_JSONPipeline(settings=settings_JSON)

    service.start()
    print(f'{len(service.result)} Items found for [{query}]')
    T = timeit.default_timer() - tic

    print(f'Total: {round(T,2)}s p.Item: {round(T/len(service.result),3)}s')
