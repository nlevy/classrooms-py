from typing import List, Set, Dict, Any
import networkx as nx
from collections import defaultdict


class SolutionEvaluator:
    """Evaluates the quality of class assignment solutions"""

    def __init__(self, friendship_graph: nx.Graph, not_with_constraints: Dict[str, List[str]]):
        self.G = friendship_graph
        self.not_with = not_with_constraints

    def evaluate_solution(self, classes: List[Set[str]]) -> Dict[str, Any]:
        """
        Comprehensive evaluation of assignment solution

        Returns:
            Dictionary with quality metrics
        """
        metrics = {}

        # Hard constraint violations
        metrics.update(self._check_hard_constraints(classes))

        # Friendship metrics
        metrics.update(self._evaluate_friendships(classes))

        # Balance metrics
        metrics.update(self._evaluate_balance(classes))

        # Overall quality score
        metrics['overall_score'] = self._calculate_overall_score(metrics)

        return metrics

    def _check_hard_constraints(self, classes: List[Set[str]]) -> Dict[str, Any]:
        """Check for hard constraint violations"""
        violations = {
            'students_without_friends': [],
            'not_with_violations': [],
            'unassigned_students': [],
            'multiply_assigned_students': []
        }

        all_assigned = set()
        all_students = set(self.G.nodes())

        # Check assignment completeness
        for class_set in classes:
            for student in class_set:
                if student in all_assigned:
                    violations['multiply_assigned_students'].append(student)
                all_assigned.add(student)

        violations['unassigned_students'] = list(all_students - all_assigned)

        # Check friendship requirements
        for i, class_set in enumerate(classes):
            for student in class_set:
                friends_in_class = [f for f in self.G.neighbors(student) if f in class_set]
                if not friends_in_class:
                    violations['students_without_friends'].append({
                        'student': student,
                        'class': i + 1
                    })

        # Check not-with constraints
        for i, class_set in enumerate(classes):
            for student in class_set:
                if student in self.not_with:
                    unwanted_in_class = [other for other in self.not_with[student] if other in class_set]
                    if unwanted_in_class:
                        violations['not_with_violations'].append({
                            'student': student,
                            'unwanted_classmates': unwanted_in_class,
                            'class': i + 1
                        })

        return violations

    def _evaluate_friendships(self, classes: List[Set[str]]) -> Dict[str, Any]:
        """Evaluate friendship satisfaction"""
        total_friendships = 0
        satisfied_friendships = 0
        friendship_distribution = []

        for i, class_set in enumerate(classes):
            class_friendships = 0
            for student in class_set:
                student_friends = list(self.G.neighbors(student))
                friends_in_class = [f for f in student_friends if f in class_set]

                total_friendships += len(student_friends)
                satisfied_friendships += len(friends_in_class)
                class_friendships += len(friends_in_class)

            friendship_distribution.append({
                'class': i + 1,
                'total_friendships_in_class': class_friendships // 2,  # Avoid double counting
                'avg_friends_per_student': class_friendships / len(class_set) if class_set else 0
            })

        return {
            'friendship_satisfaction_rate': satisfied_friendships / total_friendships if total_friendships > 0 else 0,
            'total_satisfied_friendships': satisfied_friendships,
            'total_possible_friendships': total_friendships,
            'friendship_distribution': friendship_distribution
        }

    def _evaluate_balance(self, classes: List[Set[str]]) -> Dict[str, Any]:
        """Evaluate class balance metrics"""
        balance_metrics = {
            'size_balance': self._evaluate_size_balance(classes),
            'gender_balance': self._evaluate_gender_balance(classes),
            'academic_balance': self._evaluate_performance_balance(classes, 'academic'),
            'behavioral_balance': self._evaluate_performance_balance(classes, 'behavioral')
        }

        return balance_metrics

    def _evaluate_size_balance(self, classes: List[Set[str]]) -> Dict[str, Any]:
        """Evaluate class size balance"""
        sizes = [len(class_set) for class_set in classes]
        if not sizes:
            return {'size_variance': 0, 'max_size_difference': 0, 'size_distribution': []}

        return {
            'size_variance': max(sizes) - min(sizes),
            'max_size_difference': max(sizes) - min(sizes),
            'size_distribution': [{'class': i + 1, 'size': size} for i, size in enumerate(sizes)],
            'average_size': sum(sizes) / len(sizes)
        }

    def _evaluate_gender_balance(self, classes: List[Set[str]]) -> Dict[str, Any]:
        """Evaluate gender balance across classes"""
        gender_balance = []

        for i, class_set in enumerate(classes):
            if not class_set:
                continue

            males = sum(1 for s in class_set if str(self.G.nodes[s]['gender']) == 'MALE')
            total = len(class_set)
            male_ratio = males / total

            gender_balance.append({
                'class': i + 1,
                'male_count': males,
                'female_count': total - males,
                'male_ratio': male_ratio,
                'balance_deviation': abs(0.5 - male_ratio)
            })

        avg_deviation = sum(item['balance_deviation'] for item in gender_balance) / len(gender_balance) if gender_balance else 0

        return {
            'gender_distribution': gender_balance,
            'average_gender_deviation': avg_deviation
        }

    def _evaluate_performance_balance(self, classes: List[Set[str]], performance_type: str) -> Dict[str, Any]:
        """Evaluate academic or behavioral performance balance"""
        perf_map = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        performance_balance = []

        for i, class_set in enumerate(classes):
            if not class_set:
                continue

            scores = [perf_map[self.G.nodes[s][performance_type]] for s in class_set]
            avg_score = sum(scores) / len(scores)

            performance_balance.append({
                'class': i + 1,
                'average_score': avg_score,
                'score_distribution': {
                    'LOW': scores.count(1),
                    'MEDIUM': scores.count(2),
                    'HIGH': scores.count(3)
                }
            })

        target_score = 2.0  # Target average (balanced)
        avg_deviation = sum(abs(item['average_score'] - target_score) for item in performance_balance) / len(performance_balance) if performance_balance else 0

        return {
            f'{performance_type}_distribution': performance_balance,
            f'average_{performance_type}_deviation': avg_deviation
        }

    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall solution quality score (0-100)"""
        score = 100.0

        # Heavy penalties for hard constraint violations
        if metrics['students_without_friends']:
            score -= len(metrics['students_without_friends']) * 20

        if metrics['not_with_violations']:
            score -= len(metrics['not_with_violations']) * 25

        if metrics['unassigned_students']:
            score -= len(metrics['unassigned_students']) * 30

        if metrics['multiply_assigned_students']:
            score -= len(metrics['multiply_assigned_students']) * 30

        # Moderate penalties for soft constraint issues
        if 'size_balance' in metrics:
            score -= metrics['size_balance']['size_variance'] * 2

        if 'gender_balance' in metrics:
            score -= metrics['gender_balance']['average_gender_deviation'] * 10

        if 'academic_balance' in metrics:
            score -= metrics['academic_balance']['average_academic_deviation'] * 5

        if 'behavioral_balance' in metrics:
            score -= metrics['behavioral_balance']['average_behavioral_deviation'] * 5

        # Bonus for high friendship satisfaction
        if 'friendship_satisfaction_rate' in metrics:
            score += metrics['friendship_satisfaction_rate'] * 10

        return max(0, min(100, score))