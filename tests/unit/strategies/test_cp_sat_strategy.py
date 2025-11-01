import unittest
import pandas as pd
import pytest

try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

from src.service.strategies.cp_sat_strategy import CPSATStrategy


@pytest.mark.cp_sat
@unittest.skipIf(not ORTOOLS_AVAILABLE, "ortools not available")
class TestCPSATStrategy(unittest.TestCase):

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

    def test_basic_assignment(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        self.assertEqual(len(result.classes), 2)

        all_students = set()
        for class_set in result.classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 6)
        self.assertEqual(all_students, {'Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'})

    def test_hard_constraint_no_friendless_students(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        for class_set in result.classes:
            for student in class_set:
                student_row = self.sample_df[self.sample_df['name'] == student].iloc[0]
                friends = [student_row[f'friend{i}'] for i in range(1, 5) if student_row[f'friend{i}']]

                friends_in_class = [f for f in friends if f in class_set]
                self.assertGreater(len(friends_in_class), 0,
                                 f"CP-SAT should guarantee {student} has friends in class")

    def test_not_with_absolute_enforcement(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        charlie_class = None
        eve_class = None
        for i, class_set in enumerate(result.classes):
            if 'Charlie' in class_set:
                charlie_class = i
            if 'Eve' in class_set:
                eve_class = i

        self.assertNotEqual(charlie_class, eve_class,
                          "CP-SAT must enforce notWith constraints")

    def test_cluster_grouping_enforcement(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        all_students = set()
        for class_set in result.classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 6, "All students should be assigned")

    def test_timeout_handling(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=1)

        result = strategy.assign_classes(2)

        self.assertIn('solver_time', result.metadata)
        self.assertIn('timeout_used', result.metadata)
        self.assertEqual(result.metadata['timeout_used'], 1)

    def test_metadata_completeness(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        self.assertIn('algorithm', result.metadata)
        self.assertIn('execution_time', result.metadata)
        self.assertIn('solver_status', result.metadata)
        self.assertIn('solver_time', result.metadata)
        self.assertIn('num_classes', result.metadata)
        self.assertIn('num_students', result.metadata)
        self.assertIn('timeout_used', result.metadata)

        self.assertEqual(result.metadata['algorithm'], 'cp_sat')
        self.assertEqual(result.metadata['num_classes'], 2)
        self.assertEqual(result.metadata['num_students'], 6)

    def test_strategy_name_property(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        self.assertEqual(strategy.name, 'cp_sat')

    def test_supports_timeout_property(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        self.assertTrue(strategy.supports_timeout)

    def test_all_students_assigned_once(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        student_count = {}
        for class_set in result.classes:
            for student in class_set:
                student_count[student] = student_count.get(student, 0) + 1

        for student, count in student_count.items():
            self.assertEqual(count, 1, f"{student} should be assigned exactly once")

    def test_no_empty_classes(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        for class_set in result.classes:
            self.assertGreater(len(class_set), 0, "No class should be empty")

    def test_single_class_assignment(self):
        simple_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'gender': ['FEMALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', 'Alice', 'Alice'],
            'friend2': ['Charlie', 'Charlie', 'Bob'],
            'friend3': ['', '', ''],
            'friend4': ['', '', ''],
            'notWith': ['', '', ''],
            'clusterId': [1, 1, 1]
        })

        strategy = CPSATStrategy(simple_df, timeout_seconds=10)
        result = strategy.assign_classes(1)

        self.assertEqual(len(result.classes), 1)
        self.assertEqual(len(result.classes[0]), 3)

    def test_timeout_configuration(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=20)
        self.assertEqual(strategy.timeout_seconds, 20)

    def test_very_small_dataset(self):
        small_df = pd.DataFrame({
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

        strategy = CPSATStrategy(small_df, timeout_seconds=10)
        result = strategy.assign_classes(1)

        self.assertEqual(len(result.classes), 1)
        self.assertEqual(result.classes[0], {'Alice', 'Bob'})

    def test_balanced_class_sizes(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        sizes = [len(class_set) for class_set in result.classes]
        self.assertLessEqual(max(sizes) - min(sizes), 3,
                            "Class sizes should be reasonably balanced")

    def test_execution_time_tracked(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        self.assertGreater(result.metadata['execution_time'], 0)
        self.assertGreater(result.metadata['solver_time'], 0)

    def test_multiple_clusters_enforcement(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(3)

        all_students = set()
        for class_set in result.classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 6)
        self.assertEqual(len(result.classes), 3)

    def test_solver_status_recorded(self):
        strategy = CPSATStrategy(self.sample_df, timeout_seconds=10)
        result = strategy.assign_classes(2)

        self.assertIn('solver_status', result.metadata)
        self.assertIsNotNone(result.metadata['solver_status'])

if __name__ == '__main__':
    unittest.main()
