import threading
import requests
import json
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Consumer

from src.settings import config

class TaskCreatedConsumer:
    """
    TaskCreatedConsumer is responsible for consuming task-created events from a Kafka topic 
    and asynchronously estimating them by calling an api in the model service
    .
    Attributes:
        continue_running (bool): A flag to control the running state of the worker.
        lock (threading.Lock): A lock to synchronize access to shared resources.
        executor (ThreadPoolExecutor): A thread pool executor to handle asynchronous task estimation.
    Methods:
        __init__():
            Initializes the TaskCreatedConsumer with default settings.
        start():
            Starts the worker to consume tasks from the 'task-created' Kafka topic and
            submit them for estimation.
        estimate_task(task_id, task):
            Sends a POST request to an external service to estimate the given task.
        stop():
            Stops the worker and shuts down the thread pool executor.
    """
    ESTIMATE_URL = f'http://localhost:5001/models/task'

    def __init__(self):
        self.continue_running = False
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=5)  # Adjust the number of workers as needed

    def start(self):
        consumer = Consumer(config.kafka_consumer_config)
        consumer.subscribe(['task-created'])

        with self.lock:
            self.continue_running = True

        while True:
            with self.lock:
                if not self.continue_running:
                    break

            event = consumer.poll(1.0)

            if event is None:
                continue
            if event.error():
                print(f'Consumer error: {event.error()}')
                continue

            task_id = event.key().decode('utf-8')
            task = event.value().decode('utf-8')

            print(f'Message: {event.value()}')

            # Asynchronously call the update_task route
            self.executor.submit(self.estimate_task, task_id, task)

        consumer.close()
    
    def estimate_task(self, task_id, task):

        task = json.loads(task)
        data = {
            'task_id': task_id,
            'title': task['title'],
            'description': task['description'],
            'code_snippet': '' # empty for now, need to generate code snippet
        }
        try:
            response = requests.post(self.ESTIMATE_URL, json=data)

            if response.status_code == 201:
                print(f'Successfully estimated {task_id}')
            else:
                print(f'Failed to estimate task {task_id}: {response.status_code} {response.text}')
        except requests.RequestException as e:
            print(f'Error updating task {task_id}: {e}')
    
    def stop(self):
        with self.lock:
            self.continue_running = False
        self.executor.shutdown(wait=True)

    

    

    