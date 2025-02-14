import os

class Config:
    def __init__(self):
        self.testing = False

        self.kafka_consumer_config = {
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
            'group.id': os.getenv('KAFKA_GROUP_ID', 'task-updator-group'),
            'auto.offset.reset': os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')
        }

        self.kafka_producer_config = {
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
            'acks': 'all'
        }

config = Config()