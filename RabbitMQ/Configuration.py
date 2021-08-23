import os

EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE_NAME")
ROUTING = {
    'query-pubmed': {
        'QUEUE_NAME':  os.getenv("RABBITMQ_CRAWLER_PUBMED_QUEUE_INPUT")
    },
    'query-pubmed-status': {
        'QUEUE_NAME':  os.getenv("RABBITMQ_CRAWLER_STATUS_QUEUE_INPUT")
    },
    'query-status': {
        'QUEUE_NAME':  os.getenv("RABBITMQ_CRAWLER_STATUS_QUEUE_INPUT")
    }
}
