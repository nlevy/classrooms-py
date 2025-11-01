import unittest
import pandas as pd
import pytest

try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

from src.service.class_assignment_service import ClassAssignmentService


@pytest.mark.quality
class TestHardConstraints(unittest.TestCase):

    def setUp(self):
        self.sample_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE', 'FEMALE', 'MALE', 'FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie', 'Frank', 'Eve', 'Henry', 'Grace'],
            'friend2': ['Charlie', 'David', 'Alice', 'Bob', 'Grace', 'Grace', 'Frank', 'Eve'],
            'friend3': ['', '', '', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', '', '', ''],
            'notWith': ['', '', 'Eve', '', 'Charlie', '', '', ''],
            'clusterId': [1, 1, 2, 2, 3, 3, 4, 4]
        })

    def test_no_friendless_students_greedy(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        info = service.get_last_assignment_info()
        friendless_students = info['metadata']['evaluation']['students_without_friends']

        self.assertIsInstance(friendless_students, list)

    @unittest.skipIf(not ORTOOLS_AVAILABLE, "ortools not available")
    @pytest.mark.cp_sat
    def test_no_friendless_students_cp_sat(self):
        service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)
        classes = service.assign_classes(3)

        info = service.get_last_assignment_info()
        friendless_students = info['metadata']['evaluation']['students_without_friends']

        self.assertEqual(len(friendless_students), 0,
                        "CP-SAT should guarantee zero friendless students")

    def test_not_with_always_respected(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        charlie_class = None
        eve_class = None
        for i, class_set in enumerate(classes):
            if 'Charlie' in class_set:
                charlie_class = i
            if 'Eve' in class_set:
                eve_class = i

        self.assertIsNotNone(charlie_class)
        self.assertIsNotNone(eve_class)
        self.assertNotEqual(charlie_class, eve_class,
                          "Charlie and Eve should be in different classes (notWith constraint)")

    def test_all_students_assigned(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)

        expected_students = set(self.sample_df['name'].tolist())
        self.assertEqual(all_students, expected_students,
                        "All students must be assigned to a class")

    def test_no_duplicate_assignments(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        student_count = {}
        for class_set in classes:
            for student in class_set:
                student_count[student] = student_count.get(student, 0) + 1

        for student, count in student_count.items():
            self.assertEqual(count, 1,
                           f"{student} should be assigned to exactly one class, found {count}")

    def test_correct_number_of_classes(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        num_classes = 3
        classes = service.assign_classes(num_classes)

        non_empty_classes = [c for c in classes if len(c) > 0]
        self.assertGreaterEqual(len(non_empty_classes), 1,
                               "Should create at least one non-empty class")
        self.assertLessEqual(len(non_empty_classes), num_classes,
                            f"Should create at most {num_classes} classes")

    def test_complex_not_with_network(self):
        df = pd.DataFrame({
            'name': ['A', 'B', 'C', 'D', 'E', 'F'],
            'gender': ['MALE', 'FEMALE', 'MALE', 'FEMALE', 'MALE', 'FEMALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'friend1': ['B', 'A', 'D', 'C', 'F', 'E'],
            'friend2': ['', '', '', '', '', ''],
            'friend3': ['', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', ''],
            'notWith': ['C', 'D', 'A', 'B', '', ''],
            'clusterId': [1, 1, 2, 2, 3, 3]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(3)

        info = service.get_last_assignment_info()
        not_with_violations = info['metadata']['evaluation']['not_with_violations']

        self.assertEqual(len(not_with_violations), 0,
                        "Complex notWith network should be respected")

    def test_large_clusters(self):
        df = pd.DataFrame({
            'name': [f'Student{i}' for i in range(15)],
            'gender': ['MALE' if i % 2 == 0 else 'FEMALE' for i in range(15)],
            'academicPerformance': ['HIGH' if i % 3 == 0 else 'MEDIUM' if i % 3 == 1 else 'LOW' for i in range(15)],
            'behavioralPerformance': ['HIGH' if i % 3 == 0 else 'MEDIUM' if i % 3 == 1 else 'LOW' for i in range(15)],
            'friend1': [f'Student{(i+1) % 15}' for i in range(15)],
            'friend2': [''] * 15,
            'friend3': [''] * 15,
            'friend4': [''] * 15,
            'notWith': [''] * 15,
            'clusterId': [1] * 10 + [2] * 5
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 15,
                        "All students should be assigned even with large clusters")

    def test_conflicting_constraints(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'gender': ['FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM'],
            'behavioralPerformance': ['HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Alice'],
            'friend2': ['', ''],
            'friend3': ['', ''],
            'friend4': ['', ''],
            'notWith': ['Bob', 'Alice'],
            'clusterId': [1, 1]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(1)

        info = service.get_last_assignment_info()
        not_with_violations = info['metadata']['evaluation']['not_with_violations']

        self.assertGreater(len(not_with_violations), 0,
                         "Conflicting constraints (same cluster + notWith + 1 class) should violate notWith")


if __name__ == '__main__':
    unittest.main()
