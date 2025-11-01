import unittest
from src.server.dto import StudentDto, ClassSummaryDto, Gender, Grade


class TestStudentDto(unittest.TestCase):

    def test_student_dto_from_valid_dict(self):
        data = {
            'name': 'Alice',
            'school': 'Test School',
            'gender': 'FEMALE',
            'academicPerformance': 'HIGH',
            'behavioralPerformance': 'MEDIUM',
            'comments': 'Good student',
            'friend1': 'Bob',
            'friend2': 'Charlie',
            'friend3': '',
            'friend4': '',
            'notWith': 'Eve',
            'clusterId': 1
        }

        student = StudentDto.from_dict(data)

        self.assertEqual(student.name, 'Alice')
        self.assertEqual(student.school, 'Test School')
        self.assertEqual(student.gender, Gender.FEMALE)
        self.assertEqual(student.academicPerformance, Grade.HIGH)
        self.assertEqual(student.behavioralPerformance, Grade.MEDIUM)
        self.assertEqual(student.comments, 'Good student')
        self.assertEqual(student.friend1, 'Bob')
        self.assertEqual(student.friend2, 'Charlie')
        self.assertEqual(student.friend3, '')
        self.assertEqual(student.friend4, '')
        self.assertEqual(student.notWith, 'Eve')
        self.assertEqual(student.clusterId, 1)

    def test_student_dto_invalid_gender(self):
        data = {
            'name': 'Alice',
            'school': 'Test School',
            'gender': 'INVALID',
            'academicPerformance': 'HIGH',
            'behavioralPerformance': 'MEDIUM',
            'comments': '',
            'friend1': '',
            'friend2': '',
            'friend3': '',
            'friend4': ''
        }

        with self.assertRaises(ValueError):
            StudentDto.from_dict(data)

    def test_student_dto_invalid_academic_performance(self):
        data = {
            'name': 'Alice',
            'school': 'Test School',
            'gender': 'FEMALE',
            'academicPerformance': 'INVALID',
            'behavioralPerformance': 'MEDIUM',
            'comments': '',
            'friend1': '',
            'friend2': '',
            'friend3': '',
            'friend4': ''
        }

        with self.assertRaises(ValueError):
            StudentDto.from_dict(data)

    def test_student_dto_invalid_behavioral_performance(self):
        data = {
            'name': 'Alice',
            'school': 'Test School',
            'gender': 'FEMALE',
            'academicPerformance': 'HIGH',
            'behavioralPerformance': 'INVALID',
            'comments': '',
            'friend1': '',
            'friend2': '',
            'friend3': '',
            'friend4': ''
        }

        with self.assertRaises(ValueError):
            StudentDto.from_dict(data)

    def test_student_dto_optional_fields(self):
        data = {
            'name': 'Alice',
            'school': 'Test School',
            'gender': 'FEMALE',
            'academicPerformance': 'HIGH',
            'behavioralPerformance': 'MEDIUM',
            'comments': '',
            'friend1': 'Bob',
            'friend2': '',
            'friend3': '',
            'friend4': ''
        }

        student = StudentDto.from_dict(data)

        self.assertIsNone(student.notWith)
        self.assertIsNone(student.clusterId)

    def test_student_dto_missing_required_fields(self):
        data = {
            'name': 'Alice',
            'school': 'Test School'
        }

        with self.assertRaises(KeyError):
            StudentDto.from_dict(data)

    def test_gender_enum_values(self):
        self.assertEqual(Gender.MALE.value, 'MALE')
        self.assertEqual(Gender.FEMALE.value, 'FEMALE')

    def test_grade_enum_values(self):
        self.assertEqual(Grade.LOW.value, 'LOW')
        self.assertEqual(Grade.MEDIUM.value, 'MEDIUM')
        self.assertEqual(Grade.HIGH.value, 'HIGH')


class TestClassSummaryDto(unittest.TestCase):

    def test_class_summary_dto_creation(self):
        summary = ClassSummaryDto(
            classNumber=1,
            studentsCount=25,
            malesCount=12,
            averageAcademicPerformance=2.5,
            averageBehaviouralPerformance=2.3,
            withoutFriends=0,
            unwantedMatches=0
        )

        self.assertEqual(summary.classNumber, 1)
        self.assertEqual(summary.studentsCount, 25)
        self.assertEqual(summary.malesCount, 12)
        self.assertEqual(summary.averageAcademicPerformance, 2.5)
        self.assertEqual(summary.averageBehaviouralPerformance, 2.3)
        self.assertEqual(summary.withoutFriends, 0)
        self.assertEqual(summary.unwantedMatches, 0)

    def test_class_summary_dto_with_violations(self):
        summary = ClassSummaryDto(
            classNumber=2,
            studentsCount=20,
            malesCount=10,
            averageAcademicPerformance=2.0,
            averageBehaviouralPerformance=2.0,
            withoutFriends=2,
            unwantedMatches=1
        )

        self.assertEqual(summary.withoutFriends, 2)
        self.assertEqual(summary.unwantedMatches, 1)


if __name__ == '__main__':
    unittest.main()
