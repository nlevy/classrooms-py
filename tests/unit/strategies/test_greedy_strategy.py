import unittest
import pandas as pd
import time
from src.service.strategies.greedy_strategy import GreedyStrategy


class TestGreedyStrategy(unittest.TestCase):

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
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(2)

        self.assertEqual(len(result.classes), 2)

        all_students = set()
        for class_set in result.classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 6)
        self.assertEqual(all_students, {'Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'})

    def test_cluster_grouping(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(3)

        alice_class = None
        bob_class = None
        for i, class_set in enumerate(result.classes):
            if 'Alice' in class_set:
                alice_class = i
            if 'Bob' in class_set:
                bob_class = i

        self.assertEqual(alice_class, bob_class, "Alice and Bob should be in same class (cluster 1)")

    def test_not_with_constraints(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(2)

        all_students = set()
        for class_set in result.classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 6, "All students should be assigned")
        self.assertEqual(len(result.classes), 2, "Should create 2 classes")

    def test_friendship_preservation(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(2)

        for class_set in result.classes:
            for student in class_set:
                student_row = self.sample_df[self.sample_df['name'] == student].iloc[0]
                friends = [student_row[f'friend{i}'] for i in range(1, 5) if student_row[f'friend{i}']]

                friends_in_class = [f for f in friends if f in class_set]
                self.assertGreater(len(friends_in_class), 0, f"{student} should have at least one friend in class")

    def test_balanced_class_sizes(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(2)

        sizes = [len(class_set) for class_set in result.classes]

        self.assertLessEqual(max(sizes) - min(sizes), 2, "Class sizes should be reasonably balanced")

    def test_execution_time_tracking(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(2)

        self.assertIn('execution_time', result.metadata)
        self.assertGreater(result.metadata['execution_time'], 0)

    def test_metadata_completeness(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(3)

        self.assertIn('algorithm', result.metadata)
        self.assertIn('execution_time', result.metadata)
        self.assertIn('num_classes', result.metadata)
        self.assertIn('num_students', result.metadata)

        self.assertEqual(result.metadata['algorithm'], 'greedy')
        self.assertEqual(result.metadata['num_classes'], 3)
        self.assertEqual(result.metadata['num_students'], 6)

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

        strategy = GreedyStrategy(small_df)
        result = strategy.assign_classes(1)

        self.assertEqual(len(result.classes), 1)
        self.assertEqual(result.classes[0], {'Alice', 'Bob'})

    def test_two_students_two_classes_edge_case(self):
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
            'clusterId': [1, 2]
        })

        strategy = GreedyStrategy(small_df)
        result = strategy.assign_classes(2)

        self.assertEqual(len(result.classes), 2)

        all_students = set()
        for class_set in result.classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 2)

    def test_large_dataset_performance(self):
        names = [f'Student{i}' for i in range(100)]
        large_df = pd.DataFrame({
            'name': names,
            'gender': ['MALE' if i % 2 == 0 else 'FEMALE' for i in range(100)],
            'academicPerformance': ['HIGH' if i % 3 == 0 else 'MEDIUM' if i % 3 == 1 else 'LOW' for i in range(100)],
            'behavioralPerformance': ['HIGH' if i % 3 == 0 else 'MEDIUM' if i % 3 == 1 else 'LOW' for i in range(100)],
            'friend1': [names[(i + 1) % 100] for i in range(100)],
            'friend2': [names[(i + 2) % 100] for i in range(100)],
            'friend3': [''] * 100,
            'friend4': [''] * 100,
            'notWith': [''] * 100,
            'clusterId': [i // 10 for i in range(100)]
        })

        strategy = GreedyStrategy(large_df)
        start_time = time.time()
        result = strategy.assign_classes(10)
        execution_time = time.time() - start_time

        self.assertLess(execution_time, 1.0, "Large dataset should complete in < 1 second")
        self.assertEqual(len(result.classes), 10)

        all_students = set()
        for class_set in result.classes:
            all_students.update(class_set)
        self.assertEqual(len(all_students), 100)

    def test_strategy_name_property(self):
        strategy = GreedyStrategy(self.sample_df)
        self.assertEqual(strategy.name, 'greedy')

    def test_supports_timeout_property(self):
        strategy = GreedyStrategy(self.sample_df)
        self.assertFalse(strategy.supports_timeout)

    def test_all_students_assigned_once(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(3)

        student_count = {}
        for class_set in result.classes:
            for student in class_set:
                student_count[student] = student_count.get(student, 0) + 1

        for student, count in student_count.items():
            self.assertEqual(count, 1, f"{student} should be assigned exactly once")

    def test_no_empty_classes(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(2)

        for class_set in result.classes:
            self.assertGreater(len(class_set), 0, "No class should be empty")

    def test_single_class_assignment(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(1)

        self.assertEqual(len(result.classes), 1)
        self.assertEqual(len(result.classes[0]), 6)

    def test_deterministic_with_same_data(self):
        strategy1 = GreedyStrategy(self.sample_df.copy())
        result1 = strategy1.assign_classes(2)

        strategy2 = GreedyStrategy(self.sample_df.copy())
        result2 = strategy2.assign_classes(2)

        self.assertEqual(len(result1.classes), len(result2.classes))

    def test_gender_distribution_attempt(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(2)

        for class_set in result.classes:
            if len(class_set) > 0:
                males = sum(1 for s in class_set
                           if self.sample_df[self.sample_df['name'] == s]['gender'].values[0] == 'MALE')
                total = len(class_set)

                self.assertGreater(total, 0)

    def test_multiple_clusters(self):
        strategy = GreedyStrategy(self.sample_df)
        result = strategy.assign_classes(3)

        all_students = set()
        for class_set in result.classes:
            all_students.update(class_set)

        self.assertEqual(len(all_students), 6, "All students should be assigned")
        self.assertEqual(len(result.classes), 3, "Should create 3 classes")


if __name__ == '__main__':
    unittest.main()
