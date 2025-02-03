import unittest
import json

from src.settings import config as cfg
from src.app import create_app
from src.database import db

from src.models import Task, Project

class TestProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg.testing = True
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
    
    def test_create_project(self):
        data = {
            'name': 'Test Project',
            'description': 'Test Description'
        }

        response = self.client.post(
            '/projects',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        project_out = response.get_json()

        self.assertEqual(project_out['name'], data['name'])
        self.assertEqual(project_out['description'], data['description'])

    def test_get_project(self):
        with self.app.app_context():
            project = Project(name='Test Project', description='Test Description')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        response = self.client.get(f'/projects/{project_id}')
        self.assertEqual(response.status_code, 200)
        project_out = response.get_json()

        self.assertEqual(project_out['name'], project.name)
        self.assertEqual(project_out['description'], project.description)

    def test_get_all_projects(self):
        with self.app.app_context():
            project1 = Project(name='Test Project 1', description='Test Description 1')
            project2 = Project(name='Test Project 2', description='Test Description 2')
            db.session.add(project1)
            db.session.add(project2)
            db.session.commit()

            response = self.client.get('/projects')
            self.assertEqual(response.status_code, 200)
            projects_out = response.get_json()

            self.assertEqual(len(projects_out), 2)
            self.assertEqual(projects_out[0]['name'], project1.name)
            self.assertEqual(projects_out[0]['description'], project1.description)
            self.assertEqual(projects_out[1]['name'], project2.name)
            self.assertEqual(projects_out[1]['description'], project2.description)

    def test_update_project(self):
        with self.app.app_context():
            project = Project(name='Test Project', description='Test Description')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        data = {
            'name': 'Updated Project',
            'description': 'Updated Description'
        }

        response = self.client.put(
            f'/projects/{project_id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        project_out = response.get_json()

        self.assertEqual(project_out['name'], data['name'])
        self.assertEqual(project_out['description'], data['description'])

    def test_delete_project(self):
        with self.app.app_context():
            project = Project(name='Test Project', description='Test Description')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

            task1 = Task(title='Test Task 1', description='Test Description 1', project_id=project_id)
            task2 = Task(title='Test Task 2', description='Test Description 2', project_id=project_id)
            db.session.add_all([task1, task2])
            db.session.commit()

            response = self.client.delete(f'/projects/{project_id}')
            self.assertEqual(response.status_code, 200)

            response = self.client.get(f'/projects/{project_id}')
            self.assertEqual(response.status_code, 404)

            response = self.client.get(f'/tasks/{task1.id}')
            self.assertEqual(response.status_code, 404)

            response = self.client.get(f'/tasks/{task2.id}')
            self.assertEqual(response.status_code, 404)

