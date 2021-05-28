import timeit
import binascii
import logging
import pickle
from crawler.spiders.pubmed import PubmedSpider
from scrapy.signalmanager import dispatcher
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import scrapy
import argparse
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


# Callbacks


def empty_fn(x, y):
    pass


def str2hex(text):
    return binascii.hexlify(text.encode()).decode('utf-8')


if __name__ == '__main__':
    try:
        # Setup Argument Parser
        parser = argparse.ArgumentParser(description='Argument Parser')
        parser.add_argument('query', type=str, help='query to search for')
        parser.add_argument('--out', type=str,
                            help='folder output', default="./.out")
        parser.add_argument('-l', '--log', type=str,
                            help='Target path for logging.', default=None)
        parser.add_argument('--model', type=str,
                            help='Target path for Transformers model default: "./.model"', default="./.model")
        parser.add_argument(
            '-c', '--cached', help='Use cached results if available - Output File already existing and not older than 5 days. Default=False', action='store_true')
        parser.add_argument(
            '-p', '--production', help="Enable production mode. Default=False", action='store_true')
        args = parser.parse_args()

        PRODUCTION = args.production
        USE_CACHED = args.cached
        LOG_ENABLED = not PRODUCTION
        LOG_LEVEL = logging.INFO if PRODUCTION else logging.DEBUG
        ###################
        # Setup Logging
        ###################
        query = args.query
        query_id = str2hex(query)
        LOGFILE = args.log if args.log else f'./.log/{query_id}.crawler.log'

        if not os.path.exists(os.path.abspath(os.path.dirname(LOGFILE))):
            os.makedirs(os.path.abspath(os.path.dirname(LOGFILE)))

        if os.path.isfile(LOGFILE):
            os.remove(LOGFILE)

        logging.basicConfig(filename=LOGFILE, level=LOG_LEVEL,
                            format='%(asctime)s %(levelname)-8s %(message)s')
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.info(f"Crawler Start!")
        logging.info(f"Arguments: [{args}]")
        logging.info(f"Query: [{query}]")
        logging.info(f"Query ID: [{query_id}]")
        tic = timeit.default_timer()

        ###################
        # Init Crawler Settings
        ###################
        settings = get_project_settings()
        settings['SPIDER_MODULES'] = ['crawler.spiders']
        settings['LOG_ENABLED'] = LOG_ENABLED
        settings['LOG_LEVEL'] = LOG_LEVEL
        settings['RETRY_TIMES'] = 5
        settings['AUTOTHROTTLE_ENABLED'] = True
        settings['AUTOTHROTTLE_MAX_DELAY'] = 1.0
        settings['AUTOTHROTTLE_START_DELAY'] = 0.1
        settings['AUTOTHROTTLE_TARGET_CONCURRENCY'] = 3.0

        # Disable/Enable scrapy logging if LOG_ENABLED
        logging.getLogger('scrapy').propagate = LOG_ENABLED
        ###################
        # Start Crawler
        ###################
        result = []
        logging.info("Start Crawling ...")

        def on_item_passed(signal, sender, item, response):
            result.append(dict(item))

        dispatcher.connect(on_item_passed, signal=signals.item_passed)
        process = CrawlerProcess(settings=settings)
        process.crawl(PubmedSpider, query=query)
        process.start()
        dispatcher.disconnect(on_item_passed, signal=signals.item_passed)
        T = timeit.default_timer() - tic

        logging.info(f'{len(result)} Items found for [{query}]')
        logging.info(f'Total: {round(T,2)}s p.Item: {round(T/len(result),3)}s')
        logging.info("... Finish Crawling!")
        ###################
        # Write Results
        ###################
        FOLDEROUT = args.out
        if not os.path.exists(os.path.abspath(os.path.dirname(FOLDEROUT))):
            os.makedirs(os.path.abspath(os.path.dirname(FOLDEROUT)))

        # Query Results
        QUERYOUT = f"{FOLDEROUT}/{query_id}.query.dat"
        logging.info(f"Store Query Data [{QUERYOUT}] ...")
        _ids = list(set([x['_id'] for x in result]))
        query_data = {
            '_id': query_id,
            'query': query,
            'articles': _ids
        }
        pickle.dump(query_data, open(QUERYOUT, 'wb'))
        logging.info("... Store Query Data Sucess!")

        # Article Results
        ARTICLEOUT = f"{FOLDEROUT}/{query_id}.article.dat"
        logging.info(f"Store Article Data [{ARTICLEOUT}] ...")
        article_data = {
            '_id': query_id,
            'query': query,
            'articles': result
        }
        pickle.dump(article_data, open(ARTICLEOUT, 'wb'))
        logging.info("... Store Article Data Sucess!")
        logging.info("Crawler Success!")
    except Exception as e:
        ###################
        # Error Management
        ###################
        logging.error("Crawler Error!")
        logging.error(e)
