import os

class Config:
    def __init__(self):
        self.testing = False

        self.SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        self.kafka_consumer_config = {
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'group.id': os.getenv('KAFKA_GROUP_ID', 'ai-estimation-group'),
            'auto.offset.reset': os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')
        }

        self.kafka_producer_config = {
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'acks': 'all'
        }

config = Config()