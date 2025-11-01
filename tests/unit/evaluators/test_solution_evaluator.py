import unittest
import networkx as nx
from src.service.evaluators.solution_evaluator import SolutionEvaluator


class TestSolutionEvaluator(unittest.TestCase):

    def setUp(self):
        self.G = nx.Graph()
        self.G.add_node('Alice', gender='FEMALE', academic='HIGH', behavioral='MEDIUM')
        self.G.add_node('Bob', gender='MALE', academic='MEDIUM', behavioral='HIGH')
        self.G.add_node('Charlie', gender='MALE', academic='LOW', behavioral='MEDIUM')
        self.G.add_node('David', gender='MALE', academic='HIGH', behavioral='LOW')
        self.G.add_node('Eve', gender='FEMALE', academic='MEDIUM', behavioral='HIGH')
        self.G.add_node('Frank', gender='MALE', academic='LOW', behavioral='MEDIUM')

        self.G.add_edge('Alice', 'Bob')
        self.G.add_edge('Alice', 'Charlie')
        self.G.add_edge('Bob', 'David')
        self.G.add_edge('Charlie', 'David')
        self.G.add_edge('Eve', 'Frank')

        self.not_with = {
            'Charlie': ['Eve'],
            'Eve': ['Charlie']
        }

    def test_detect_students_without_friends(self):
        classes = [
            {'Alice', 'David'},
            {'Bob', 'Charlie', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertGreater(len(metrics['students_without_friends']), 0)
        student_names = [item['student'] for item in metrics['students_without_friends']]
        self.assertIn('Alice', student_names)

    def test_detect_not_with_violations(self):
        classes = [
            {'Alice', 'Bob'},
            {'Charlie', 'Eve', 'David', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertGreater(len(metrics['not_with_violations']), 0)

    def test_detect_unassigned_students(self):
        classes = [
            {'Alice', 'Bob'},
            {'Charlie', 'David'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(len(metrics['unassigned_students']), 2)
        self.assertIn('Eve', metrics['unassigned_students'])
        self.assertIn('Frank', metrics['unassigned_students'])

    def test_detect_multiply_assigned_students(self):
        classes = [
            {'Alice', 'Bob', 'Charlie'},
            {'Alice', 'David', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(len(metrics['multiply_assigned_students']), 1)
        self.assertIn('Alice', metrics['multiply_assigned_students'])

    def test_perfect_hard_constraints(self):
        classes = [
            {'Alice', 'Bob', 'David'},
            {'Charlie', 'Frank'}
        ]

        no_not_with = {}
        evaluator = SolutionEvaluator(self.G, no_not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(len(metrics['not_with_violations']), 0)
        self.assertEqual(len(metrics['multiply_assigned_students']), 0)

    def test_friendship_satisfaction_calculation(self):
        classes = [
            {'Alice', 'Bob', 'Charlie'},
            {'David', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertIn('friendship_satisfaction_rate', metrics)
        self.assertGreaterEqual(metrics['friendship_satisfaction_rate'], 0.0)
        self.assertLessEqual(metrics['friendship_satisfaction_rate'], 1.0)

    def test_friendship_distribution_per_class(self):
        classes = [
            {'Alice', 'Bob', 'Charlie'},
            {'David', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertIn('friendship_distribution', metrics)
        self.assertEqual(len(metrics['friendship_distribution']), 2)

        for dist in metrics['friendship_distribution']:
            self.assertIn('class', dist)
            self.assertIn('total_friendships_in_class', dist)
            self.assertIn('avg_friends_per_student', dist)

    def test_zero_friendship_satisfaction(self):
        G = nx.Graph()
        G.add_node('Alice', gender='FEMALE', academic='HIGH', behavioral='MEDIUM')
        G.add_node('Bob', gender='MALE', academic='MEDIUM', behavioral='HIGH')
        G.add_node('Charlie', gender='MALE', academic='LOW', behavioral='MEDIUM')
        G.add_node('David', gender='MALE', academic='HIGH', behavioral='LOW')

        G.add_edge('Alice', 'Bob')
        G.add_edge('Charlie', 'David')

        classes = [
            {'Alice', 'Charlie'},
            {'Bob', 'David'}
        ]

        evaluator = SolutionEvaluator(G, {})
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(metrics['friendship_satisfaction_rate'], 0.0)

    def test_perfect_friendship_satisfaction(self):
        G = nx.Graph()
        G.add_node('Alice', gender='FEMALE', academic='HIGH', behavioral='MEDIUM')
        G.add_node('Bob', gender='MALE', academic='MEDIUM', behavioral='HIGH')
        G.add_node('Charlie', gender='MALE', academic='LOW', behavioral='MEDIUM')
        G.add_node('David', gender='MALE', academic='HIGH', behavioral='LOW')

        G.add_edge('Alice', 'Bob')
        G.add_edge('Charlie', 'David')

        classes = [
            {'Alice', 'Bob'},
            {'Charlie', 'David'}
        ]

        evaluator = SolutionEvaluator(G, {})
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(metrics['friendship_satisfaction_rate'], 1.0)

    def test_size_balance_equal_distribution(self):
        classes = [
            {'Alice', 'Bob', 'Charlie'},
            {'David', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(metrics['size_balance']['size_variance'], 0)
        self.assertEqual(metrics['size_balance']['max_size_difference'], 0)

    def test_size_balance_unequal_distribution(self):
        classes = [
            {'Alice', 'Bob'},
            {'Charlie', 'David', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(metrics['size_balance']['size_variance'], 2)
        self.assertEqual(metrics['size_balance']['max_size_difference'], 2)

    def test_gender_balance_perfect(self):
        G = nx.Graph()
        G.add_node('Alice', gender='FEMALE', academic='HIGH', behavioral='MEDIUM')
        G.add_node('Bob', gender='MALE', academic='MEDIUM', behavioral='HIGH')
        G.add_node('Charlie', gender='FEMALE', academic='LOW', behavioral='MEDIUM')
        G.add_node('David', gender='MALE', academic='HIGH', behavioral='LOW')

        G.add_edge('Alice', 'Bob')
        G.add_edge('Charlie', 'David')

        classes = [
            {'Alice', 'Bob'},
            {'Charlie', 'David'}
        ]

        evaluator = SolutionEvaluator(G, {})
        metrics = evaluator.evaluate_solution(classes)

        self.assertIn('gender_balance', metrics)
        for dist in metrics['gender_balance']['gender_distribution']:
            self.assertEqual(dist['male_ratio'], 0.5)

    def test_gender_balance_skewed(self):
        classes = [
            {'Alice', 'Eve'},
            {'Bob', 'Charlie', 'David', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertIn('gender_balance', metrics)
        gender_dist = metrics['gender_balance']['gender_distribution']

        class1_ratio = next(d['male_ratio'] for d in gender_dist if d['class'] == 1)
        class2_ratio = next(d['male_ratio'] for d in gender_dist if d['class'] == 2)

        self.assertEqual(class1_ratio, 0.0)
        self.assertEqual(class2_ratio, 1.0)

    def test_academic_performance_balance(self):
        classes = [
            {'Alice', 'Bob', 'Charlie'},
            {'David', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertIn('academic_balance', metrics)
        self.assertIn('academic_distribution', metrics['academic_balance'])
        self.assertIn('average_academic_deviation', metrics['academic_balance'])

    def test_behavioral_performance_balance(self):
        classes = [
            {'Alice', 'Bob', 'Charlie'},
            {'David', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertIn('behavioral_balance', metrics)
        self.assertIn('behavioral_distribution', metrics['behavioral_balance'])
        self.assertIn('average_behavioral_deviation', metrics['behavioral_balance'])

    def test_perfect_solution_score(self):
        G = nx.Graph()
        G.add_node('Alice', gender='FEMALE', academic='HIGH', behavioral='MEDIUM')
        G.add_node('Bob', gender='MALE', academic='MEDIUM', behavioral='HIGH')
        G.add_node('Charlie', gender='FEMALE', academic='LOW', behavioral='MEDIUM')
        G.add_node('David', gender='MALE', academic='MEDIUM', behavioral='MEDIUM')

        G.add_edge('Alice', 'Bob')
        G.add_edge('Charlie', 'David')

        classes = [
            {'Alice', 'Bob'},
            {'Charlie', 'David'}
        ]

        evaluator = SolutionEvaluator(G, {})
        metrics = evaluator.evaluate_solution(classes)

        self.assertGreater(metrics['overall_score'], 90.0)

    def test_hard_constraint_violation_penalties(self):
        classes = [
            {'Alice', 'David'},
            {'Bob', 'Charlie', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertLess(metrics['overall_score'], 100.0)

    def test_minimum_score_bounds(self):
        classes = [
            {'Alice'},
            {'Bob'},
            {'Charlie'},
            {'David'},
            {'Eve'},
            {'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertGreaterEqual(metrics['overall_score'], 0.0)

    def test_maximum_score_bounds(self):
        G = nx.Graph()
        G.add_node('Alice', gender='FEMALE', academic='HIGH', behavioral='MEDIUM')
        G.add_node('Bob', gender='MALE', academic='MEDIUM', behavioral='HIGH')

        G.add_edge('Alice', 'Bob')

        classes = [{'Alice', 'Bob'}]

        evaluator = SolutionEvaluator(G, {})
        metrics = evaluator.evaluate_solution(classes)

        self.assertLessEqual(metrics['overall_score'], 100.0)

    def test_overall_score_in_metrics(self):
        classes = [
            {'Alice', 'Bob', 'Charlie'},
            {'David', 'Eve', 'Frank'}
        ]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertIn('overall_score', metrics)
        self.assertIsInstance(metrics['overall_score'], float)

    def test_empty_classes(self):
        classes = []

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(len(metrics['unassigned_students']), 6)

    def test_single_class_all_students(self):
        classes = [{'Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'}]

        evaluator = SolutionEvaluator(self.G, self.not_with)
        metrics = evaluator.evaluate_solution(classes)

        self.assertEqual(len(metrics['unassigned_students']), 0)
        self.assertGreater(len(metrics['not_with_violations']), 0)


if __name__ == '__main__':
    unittest.main()
