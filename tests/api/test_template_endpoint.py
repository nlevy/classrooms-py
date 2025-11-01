import unittest
import json
from src.server.app import app


class TestTemplateEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.testing = True

    def test_get_english_template(self):
        response = self.client.get('/template?lang=en')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_hebrew_template(self):
        response = self.client.get('/template?lang=he')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_default_language(self):
        response = self.client.get('/template')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_unsupported_language(self):
        response = self.client.get('/template?lang=fr')

        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'UNSUPPORTED_LANGUAGE')
        self.assertEqual(data['error']['params']['language'], 'fr')

    def test_template_structure(self):
        response = self.client.get('/template?lang=en')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIsInstance(data, list)

        if len(data) > 0:
            first_item = data[0]
            self.assertIn('name', first_item)
            self.assertIn('school', first_item)
            self.assertIn('gender', first_item)
            self.assertIn('academicPerformance', first_item)
            self.assertIn('behavioralPerformance', first_item)

    def test_template_response_headers(self):
        response = self.client.get('/template?lang=en')

        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response.content_type)

    def test_both_templates_exist(self):
        response_en = self.client.get('/template?lang=en')
        response_he = self.client.get('/template?lang=he')

        self.assertEqual(response_en.status_code, 200)
        self.assertEqual(response_he.status_code, 200)

        data_en = json.loads(response_en.data)
        data_he = json.loads(response_he.data)

        self.assertIsInstance(data_en, list)
        self.assertIsInstance(data_he, list)

    def test_template_contains_sample_data(self):
        response = self.client.get('/template?lang=en')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertGreater(len(data), 0, "Template should contain at least one sample student")

    def test_error_response_structure(self):
        response = self.client.get('/template?lang=invalid')

        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('code', data['error'])
        self.assertIn('params', data['error'])
        self.assertIn('message', data['error'])


if __name__ == '__main__':
    unittest.main()
