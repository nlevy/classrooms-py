import unittest
from src.server.error_codes import ErrorCode, ErrorResponse
from src.service.validators.input_validator import InputValidationError


class TestErrorCode(unittest.TestCase):

    def test_all_error_codes_unique(self):
        codes = [code.value for code in ErrorCode]
        unique_codes = set(codes)

        self.assertEqual(len(codes), len(unique_codes), "Error codes must be unique")

    def test_error_code_values_are_strings(self):
        for code in ErrorCode:
            self.assertIsInstance(code.value, str)

    def test_error_code_coverage(self):
        expected_codes = [
            'INVALID_CONTENT_TYPE',
            'MISSING_PARAMETER',
            'INVALID_STUDENT_DATA',
            'EMPTY_STUDENT_DATA',
            'MISSING_REQUIRED_FIELDS',
            'DUPLICATE_STUDENT_NAMES',
            'STUDENT_NO_FRIENDS',
            'UNKNOWN_FRIEND',
            'ISOLATED_STUDENTS',
            'INVALID_CLASS_COUNT',
            'INVALID_STUDENT_COUNT',
            'TOO_MANY_CLASSES',
            'CLASS_SIZE_TOO_SMALL',
            'ASSIGNMENT_FAILED',
            'NO_SOLUTION_FOUND',
            'OPTIMIZATION_TIMEOUT',
            'UNSUPPORTED_LANGUAGE',
            'TEMPLATE_NOT_AVAILABLE',
            'INTERNAL_SERVER_ERROR'
        ]

        for expected_code in expected_codes:
            self.assertTrue(
                hasattr(ErrorCode, expected_code),
                f"ErrorCode.{expected_code} should exist"
            )


class TestErrorResponse(unittest.TestCase):

    def test_error_response_structure(self):
        error = ErrorResponse(
            code=ErrorCode.EMPTY_STUDENT_DATA,
            params={'count': 0},
            message='Student data is empty'
        )

        error_dict = error.to_dict()

        self.assertIn('error', error_dict)
        self.assertIn('code', error_dict['error'])
        self.assertIn('params', error_dict['error'])
        self.assertIn('message', error_dict['error'])

    def test_error_response_with_params(self):
        error = ErrorResponse(
            code=ErrorCode.STUDENT_NO_FRIENDS,
            params={'studentName': 'Alice'},
            message='Student has no friends'
        )

        error_dict = error.to_dict()

        self.assertEqual(error_dict['error']['code'], 'STUDENT_NO_FRIENDS')
        self.assertEqual(error_dict['error']['params']['studentName'], 'Alice')
        self.assertEqual(error_dict['error']['message'], 'Student has no friends')

    def test_error_response_to_dict(self):
        error = ErrorResponse(
            code=ErrorCode.TOO_MANY_CLASSES,
            params={'classCount': 10, 'studentCount': 5}
        )

        error_dict = error.to_dict()

        self.assertIsInstance(error_dict, dict)
        self.assertEqual(error_dict['error']['code'], 'TOO_MANY_CLASSES')
        self.assertEqual(error_dict['error']['params']['classCount'], 10)
        self.assertEqual(error_dict['error']['params']['studentCount'], 5)

    def test_error_response_to_tuple(self):
        error = ErrorResponse(
            code=ErrorCode.INVALID_CLASS_COUNT,
            params={'classCount': 0}
        )

        response_tuple = error.to_tuple(400)

        self.assertIsInstance(response_tuple, tuple)
        self.assertEqual(len(response_tuple), 2)
        self.assertIsInstance(response_tuple[0], dict)
        self.assertEqual(response_tuple[1], 400)

    def test_error_response_default_message(self):
        error = ErrorResponse(code=ErrorCode.EMPTY_STUDENT_DATA)

        error_dict = error.to_dict()

        self.assertEqual(error_dict['error']['message'], 'EMPTY_STUDENT_DATA')

    def test_error_response_empty_params(self):
        error = ErrorResponse(code=ErrorCode.INTERNAL_SERVER_ERROR)

        error_dict = error.to_dict()

        self.assertEqual(error_dict['error']['params'], {})

    def test_error_response_with_explicit_params(self):
        error = ErrorResponse(
            code=ErrorCode.MISSING_PARAMETER,
            params={'parameter': 'classesNumber'},
            message='Parameter is required'
        )

        error_dict = error.to_dict()

        self.assertEqual(error_dict['error']['params']['parameter'], 'classesNumber')


class TestInputValidationError(unittest.TestCase):

    def test_input_validation_error_creation(self):
        error = InputValidationError(
            code=ErrorCode.STUDENT_NO_FRIENDS,
            params={'studentName': 'Alice'},
            message='Student has no friends'
        )

        self.assertEqual(error.code, ErrorCode.STUDENT_NO_FRIENDS)
        self.assertEqual(error.params['studentName'], 'Alice')
        self.assertEqual(error.message, 'Student has no friends')

    def test_input_validation_error_to_response(self):
        error = InputValidationError(
            code=ErrorCode.DUPLICATE_STUDENT_NAMES,
            params={'duplicates': ['Alice', 'Bob']},
            message='Duplicate names found'
        )

        response = error.to_response()

        self.assertIsInstance(response, ErrorResponse)
        error_dict = response.to_dict()
        self.assertEqual(error_dict['error']['code'], 'DUPLICATE_STUDENT_NAMES')
        self.assertEqual(error_dict['error']['params']['duplicates'], ['Alice', 'Bob'])

    def test_input_validation_error_default_message(self):
        error = InputValidationError(
            code=ErrorCode.EMPTY_STUDENT_DATA,
            params={'count': 0}
        )

        self.assertEqual(error.message, 'EMPTY_STUDENT_DATA')

    def test_input_validation_error_inheritance(self):
        error = InputValidationError(
            code=ErrorCode.UNKNOWN_FRIEND,
            params={'studentName': 'Alice', 'friendName': 'Charlie'}
        )

        self.assertIsInstance(error, Exception)
        self.assertTrue(hasattr(error, 'code'))
        self.assertTrue(hasattr(error, 'params'))
        self.assertTrue(hasattr(error, 'message'))


if __name__ == '__main__':
    unittest.main()
