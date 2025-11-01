import unittest
import json
from src.server.app import app


class TestClassroomsEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.testing = True

        self.valid_students = [
            {
                "name": "Alice",
                "school": "Test School",
                "gender": "FEMALE",
                "academicPerformance": "HIGH",
                "behavioralPerformance": "MEDIUM",
                "comments": "",
                "friend1": "Bob",
                "friend2": "Charlie",
                "friend3": "",
                "friend4": "",
                "notWith": "",
                "clusterId": 1
            },
            {
                "name": "Bob",
                "school": "Test School",
                "gender": "MALE",
                "academicPerformance": "MEDIUM",
                "behavioralPerformance": "HIGH",
                "comments": "",
                "friend1": "Alice",
                "friend2": "David",
                "friend3": "",
                "friend4": "",
                "notWith": "",
                "clusterId": 1
            },
            {
                "name": "Charlie",
                "school": "Test School",
                "gender": "MALE",
                "academicPerformance": "LOW",
                "behavioralPerformance": "MEDIUM",
                "comments": "",
                "friend1": "Alice",
                "friend2": "David",
                "friend3": "",
                "friend4": "",
                "notWith": "Eve",
                "clusterId": 2
            },
            {
                "name": "David",
                "school": "Test School",
                "gender": "MALE",
                "academicPerformance": "HIGH",
                "behavioralPerformance": "LOW",
                "comments": "",
                "friend1": "Bob",
                "friend2": "Charlie",
                "friend3": "",
                "friend4": "",
                "notWith": "",
                "clusterId": 2
            },
            {
                "name": "Eve",
                "school": "Test School",
                "gender": "FEMALE",
                "academicPerformance": "MEDIUM",
                "behavioralPerformance": "HIGH",
                "comments": "",
                "friend1": "Frank",
                "friend2": "",
                "friend3": "",
                "friend4": "",
                "notWith": "Charlie",
                "clusterId": 3
            },
            {
                "name": "Frank",
                "school": "Test School",
                "gender": "MALE",
                "academicPerformance": "LOW",
                "behavioralPerformance": "MEDIUM",
                "comments": "",
                "friend1": "Eve",
                "friend2": "",
                "friend3": "",
                "friend4": "",
                "notWith": "",
                "clusterId": 3
            }
        ]

    def test_successful_assignment(self):
        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps(self.valid_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('classes', data)
        self.assertEqual(len(data['classes']), 2)

    def test_response_structure(self):
        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps(self.valid_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('classes', data)
        self.assertIn('summaries', data)
        self.assertIsInstance(data['classes'], dict)
        self.assertIsInstance(data['summaries'], list)

    def test_missing_content_type(self):
        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps(self.valid_students)
        )

        self.assertEqual(response.status_code, 415)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'INVALID_CONTENT_TYPE')

    def test_missing_classes_number_param(self):
        response = self.client.post(
            '/classrooms',
            data=json.dumps(self.valid_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'MISSING_PARAMETER')
        self.assertEqual(data['error']['params']['parameter'], 'classesNumber')

    def test_invalid_classes_number(self):
        response = self.client.post(
            '/classrooms?classesNumber=-5',
            data=json.dumps(self.valid_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'INVALID_CLASS_COUNT')

    def test_empty_student_list(self):
        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps([]),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'EMPTY_STUDENT_DATA')

    def test_invalid_student_data_format(self):
        invalid_students = [
            {
                "name": "Alice",
                "gender": "INVALID_GENDER"
            }
        ]

        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps(invalid_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'INVALID_STUDENT_DATA')

    def test_duplicate_student_names(self):
        duplicate_students = [
            {
                "name": "Alice",
                "school": "Test School",
                "gender": "FEMALE",
                "academicPerformance": "HIGH",
                "behavioralPerformance": "MEDIUM",
                "comments": "",
                "friend1": "Bob",
                "friend2": "",
                "friend3": "",
                "friend4": ""
            },
            {
                "name": "Alice",
                "school": "Test School",
                "gender": "MALE",
                "academicPerformance": "MEDIUM",
                "behavioralPerformance": "HIGH",
                "comments": "",
                "friend1": "Alice",
                "friend2": "",
                "friend3": "",
                "friend4": ""
            }
        ]

        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps(duplicate_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'DUPLICATE_STUDENT_NAMES')

    def test_student_no_friends(self):
        students_no_friends = [
            {
                "name": "Alice",
                "school": "Test School",
                "gender": "FEMALE",
                "academicPerformance": "HIGH",
                "behavioralPerformance": "MEDIUM",
                "comments": "",
                "friend1": "",
                "friend2": "",
                "friend3": "",
                "friend4": ""
            },
            {
                "name": "Bob",
                "school": "Test School",
                "gender": "MALE",
                "academicPerformance": "MEDIUM",
                "behavioralPerformance": "HIGH",
                "comments": "",
                "friend1": "Alice",
                "friend2": "",
                "friend3": "",
                "friend4": ""
            }
        ]

        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps(students_no_friends),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'STUDENT_NO_FRIENDS')

    def test_unknown_friend(self):
        students_unknown_friend = [
            {
                "name": "Alice",
                "school": "Test School",
                "gender": "FEMALE",
                "academicPerformance": "HIGH",
                "behavioralPerformance": "MEDIUM",
                "comments": "",
                "friend1": "Unknown",
                "friend2": "",
                "friend3": "",
                "friend4": ""
            },
            {
                "name": "Bob",
                "school": "Test School",
                "gender": "MALE",
                "academicPerformance": "MEDIUM",
                "behavioralPerformance": "HIGH",
                "comments": "",
                "friend1": "Alice",
                "friend2": "",
                "friend3": "",
                "friend4": ""
            }
        ]

        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps(students_unknown_friend),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'UNKNOWN_FRIEND')

    def test_too_many_classes(self):
        response = self.client.post(
            '/classrooms?classesNumber=10',
            data=json.dumps(self.valid_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'TOO_MANY_CLASSES')

    def test_single_student_single_class(self):
        single_student = [
            {
                "name": "Alice",
                "school": "Test School",
                "gender": "FEMALE",
                "academicPerformance": "HIGH",
                "behavioralPerformance": "MEDIUM",
                "comments": "",
                "friend1": "Alice",
                "friend2": "",
                "friend3": "",
                "friend4": ""
            }
        ]

        response = self.client.post(
            '/classrooms?classesNumber=1',
            data=json.dumps(single_student),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('classes', data)

    def test_assignment_with_clusters(self):
        response = self.client.post(
            '/classrooms?classesNumber=3',
            data=json.dumps(self.valid_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('classes', data)
        self.assertEqual(len(data['classes']), 3)

    def test_assignment_with_not_with(self):
        response = self.client.post(
            '/classrooms?classesNumber=2',
            data=json.dumps(self.valid_students),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('classes', data)


if __name__ == '__main__':
    unittest.main()
