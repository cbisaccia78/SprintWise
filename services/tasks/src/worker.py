import threading
import requests
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Consumer

from src.settings import config

class TaskWorker:
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