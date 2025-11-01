import unittest
import os
import pandas as pd
from unittest.mock import patch
from src.service.class_assignment_service import ClassAssignmentService
from src.service.validators.input_validator import InputValidationError


class TestAssignmentServiceIntegration(unittest.TestCase):

    def setUp(self):
        self.sample_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE', 'FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie', 'Frank', 'Eve'],
            'friend2': ['Charlie', 'David', 'Alice', 'Bob', '', ''],
            'friend3': ['', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', ''],
            'notWith': ['', '', 'Eve', '', 'Charlie', ''],
            'clusterId': [1, 1, 2, 2, 3, 3]
        })

    def test_complete_assignment_workflow_greedy(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(2)

        self.assertEqual(len(classes), 2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 6)

        info = service.get_last_assignment_info()
        self.assertIsNotNone(info)
        self.assertEqual(info['strategy_used'], 'greedy')
        self.assertIn('execution_time', info)
        self.assertIn('solution_quality', info)

    def test_complete_assignment_workflow_cp_sat(self):
        service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)
        classes = service.assign_classes(2)

        self.assertEqual(len(classes), 2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 6)

        info = service.get_last_assignment_info()
        self.assertIsNotNone(info)
        self.assertIn(info['strategy_used'], ['cp_sat', 'greedy'])
        self.assertIn('execution_time', info)
        self.assertIn('solution_quality', info)

    def test_strategy_switching(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')

        self.assertEqual(service.strategy_name, 'greedy')

        service.switch_strategy('greedy', timeout_seconds=15)
        self.assertEqual(service.strategy_name, 'greedy')

    def test_environment_variable_configuration(self):
        with patch.dict(os.environ, {'ASSIGNMENT_ALGORITHM': 'greedy', 'ASSIGNMENT_TIMEOUT': '20'}):
            service = ClassAssignmentService(self.sample_df)

            self.assertEqual(service.strategy_name, 'greedy')
            self.assertEqual(service.timeout_seconds, 20)

    def test_metadata_tracking(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        info = service.get_last_assignment_info()

        self.assertIn('metadata', info)
        self.assertIn('evaluation', info['metadata'])

        evaluation = info['metadata']['evaluation']
        self.assertIn('overall_score', evaluation)
        self.assertIn('students_without_friends', evaluation)
        self.assertIn('not_with_violations', evaluation)

    def test_get_last_assignment_info(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')

        self.assertIsNone(service.get_last_assignment_info())

        service.assign_classes(2)

        info = service.get_last_assignment_info()
        self.assertIsNotNone(info)
        self.assertIsInstance(info['execution_time'], float)
        self.assertGreater(info['execution_time'], 0)

    def test_get_class_details(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(2)

        details = service.get_class_details(classes)

        self.assertEqual(len(details), 2)

        for detail in details:
            self.assertIn('class', detail)
            self.assertIn('size', detail)
            self.assertIn('male_ratio', detail)
            self.assertIn('academic_score', detail)
            self.assertIn('behavioral_score', detail)
            self.assertIn('clusters', detail)
            self.assertIn('students', detail)

            self.assertGreater(detail['size'], 0)
            self.assertGreaterEqual(detail['male_ratio'], 0)
            self.assertLessEqual(detail['male_ratio'], 1)

    def test_multiple_consecutive_assignments(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')

        classes1 = service.assign_classes(2)
        info1 = service.get_last_assignment_info()

        classes2 = service.assign_classes(3)
        info2 = service.get_last_assignment_info()

        self.assertEqual(len(classes1), 2)
        self.assertEqual(len(classes2), 3)

        self.assertNotEqual(info1['execution_time'], info2['execution_time'])

    def test_validation_before_service_creation(self):
        empty_df = pd.DataFrame()

        with self.assertRaises(InputValidationError):
            ClassAssignmentService(empty_df)

    def test_validation_before_assignment(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')

        with self.assertRaises(InputValidationError):
            service.assign_classes(10)

    def test_get_available_strategies(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        strategies = service.get_available_strategies()

        self.assertIsInstance(strategies, list)
        self.assertIn('greedy', strategies)
        self.assertIn('cp_sat', strategies)

    def test_evaluation_metrics_included(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(2)

        info = service.get_last_assignment_info()
        evaluation = info['metadata']['evaluation']

        self.assertIn('friendship_satisfaction_rate', evaluation)
        self.assertIn('size_balance', evaluation)
        self.assertIn('gender_balance', evaluation)
        self.assertIn('academic_balance', evaluation)
        self.assertIn('behavioral_balance', evaluation)

    def test_service_handles_timeout_parameter(self):
        service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=5)

        self.assertEqual(service.timeout_seconds, 5)

        classes = service.assign_classes(2)
        self.assertEqual(len(classes), 2)


if __name__ == '__main__':
    unittest.main()
