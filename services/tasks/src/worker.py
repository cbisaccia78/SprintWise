import threading
import requests
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Consumer

from src.settings import config

class TaskWorker:
    """
    TaskWorker is responsible for consuming estimate-complete messages from a Kafka topic 
    and updating tasks with their estimation asynchronously.

    Attributes:
        continue_running (bool): A flag to control the running state of the worker.
        lock (threading.Lock): A lock to synchronize access to shared resources.
        executor (ThreadPoolExecutor): A thread pool executor to handle asynchronous task updates.

    Methods:
        __init__():
            Initializes the TaskWorker with default values and a thread pool executor.
        
        start():
            Starts the Kafka consumer to listen for messages and process them asynchronously.
        
        update_task(task_id, task_estimate):
            Sends an HTTP PUT request to update the task with the given ID and estimated time.
        
        stop():
            Stops the worker by setting the continue_running flag to False and shutting down the executor.
    """
    def __init__(self):
        self.continue_running = False
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=5)  # Adjust the number of workers as needed

    def start(self):
        consumer = Consumer(config.kafka_consumer_config)
        consumer.subscribe(['estimate-complete'])

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
            task_estimate = event.value().decode('utf-8')

            print(f'Message: {event.value()}')

            # Asynchronously call the update_task route
            self.executor.submit(self.update_task, task_id, task_estimate)

        consumer.close()

    def update_task(self, task_id, task_estimate):
        url = f'http://localhost:5000/tasks/{task_id}'
        data = {
            'estimated_time': task_estimate
        }
        try:
            response = requests.put(url, json=data)
            if response.status_code == 200:
                print(f'Successfully updated task {task_id}')
            else:
                print(f'Failed to update task {task_id}: {response.status_code} {response.text}')
        except requests.RequestException as e:
            print(f'Error updating task {task_id}: {e}')

    def stop(self):
        with self.lock:
            self.continue_running = False
        self.executor.shutdown(wait=True)