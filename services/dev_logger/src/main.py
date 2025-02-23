import logging
import os

from confluent_kafka import Consumer, KafkaException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KafkaLogger:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
            'group.id': 'logger-group',
            'auto.offset.reset': 'earliest'
        })
        self.topics = ['task-created', 'estimate-complete']

    def start(self):
        self.consumer.subscribe(self.topics)
        logging.info(f'Subscribed to topics: {self.topics}')

        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        logging.info(f'End of partition reached {msg.topic()} [{msg.partition()}]')
                    else:
                        logging.error(f'Error: {msg.error()}')
                    continue

                logging.info(f'Received message: {msg.value().decode("utf-8")} from topic: {msg.topic()}')

        except KeyboardInterrupt:
            logging.info('Aborted by user')

        finally:
            self.consumer.close()
            logging.info('Consumer closed')


logger = KafkaLogger()
logger.start()