from RabbitMQ.Listener import Listener
import RabbitMQ.Configuration as Configuration
import logging
import os
import sys
import argparse
import json

fire_connector = None


def query_request_callback(ch, method, properties, body):

    logging.info(" [x] Pubmed - Query Received %r" % body.decode())
    try:
        request = json.loads(body)
        _id = request.get('id', None)
        text = request.get('text', None)

        assert _id != None, "Invalid Session Status Body! Missing field 'id'"
        assert text != None, "Invalid Session Status Body! Missing field 'text'"

        logging.info(f"Execute Query: [{request}]")

        logging.info(" [x] Done")
    except Exception as e:
        logging.error(f"Pubmed - Query Request Callback Failed! " + str(e))


if __name__ == '__main__':

    LOG = "./.log/pubmed-query-worker.log"
    try:
        # Setup Argument Parser
        parser = argparse.ArgumentParser(description='Argument Parser')
        parser.add_argument('--l', '--log', dest='LOGFILE', type=str, default=LOG,
                            help=f'path for logfile (default: {LOG})')
        parser.add_argument("--production", action='store_const',
                            help="set to production mode", const=True, default=False)

        args = parser.parse_args()
        # Check if production is set
        PRODUCTION = args.production
        os.environ['PRODUCTION'] = str(PRODUCTION)

        if not os.path.exists(os.path.abspath(os.path.dirname(args.LOGFILE))):
            os.makedirs(os.path.abspath(os.path.dirname(args.LOGFILE)))

        # Setup Logging
        logging.basicConfig(filename=args.LOGFILE, level=logging.INFO if PRODUCTION else logging.DEBUG,
                            format='%(asctime)s %(levelname)-8s %(message)s')
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        logging.info(f"Starting Query Service with [{args}]")

        routing_key = os.getenv('RABBITMQ_CRAWLER_PUBMED_ROUTING_KEY')
        queue = Configuration.ROUTING[routing_key]['QUEUE_NAME']
        
        listener_sklearn = Listener(routing_key=routing_key)
        listener_sklearn.attachCallbackToQueue(queue, query_request_callback)
        listener_sklearn.run()

    except Exception as e:
        logging.error(e)
