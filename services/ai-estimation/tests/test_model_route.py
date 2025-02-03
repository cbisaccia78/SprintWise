import unittest
import json

from src.app import create_app
from src.settings import config as cfg

class TestModelRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg.testing = True
        cls.app = create_app()
        cls.client = cls.app.test_client()
    
    def test_estimate_task(self):
        # test with just title
        test_data = {
            'task_id': 1, 
            'title': 'test_title',
        }
        response = self.client.post('/models/task', data=json.dumps(test_data), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        response = response.get_json()
        self.assertEqual(response['task_id'], 1)
        self.assertEqual(response['title'], 'test_title')
        self.assertIn('estimated_time', response)
        self.assertIn('confidence', response)

        # test with just title and description
        test_data["description"] = "test_description"
        response = self.client.post('/models/task', data=json.dumps(test_data), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        response = response.get_json()
        self.assertEqual(response['task_id'], 1)
        self.assertEqual(response['title'], 'test_title')
        self.assertEqual(response['description'], 'test_description')
        self.assertIn('estimated_time', response)
        self.assertIn('confidence', response)

        # test with title, description, and code_snippet
        test_data["code_snippet"] = "def test():\n    return 1"
        response = self.client.post('/models/task', data=json.dumps(test_data), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        response = response.get_json()
        self.assertEqual(response['task_id'], 1)
        self.assertEqual(response['title'], 'test_title')
        self.assertEqual(response['description'], 'test_description')
        self.assertEqual(response['code_snippet'], 'def test():\n    return 1')
        self.assertIn('estimated_time', response)
        self.assertIn('confidence', response)