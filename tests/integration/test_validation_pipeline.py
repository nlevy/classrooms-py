import unittest
import pandas as pd
from src.service.class_assignment_service import ClassAssignmentService
from src.service.validators.input_validator import InputValidationError
from src.server.error_codes import ErrorCode


class TestValidationPipeline(unittest.TestCase):

    def test_validation_before_service_creation(self):
        empty_df = pd.DataFrame()

        with self.assertRaises(InputValidationError) as context:
            ClassAssignmentService(empty_df, strategy='greedy')

        self.assertEqual(context.exception.code, ErrorCode.EMPTY_STUDENT_DATA)

    def test_validation_missing_required_columns(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE']
        })

        with self.assertRaises(InputValidationError) as context:
            ClassAssignmentService(df, strategy='greedy')

        self.assertEqual(context.exception.code, ErrorCode.MISSING_REQUIRED_FIELDS)

    def test_validation_duplicate_names(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Alice'],
            'gender': ['FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM'],
            'behavioralPerformance': ['HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Bob'],
            'friend2': ['', ''],
            'friend3': ['', ''],
            'friend4': ['', '']
        })

        with self.assertRaises(InputValidationError) as context:
            ClassAssignmentService(df, strategy='greedy')

        self.assertEqual(context.exception.code, ErrorCode.DUPLICATE_STUDENT_NAMES)

    def test_validation_before_assignment(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM'],
            'behavioralPerformance': ['HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Alice'],
            'friend2': ['', ''],
            'friend3': ['', ''],
            'friend4': ['', ''],
            'notWith': ['', ''],
            'clusterId': [1, 1]
        })

        service = ClassAssignmentService(df, strategy='greedy')

        with self.assertRaises(InputValidationError) as context:
            service.assign_classes(10)

        self.assertEqual(context.exception.code, ErrorCode.TOO_MANY_CLASSES)

    def test_validation_after_assignment(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie'],
            'friend2': ['', '', '', ''],
            'friend3': ['', '', '', ''],
            'friend4': ['', '', '', ''],
            'notWith': ['', '', '', ''],
            'clusterId': [1, 1, 2, 2]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        info = service.get_last_assignment_info()
        evaluation = info['metadata']['evaluation']

        self.assertIn('students_without_friends', evaluation)
        self.assertIn('not_with_violations', evaluation)
        self.assertIn('overall_score', evaluation)

    def test_error_propagation(self):
        df = pd.DataFrame({
            'name': ['Alice'],
            'gender': ['FEMALE'],
            'academicPerformance': ['HIGH'],
            'behavioralPerformance': ['MEDIUM'],
            'friend1': [''],
            'friend2': [''],
            'friend3': [''],
            'friend4': ['']
        })

        with self.assertRaises(InputValidationError) as context:
            ClassAssignmentService(df, strategy='greedy')

        self.assertEqual(context.exception.code, ErrorCode.STUDENT_NO_FRIENDS)

    def test_validation_error_messages(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM'],
            'behavioralPerformance': ['HIGH', 'MEDIUM'],
            'friend1': ['Charlie', 'Alice'],
            'friend2': ['', ''],
            'friend3': ['', ''],
            'friend4': ['', '']
        })

        with self.assertRaises(InputValidationError) as context:
            ClassAssignmentService(df, strategy='greedy')

        self.assertEqual(context.exception.code, ErrorCode.UNKNOWN_FRIEND)
        self.assertIn('studentName', context.exception.params)
        self.assertIn('friendName', context.exception.params)
        self.assertEqual(context.exception.params['studentName'], 'Alice')
        self.assertEqual(context.exception.params['friendName'], 'Charlie')

    def test_validation_at_multiple_stages(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'gender': ['FEMALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Alice', 'Alice'],
            'friend2': ['', '', ''],
            'friend3': ['', '', ''],
            'friend4': ['', '', ''],
            'notWith': ['', '', ''],
            'clusterId': [1, 1, 2]
        })

        service = ClassAssignmentService(df, strategy='greedy')

        with self.assertRaises(InputValidationError):
            service.assign_classes(0)

        with self.assertRaises(InputValidationError):
            service.assign_classes(5)

        classes = service.assign_classes(2)
        self.assertEqual(len(classes), 2)

    def test_validation_success_path(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie'],
            'friend2': ['Charlie', 'David', 'Alice', 'Bob'],
            'friend3': ['', '', '', ''],
            'friend4': ['', '', '', ''],
            'notWith': ['', '', '', ''],
            'clusterId': [1, 1, 2, 2]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        self.assertEqual(len(classes), 2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 4)

    def test_validation_error_response_structure(self):
        empty_df = pd.DataFrame()

        try:
            ClassAssignmentService(empty_df, strategy='greedy')
            self.fail("Should have raised InputValidationError")
        except InputValidationError as e:
            error_response = e.to_response()
            error_dict = error_response.to_dict()

            self.assertIn('error', error_dict)
            self.assertIn('code', error_dict['error'])
            self.assertIn('params', error_dict['error'])
            self.assertIn('message', error_dict['error'])

    def test_validation_catches_isolated_students(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM'],
            'behavioralPerformance': ['HIGH', 'MEDIUM'],
            'friend1': ['Bob', ''],
            'friend2': ['', ''],
            'friend3': ['', ''],
            'friend4': ['', '']
        })

        with self.assertRaises(InputValidationError) as context:
            ClassAssignmentService(df, strategy='greedy')

        self.assertEqual(context.exception.code, ErrorCode.STUDENT_NO_FRIENDS)


if __name__ == '__main__':
    unittest.main()
