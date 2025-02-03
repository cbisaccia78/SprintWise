import sys
import json
from confluent_kafka import Producer

if __name__ == '__main__':
    
    if len(sys.argv) != 4:
        print("Usage: python producer.py <topic> <keys> <values>")
        sys.exit(1)

    topic = sys.argv[1]
    keys = json.loads(sys.argv[2])
    values = json.loads(sys.argv[3])

    if len(keys) != len(values):
        print("Error: The number of keys must match the number of values.")
        sys.exit(1)

    config = {
        'bootstrap.servers': 'localhost:9092',
        'acks': 'all'
    }

    producer = Producer(config)

    def delivery_callback(err, msg):
        if err:
            print('ERROR: {}'.format(err))
        else:
            print("Produced event to topic: {topic}: key={key:12} value = {value:12}".format(topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

    for key, value in zip(keys, values):
        producer.produce(topic, key=key, value=json.dumps(value), callback=delivery_callback)

    # block until the messages are sent.
    producer.poll(10000)
    producer.flush()
