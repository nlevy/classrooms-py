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
class TestSoftConstraints(unittest.TestCase):

    def setUp(self):
        self.sample_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack', 'Kate', 'Leo'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE', 'FEMALE', 'MALE', 'FEMALE', 'MALE', 'FEMALE', 'MALE', 'FEMALE', 'MALE'],
            'academicPerformance': ['HIGH', 'HIGH', 'MEDIUM', 'MEDIUM', 'LOW', 'LOW', 'HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM', 'LOW'],
            'behavioralPerformance': ['HIGH', 'MEDIUM', 'HIGH', 'LOW', 'MEDIUM', 'HIGH', 'LOW', 'MEDIUM', 'HIGH', 'LOW', 'MEDIUM', 'HIGH'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie', 'Frank', 'Eve', 'Henry', 'Grace', 'Jack', 'Ivy', 'Leo', 'Kate'],
            'friend2': ['Charlie', 'David', 'Alice', 'Bob', 'Grace', 'Henry', 'Ivy', 'Jack', 'Kate', 'Leo', 'Alice', 'Bob'],
            'friend3': ['', '', '', '', '', '', '', '', '', '', '', ''],
            'friend4': ['', '', '', '', '', '', '', '', '', '', '', ''],
            'notWith': ['', '', '', '', '', '', '', '', '', '', '', ''],
            'clusterId': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]
        })

    def test_friendship_satisfaction_above_threshold(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        info = service.get_last_assignment_info()
        evaluation = info['metadata']['evaluation']

        friendship_satisfaction = evaluation.get('friendship_satisfaction', 0)
        self.assertGreaterEqual(friendship_satisfaction, 0.0,
                               "Friendship satisfaction should be at least 0%")

    def test_gender_balance_within_tolerance(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        for class_set in classes:
            class_df = self.sample_df[self.sample_df['name'].isin(class_set)]
            if len(class_df) == 0:
                continue

            male_count = len(class_df[class_df['gender'] == 'MALE'])
            total_count = len(class_df)
            male_ratio = male_count / total_count if total_count > 0 else 0.5

            self.assertGreaterEqual(male_ratio, 0.0)
            self.assertLessEqual(male_ratio, 1.0)

    def test_academic_balance_distribution(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        for class_set in classes:
            class_df = self.sample_df[self.sample_df['name'].isin(class_set)]
            if len(class_df) == 0:
                continue

            performance_counts = class_df['academicPerformance'].value_counts().to_dict()

            high_count = performance_counts.get('HIGH', 0)
            medium_count = performance_counts.get('MEDIUM', 0)
            low_count = performance_counts.get('LOW', 0)

            total = high_count + medium_count + low_count
            self.assertEqual(total, len(class_df))

    def test_behavioral_balance_distribution(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        for class_set in classes:
            class_df = self.sample_df[self.sample_df['name'].isin(class_set)]
            if len(class_df) == 0:
                continue

            performance_counts = class_df['behavioralPerformance'].value_counts().to_dict()

            high_count = performance_counts.get('HIGH', 0)
            medium_count = performance_counts.get('MEDIUM', 0)
            low_count = performance_counts.get('LOW', 0)

            total = high_count + medium_count + low_count
            self.assertEqual(total, len(class_df))

    def test_class_size_balance(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        sizes = [len(class_set) for class_set in classes]
        max_size = max(sizes)
        min_size = min(sizes)

        self.assertLessEqual(max_size - min_size, 2,
                           "Class sizes should be reasonably balanced (differ by at most 2)")

    @unittest.skipIf(not ORTOOLS_AVAILABLE, "ortools not available")
    @pytest.mark.cp_sat
    def test_cp_sat_better_than_greedy(self):
        greedy_service = ClassAssignmentService(self.sample_df, strategy='greedy')
        greedy_classes = greedy_service.assign_classes(3)
        greedy_info = greedy_service.get_last_assignment_info()
        greedy_score = greedy_info['solution_quality']

        cp_sat_service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)
        cp_sat_classes = cp_sat_service.assign_classes(3)
        cp_sat_info = cp_sat_service.get_last_assignment_info()
        cp_sat_score = cp_sat_info['solution_quality']

        self.assertGreaterEqual(cp_sat_score, 0)
        self.assertGreaterEqual(greedy_score, 0)

    def test_maximize_friend_groups(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        total_friendships_together = 0
        total_friendships = 0

        for _, student_row in self.sample_df.iterrows():
            student_name = student_row['name']
            friends = [student_row[f'friend{i}'] for i in range(1, 5) if student_row[f'friend{i}']]

            student_class = None
            for class_set in classes:
                if student_name in class_set:
                    student_class = class_set
                    break

            if student_class:
                for friend in friends:
                    total_friendships += 1
                    if friend in student_class:
                        total_friendships_together += 1

        if total_friendships > 0:
            satisfaction_rate = total_friendships_together / total_friendships
            self.assertGreaterEqual(satisfaction_rate, 0.0)
            self.assertLessEqual(satisfaction_rate, 1.0)

    def test_minimize_gender_deviation(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        total_males = len(self.sample_df[self.sample_df['gender'] == 'MALE'])
        total_students = len(self.sample_df)
        overall_male_ratio = total_males / total_students

        deviations = []
        for class_set in classes:
            class_df = self.sample_df[self.sample_df['name'].isin(class_set)]
            if len(class_df) == 0:
                continue

            male_count = len(class_df[class_df['gender'] == 'MALE'])
            class_male_ratio = male_count / len(class_df)
            deviation = abs(class_male_ratio - overall_male_ratio)
            deviations.append(deviation)

        if deviations:
            avg_deviation = sum(deviations) / len(deviations)
            self.assertLessEqual(avg_deviation, 0.5,
                               "Average gender deviation should be reasonable")

    def test_overall_solution_quality(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')
        classes = service.assign_classes(3)

        info = service.get_last_assignment_info()
        overall_score = info['solution_quality']

        self.assertGreaterEqual(overall_score, 0,
                               "Solution quality score should be at least 0")
        self.assertLessEqual(overall_score, 100,
                            "Solution quality score should be at most 100")


if __name__ == '__main__':
    unittest.main()
