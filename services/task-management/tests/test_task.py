import unittest
import json

from datetime import date, timedelta

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