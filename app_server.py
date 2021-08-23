from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
from werkzeug.exceptions import BadRequest, ServiceUnavailable
import logging
import argparse
import uuid

app = Flask(__name__)
CORS(app)

class IncorrectInputException(Exception):
    pass


from RabbitMQ.RabbitMQConnection import RabbitMQConnection
import os
import json

exchange = os.getenv('RABBITMQ_EXCHANGE_NAME')

def sendMessage(message, routing_key, exchange=exchange):
    channel = RabbitMQConnection().channel()
    channel.exchange_declare(exchange=exchange, exchange_type='direct')
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(message)
    )
    channel.close()

class QueryServer():
    @staticmethod
    def validateInput(input):
        try:
            assert input.get('query', False) != False, '"query" missing!'
        except Exception as e:
            raise IncorrectInputException('Missing Field! ' + str(e)) from e
        
        try:
            assert isinstance(input['query'], list), '"query": Expected list of strings!'
        except Exception as e:
            raise IncorrectInputException('Invalid Format! ' + str(e)) from e

    @staticmethod
    def update_query(input, _id=None, mode='pubmed-query'):
        _id = _id if _id else uuid.uuid4().hex
        try:
            #Send Query Status: NEW
            sendMessage({
                "id": _id, 
                "state": "NEW",
                "query": json.dumps(input),
                "state_query": json.dumps(["PENDING"] * len(input)),
                "msg": "New session commited to queue.", }, routing_key=mode+'-status')

            #Send Query Request
            for text in input:
                sendMessage({"id": _id, "text": text}, routing_key=mode)
           
        except Exception as e:
            raise ServiceUnavailable(f'RabbitMQ Service not available! Reason: {str(e)}') from e

        return _id

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "msg": "Query Service is online!"
    })

@app.route('/query', methods=['POST'])
def Commit_Query():
    try:
        data = json.loads(request.data)
    except Exception as e:
        raise BadRequest(f"Invalid Input! JSON format required! {e}") from e

    QueryServer.validateInput(data)

    query = data.get('query', None)
    id = data.get('id', None)

    mode = os.getenv('RABBITMQ_CRAWLER_PUBMED_ROUTING_KEY')
    session_id = QueryServer.update_query(query, _id=id, mode=mode)

    return jsonify(session_id)


if __name__ == '__main__':

    LOG = "./.log/query-service.log"

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

    logging.info(f"Starting Server with [{args}]")

    try:
        # Start Server
        app.run(host="0.0.0.0", debug=False, port=5001)

    except Exception as e:
        logging.error(e)
