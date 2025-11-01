import unittest
import pandas as pd
from src.service.validators.input_validator import InputValidator, InputValidationError
from src.server.error_codes import ErrorCode


class TestInputValidator(unittest.TestCase):

    def test_validate_empty_dataframe(self):
        empty_df = pd.DataFrame()

        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_student_data(empty_df)

        self.assertEqual(context.exception.code, ErrorCode.EMPTY_STUDENT_DATA)
        self.assertEqual(context.exception.params['count'], 0)

    def test_validate_missing_required_columns(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE']
        })

        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_student_data(df)

        self.assertEqual(context.exception.code, ErrorCode.MISSING_REQUIRED_FIELDS)
        self.assertIn('academicPerformance', context.exception.params['fields'])
        self.assertIn('behavioralPerformance', context.exception.params['fields'])

    def test_validate_duplicate_student_names(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Alice'],
            'gender': ['FEMALE', 'MALE', 'FEMALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', 'Alice', 'Bob'],
            'friend2': ['', '', ''],
            'friend3': ['', '', ''],
            'friend4': ['', '', '']
        })

        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_student_data(df)

        self.assertEqual(context.exception.code, ErrorCode.DUPLICATE_STUDENT_NAMES)
        self.assertIn('Alice', context.exception.params['duplicates'])

    def test_validate_valid_student_data(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM'],
            'behavioralPerformance': ['HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Alice'],
            'friend2': ['', ''],
            'friend3': ['', ''],
            'friend4': ['', '']
        })

        InputValidator.validate_student_data(df)

    def test_student_with_no_friends(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM'],
            'behavioralPerformance': ['HIGH', 'MEDIUM'],
            'friend1': ['', 'Alice'],
            'friend2': ['', ''],
            'friend3': ['', ''],
            'friend4': ['', '']
        })

        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_student_data(df)

        self.assertEqual(context.exception.code, ErrorCode.STUDENT_NO_FRIENDS)
        self.assertEqual(context.exception.params['studentName'], 'Alice')

    def test_student_with_unknown_friend(self):
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
            InputValidator.validate_student_data(df)

        self.assertEqual(context.exception.code, ErrorCode.UNKNOWN_FRIEND)
        self.assertEqual(context.exception.params['studentName'], 'Alice')
        self.assertEqual(context.exception.params['friendName'], 'Charlie')

    def test_isolated_students(self):
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
            InputValidator.validate_student_data(df)

        self.assertEqual(context.exception.code, ErrorCode.STUDENT_NO_FRIENDS)

    def test_valid_friendship_network(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'gender': ['FEMALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', 'Alice', 'Alice'],
            'friend2': ['Charlie', 'Charlie', 'Bob'],
            'friend3': ['', '', ''],
            'friend4': ['', '', '']
        })

        InputValidator.validate_student_data(df)

    def test_partial_friendships(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'gender': ['FEMALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', '', 'Alice'],
            'friend2': ['', '', ''],
            'friend3': ['', '', ''],
            'friend4': ['', '', '']
        })

        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_student_data(df)

        self.assertEqual(context.exception.code, ErrorCode.STUDENT_NO_FRIENDS)
        self.assertEqual(context.exception.params['studentName'], 'Bob')

    def test_zero_classes(self):
        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_assignment_parameters(10, 0)

        self.assertEqual(context.exception.code, ErrorCode.INVALID_CLASS_COUNT)
        self.assertEqual(context.exception.params['classCount'], 0)

    def test_negative_classes(self):
        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_assignment_parameters(10, -5)

        self.assertEqual(context.exception.code, ErrorCode.INVALID_CLASS_COUNT)
        self.assertEqual(context.exception.params['classCount'], -5)

    def test_more_classes_than_students(self):
        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_assignment_parameters(5, 10)

        self.assertEqual(context.exception.code, ErrorCode.TOO_MANY_CLASSES)
        self.assertEqual(context.exception.params['classCount'], 10)
        self.assertEqual(context.exception.params['studentCount'], 5)

    def test_class_size_too_small(self):
        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_assignment_parameters(2, 10)

        self.assertEqual(context.exception.code, ErrorCode.TOO_MANY_CLASSES)

    def test_valid_assignment_parameters(self):
        InputValidator.validate_assignment_parameters(10, 2)
        InputValidator.validate_assignment_parameters(30, 3)
        InputValidator.validate_assignment_parameters(100, 10)

    def test_single_student_single_class(self):
        InputValidator.validate_assignment_parameters(1, 1)

    def test_exactly_one_friend_per_student(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM'],
            'behavioralPerformance': ['HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Alice'],
            'friend2': ['', ''],
            'friend3': ['', ''],
            'friend4': ['', '']
        })

        InputValidator.validate_student_data(df)

    def test_all_students_mutual_friends(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'behavioralPerformance': ['HIGH', 'MEDIUM', 'LOW', 'MEDIUM'],
            'friend1': ['Bob', 'Alice', 'Alice', 'Alice'],
            'friend2': ['Charlie', 'Charlie', 'Bob', 'Bob'],
            'friend3': ['David', 'David', 'David', 'Charlie'],
            'friend4': ['', '', '', '']
        })

        InputValidator.validate_student_data(df)

    def test_zero_students(self):
        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_assignment_parameters(0, 1)

        self.assertEqual(context.exception.code, ErrorCode.INVALID_STUDENT_COUNT)
        self.assertEqual(context.exception.params['studentCount'], 0)

    def test_negative_students(self):
        with self.assertRaises(InputValidationError) as context:
            InputValidator.validate_assignment_parameters(-5, 1)

        self.assertEqual(context.exception.code, ErrorCode.INVALID_STUDENT_COUNT)
        self.assertEqual(context.exception.params['studentCount'], -5)


if __name__ == '__main__':
    unittest.main()
