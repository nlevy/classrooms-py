import unittest
import pandas as pd
import pytest
import time

try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

from src.service.class_assignment_service import ClassAssignmentService


@pytest.mark.quality
class TestEdgeCases(unittest.TestCase):

    def test_two_students_two_classes(self):
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
        classes = service.assign_classes(2)

        self.assertEqual(len(classes), 2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(all_students, {'Alice', 'Bob'})

    def test_two_students_one_class(self):
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
        classes = service.assign_classes(1)

        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0], {'Alice', 'Bob'})

    def test_all_students_one_class(self):
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
        classes = service.assign_classes(1)

        self.assertEqual(len(classes), 1)
        self.assertEqual(len(classes[0]), 4)

    @pytest.mark.slow
    def test_100_students_10_classes(self):
        df = pd.DataFrame({
            'name': [f'Student{i}' for i in range(100)],
            'gender': ['MALE' if i % 2 == 0 else 'FEMALE' for i in range(100)],
            'academicPerformance': ['HIGH' if i % 3 == 0 else 'MEDIUM' if i % 3 == 1 else 'LOW' for i in range(100)],
            'behavioralPerformance': ['HIGH' if i % 3 == 0 else 'MEDIUM' if i % 3 == 1 else 'LOW' for i in range(100)],
            'friend1': [f'Student{(i+1) % 100}' for i in range(100)],
            'friend2': [f'Student{(i+2) % 100}' for i in range(100)],
            'friend3': [''] * 100,
            'friend4': [''] * 100,
            'notWith': [''] * 100,
            'clusterId': [i // 10 + 1 for i in range(100)]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(10)

        self.assertEqual(len(classes), 10)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 100)

    def test_students_equal_classes(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE', 'FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie', 'Frank', 'Eve'],
            'friend2': ['', '', '', '', '', ''],
            'friend3': ['', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', ''],
            'notWith': ['', '', '', '', '', ''],
            'clusterId': [1, 1, 2, 2, 3, 3]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(3)

        sizes = [len(class_set) for class_set in classes]
        self.assertEqual(sum(sizes), 6)
        self.assertLessEqual(max(sizes) - min(sizes), 3,
                           "Class sizes should be reasonably balanced")

    def test_maximum_friends_per_student(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE', 'FEMALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'friend1': ['Bob', 'Alice', 'Alice', 'Alice', 'Alice'],
            'friend2': ['Charlie', 'Charlie', 'Bob', 'Bob', 'Bob'],
            'friend3': ['David', 'David', 'David', 'Charlie', 'Charlie'],
            'friend4': ['Eve', 'Eve', 'Eve', 'Eve', 'David'],
            'notWith': ['', '', '', '', ''],
            'clusterId': [1, 1, 2, 2, 3]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 5)

    def test_all_male_students(self):
        df = pd.DataFrame({
            'name': ['Bob', 'Charlie', 'David', 'Frank', 'Henry', 'Jack'],
            'gender': ['MALE', 'MALE', 'MALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'friend1': ['Charlie', 'Bob', 'Frank', 'David', 'Jack', 'Henry'],
            'friend2': ['', '', '', '', '', ''],
            'friend3': ['', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', ''],
            'notWith': ['', '', '', '', '', ''],
            'clusterId': [1, 1, 2, 2, 3, 3]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 6)

        for class_set in classes:
            class_df = df[df['name'].isin(class_set)]
            all_male = all(class_df['gender'] == 'MALE')
            self.assertTrue(all_male)

    def test_all_high_performance(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'HIGH', 'HIGH', 'HIGH'],
            'behavioralPerformance': ['HIGH', 'HIGH', 'HIGH', 'HIGH'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie'],
            'friend2': ['', '', '', ''],
            'friend3': ['', '', '', ''],
            'friend4': ['', '', '', ''],
            'notWith': ['', '', '', ''],
            'clusterId': [1, 1, 2, 2]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 4)

    def test_single_cluster_all_students(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE', 'FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie', 'Frank', 'Eve'],
            'friend2': ['', '', '', '', '', ''],
            'friend3': ['', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', ''],
            'notWith': ['', '', '', '', '', ''],
            'clusterId': [1, 1, 1, 1, 1, 1]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 6)

    def test_all_students_mutual_friends(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', 'Alice', 'Alice', 'Alice'],
            'friend2': ['Charlie', 'Charlie', 'Bob', 'Bob'],
            'friend3': ['David', 'David', 'David', 'Charlie'],
            'friend4': ['', '', '', ''],
            'notWith': ['', '', '', ''],
            'clusterId': [1, 1, 2, 2]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 4)

    def test_mutual_not_with(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Charlie', 'David', 'Alice', 'Bob'],
            'friend2': ['', '', '', ''],
            'friend3': ['', '', '', ''],
            'friend4': ['', '', '', ''],
            'notWith': ['Bob', 'Alice', '', ''],
            'clusterId': [1, 1, 2, 2]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        alice_class = None
        bob_class = None
        for i, class_set in enumerate(classes):
            if 'Alice' in class_set:
                alice_class = i
            if 'Bob' in class_set:
                bob_class = i

        self.assertNotEqual(alice_class, bob_class,
                          "Alice and Bob should be in different classes (mutual notWith)")

    def test_chain_not_with(self):
        df = pd.DataFrame({
            'name': ['A', 'B', 'C', 'D', 'E', 'F'],
            'gender': ['MALE', 'FEMALE', 'MALE', 'FEMALE', 'MALE', 'FEMALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'friend1': ['F', 'A', 'B', 'C', 'D', 'E'],
            'friend2': ['', '', '', '', '', ''],
            'friend3': ['', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', ''],
            'notWith': ['B', 'C', 'D', '', '', ''],
            'clusterId': [1, 2, 3, 4, 5, 6]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(3)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 6,
                        "All students should be assigned in chain notWith scenario")

    def test_orphan_friend_references(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', 'Charlie', 'David', 'Alice'],
            'friend2': ['Charlie', '', '', ''],
            'friend3': ['', '', '', ''],
            'friend4': ['', '', '', ''],
            'notWith': ['', '', '', ''],
            'clusterId': [1, 1, 2, 2]
        })

        service = ClassAssignmentService(df, strategy='greedy')
        classes = service.assign_classes(2)

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 4)

    def test_very_fast_greedy(self):
        df = pd.DataFrame({
            'name': [f'Student{i}' for i in range(50)],
            'gender': ['MALE' if i % 2 == 0 else 'FEMALE' for i in range(50)],
            'academicPerformance': ['HIGH' if i % 3 == 0 else 'MEDIUM' if i % 3 == 1 else 'LOW' for i in range(50)],
            'behavioralPerformance': ['HIGH' if i % 3 == 0 else 'MEDIUM' if i % 3 == 1 else 'LOW' for i in range(50)],
            'friend1': [f'Student{(i+1) % 50}' for i in range(50)],
            'friend2': [''] * 50,
            'friend3': [''] * 50,
            'friend4': [''] * 50,
            'notWith': [''] * 50,
            'clusterId': [i // 5 + 1 for i in range(50)]
        })

        service = ClassAssignmentService(df, strategy='greedy')

        start_time = time.time()
        classes = service.assign_classes(5)
        execution_time = time.time() - start_time

        self.assertLess(execution_time, 1.0,
                       "Greedy strategy should complete in under 1 second for 50 students")

        all_students = set()
        for class_set in classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 50)

    @unittest.skipIf(not ORTOOLS_AVAILABLE, "ortools not available")
    @pytest.mark.cp_sat
    @pytest.mark.slow
    def test_cp_sat_optimization_quality(self):
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE', 'FEMALE', 'MALE', 'FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie', 'Frank', 'Eve', 'Henry', 'Grace'],
            'friend2': ['Charlie', 'David', 'Alice', 'Bob', 'Grace', 'Grace', 'Frank', 'Eve'],
            'friend3': ['', '', '', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', '', '', ''],
            'notWith': ['', '', '', '', '', '', '', ''],
            'clusterId': [1, 1, 2, 2, 3, 3, 4, 4]
        })

        cp_sat_service = ClassAssignmentService(df, strategy='cp_sat', timeout_seconds=10)
        cp_sat_classes = cp_sat_service.assign_classes(2)
        cp_sat_info = cp_sat_service.get_last_assignment_info()

        self.assertGreaterEqual(cp_sat_info['solution_quality'], 0)
        self.assertLessEqual(cp_sat_info['solution_quality'], 100)


if __name__ == '__main__':
    unittest.main()
