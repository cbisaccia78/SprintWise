import unittest
import json

from src.app import create_app
from src.database import db

from src.models import Task, Project

class TestTask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_create_task(self):
        with self.app.app_context():
            project = Project(name='Test Project', description='Test Description')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'project_id': project_id
        }

        response = self.client.post(
            '/tasks',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        task_out = response.get_json()

        self.assertEqual(task_out['title'], data['title'])
        self.assertEqual(task_out['description'], data['description'])
        self.assertEqual(task_out['project_id'], data['project_id'])

    def test_get_task(self):
        with self.app.app_context():
            project = Project(name='Test Project', description='Test Description')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

            task = Task(title='Test Task', description='Test Description', project_id=project_id)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = self.client.get(f'/tasks/{task_id}')
        self.assertEqual(response.status_code, 200)
        task_out = response.get_json()

        self.assertEqual(task_out['title'], task.title)
        self.assertEqual(task_out['description'], task.description)
        self.assertEqual(task_out['project_id'], task.project_id)

    def test_get_all_tasks(self):
        with self.app.app_context():
            project = Project(name='Test Project', description='Test Description')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

            task1 = Task(title='Test Task 1', description='Test Description 1', project_id=project_id)
            task2 = Task(title='Test Task 2', description='Test Description 2', project_id=project_id)
            db.session.add_all([task1, task2])
            db.session.commit()

        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)
        tasks_out = response.get_json()

        self.assertEqual(len(tasks_out), 2)

    def test_update_task(self):
        with self.app.app_context():
            project = Project(name='Test Project', description='Test Description')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

            task = Task(title='Test Task', description='Test Description', project_id=project_id)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'project_id': project_id
        }

        response = self.client.put(
            f'/tasks/{task_id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        task_out = response.get_json()

        self.assertEqual(task_out['title'], data['title'])
        self.assertEqual(task_out['description'], data['description'])
        self.assertEqual(task_out['project_id'], data['project_id'])

    def test_delete_task(self):
        with self.app.app_context():
            project = Project(name='Test Project', description='Test Description')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

            task = Task(title='Test Task', description='Test Description', project_id=project_id)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = self.client.delete(f'/tasks/{task_id}')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/tasks/{task_id}')
        self.assertEqual(response.status_code, 404)