import unittest
import pandas as pd
import os
from unittest.mock import patch

from src.service.class_assignment_service import ClassAssignmentService
from src.service.validators.input_validator import InputValidationError


class TestNewAssignmentService(unittest.TestCase):
    """Test the new parallel assignment service implementation"""

    def setUp(self):
        """Create sample test data"""
        self.sample_data = [
            {
                'name': 'Alice',
                'school': 'Test School',
                'gender': 'FEMALE',
                'academicPerformance': 'HIGH',
                'behavioralPerformance': 'MEDIUM',
                'comments': '',
                'friend1': 'Bob',
                'friend2': 'Charlie',
                'friend3': '',
                'friend4': '',
                'notWith': '',
                'clusterId': 1
            },
            {
                'name': 'Bob',
                'school': 'Test School',
                'gender': 'MALE',
                'academicPerformance': 'MEDIUM',
                'behavioralPerformance': 'HIGH',
                'comments': '',
                'friend1': 'Alice',
                'friend2': 'David',
                'friend3': '',
                'friend4': '',
                'notWith': '',
                'clusterId': 1
            },
            {
                'name': 'Charlie',
                'school': 'Test School',
                'gender': 'MALE',
                'academicPerformance': 'LOW',
                'behavioralPerformance': 'MEDIUM',
                'comments': '',
                'friend1': 'Alice',
                'friend2': 'David',
                'friend3': '',
                'friend4': '',
                'notWith': 'Eve',
                'clusterId': 2
            },
            {
                'name': 'David',
                'school': 'Test School',
                'gender': 'MALE',
                'academicPerformance': 'HIGH',
                'behavioralPerformance': 'LOW',
                'comments': '',
                'friend1': 'Bob',
                'friend2': 'Charlie',
                'friend3': '',
                'friend4': '',
                'notWith': '',
                'clusterId': 2
            },
            {
                'name': 'Eve',
                'school': 'Test School',
                'gender': 'FEMALE',
                'academicPerformance': 'MEDIUM',
                'behavioralPerformance': 'HIGH',
                'comments': '',
                'friend1': 'Frank',
                'friend2': '',
                'friend3': '',
                'friend4': '',
                'notWith': 'Charlie',
                'clusterId': 3
            },
            {
                'name': 'Frank',
                'school': 'Test School',
                'gender': 'MALE',
                'academicPerformance': 'LOW',
                'behavioralPerformance': 'MEDIUM',
                'comments': '',
                'friend1': 'Eve',
                'friend2': '',
                'friend3': '',
                'friend4': '',
                'notWith': '',
                'clusterId': 3
            }
        ]
        self.df = pd.DataFrame(self.sample_data)

    def test_service_initialization_with_defaults(self):
        """Test service initializes with default environment settings"""
        with patch.dict(os.environ, {'ASSIGNMENT_ALGORITHM': 'greedy', 'ASSIGNMENT_TIMEOUT': '15'}):
            service = ClassAssignmentService(self.df)
            self.assertEqual(service.strategy_name, 'greedy')
            self.assertEqual(service.timeout_seconds, 15)

    def test_service_initialization_with_parameters(self):
        """Test service initializes with explicit parameters"""
        service = ClassAssignmentService(self.df, strategy='greedy', timeout_seconds=20)
        self.assertEqual(service.strategy_name, 'greedy')
        self.assertEqual(service.timeout_seconds, 20)

    def test_greedy_strategy_assignment(self):
        """Test assignment using greedy strategy"""
        service = ClassAssignmentService(self.df, strategy='greedy')
        classes = service.assign_classes(2)

        # Basic validation
        self.assertEqual(len(classes), 2)
        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 6)  # All students assigned
        self.assertEqual(all_students, set(['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']))

    def test_assignment_info_tracking(self):
        """Test that assignment info is properly tracked"""
        service = ClassAssignmentService(self.df, strategy='greedy')
        classes = service.assign_classes(2)

        info = service.get_last_assignment_info()
        self.assertIsNotNone(info)
        self.assertEqual(info['strategy_used'], 'greedy')
        self.assertIn('execution_time', info)
        self.assertIn('solution_quality', info)

    def test_strategy_switching(self):
        """Test switching between strategies"""
        service = ClassAssignmentService(self.df, strategy='greedy')
        self.assertEqual(service.strategy_name, 'greedy')

        service.switch_strategy('greedy')  # Switch to same strategy
        self.assertEqual(service.strategy_name, 'greedy')

    def test_get_available_strategies(self):
        """Test getting list of available strategies"""
        service = ClassAssignmentService(self.df, strategy='greedy')
        strategies = service.get_available_strategies()
        self.assertIn('greedy', strategies)
        self.assertIn('cp_sat', strategies)

    def test_input_validation_empty_data(self):
        """Test that empty data raises validation error"""
        empty_df = pd.DataFrame()
        with self.assertRaises(InputValidationError):
            ClassAssignmentService(empty_df)

    def test_input_validation_missing_friends(self):
        """Test that students without friends raise validation error"""
        invalid_data = self.sample_data.copy()
        invalid_data[0]['friend1'] = ''
        invalid_data[0]['friend2'] = ''
        invalid_df = pd.DataFrame(invalid_data)

        with self.assertRaises(InputValidationError):
            ClassAssignmentService(invalid_df)

    def test_assignment_parameter_validation(self):
        """Test assignment parameter validation"""
        service = ClassAssignmentService(self.df, strategy='greedy')

        # Too many classes
        with self.assertRaises(InputValidationError):
            service.assign_classes(10)

        # Zero classes
        with self.assertRaises(InputValidationError):
            service.assign_classes(0)

    def test_not_with_constraints(self):
        """Test that not-with constraints are respected"""
        service = ClassAssignmentService(self.df, strategy='greedy')
        classes = service.assign_classes(2)

        # Find Charlie and Eve
        charlie_class = None
        eve_class = None
        for i, class_set in enumerate(classes):
            if 'Charlie' in class_set:
                charlie_class = i
            if 'Eve' in class_set:
                eve_class = i

        # Charlie and Eve should not be in the same class
        self.assertNotEqual(charlie_class, eve_class)

    def test_backward_compatibility_methods(self):
        """Test that backward compatibility methods still work"""
        service = ClassAssignmentService(self.df, strategy='greedy')
        classes = service.assign_classes(2)

        # Test get_class_details method
        details = service.get_class_details(classes)
        self.assertEqual(len(details), 2)
        for detail in details:
            self.assertIn('class', detail)
            self.assertIn('size', detail)
            self.assertIn('male_ratio', detail)
            self.assertIn('students', detail)

    @patch('src.service.strategies.cp_sat_strategy.ORTOOLS_AVAILABLE', False)
    def test_cp_sat_fallback_when_ortools_missing(self):
        """Test fallback to greedy when OR-Tools is not available"""
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            service = ClassAssignmentService(self.df, strategy='cp_sat')
            # Should fallback to greedy strategy during creation
            self.assertEqual(service.strategy.name, 'greedy')

    def test_cp_sat_fallback_on_solver_failure(self):
        """Test fallback to greedy when CP-SAT solver fails"""
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            service = ClassAssignmentService(self.df, strategy='cp_sat')
            # CP-SAT strategy is created successfully, but should fallback during assignment
            self.assertEqual(service.strategy.name, 'cp_sat')

            # Assignment should fallback to greedy due to model issues
            classes = service.assign_classes(2)
            info = service.get_last_assignment_info()

            # Should have used greedy via fallback
            self.assertEqual(info['strategy_used'], 'greedy')
            self.assertTrue(info['metadata'].get('fallback_used', False))
            self.assertEqual(info['metadata'].get('original_strategy'), 'cp_sat')

    def test_cp_sat_no_fallback_when_disabled(self):
        """Test that CP-SAT failures raise exceptions when fallback disabled"""
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'false'}):
            service = ClassAssignmentService(self.df, strategy='cp_sat')
            # Should raise exception instead of falling back
            with self.assertRaises(RuntimeError):
                service.assign_classes(2)


if __name__ == '__main__':
    unittest.main()