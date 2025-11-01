import unittest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from src.service.class_assignment_service import ClassAssignmentService


class TestStrategyFallback(unittest.TestCase):

    def setUp(self):
        self.sample_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'behavioralPerformance': ['MEDIUM', 'HIGH', 'MEDIUM', 'LOW'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie'],
            'friend2': ['Charlie', 'David', 'Alice', 'Bob'],
            'friend3': ['', '', '', ''],
            'friend4': ['', '', '', ''],
            'notWith': ['', '', '', ''],
            'clusterId': [1, 1, 2, 2]
        })

    @patch('src.service.strategies.cp_sat_strategy.ORTOOLS_AVAILABLE', False)
    def test_fallback_on_ortools_import_failure(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            service = ClassAssignmentService(self.sample_df, strategy='cp_sat')

            self.assertEqual(service.strategy.name, 'greedy')

    def test_fallback_metadata_complete(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)

            with patch.object(service.strategy, 'assign_classes', side_effect=RuntimeError("CP-SAT failed")):
                classes = service.assign_classes(2)

                info = service.get_last_assignment_info()

                self.assertTrue(info['metadata'].get('fallback_used', False))
                self.assertEqual(info['metadata'].get('original_strategy'), 'cp_sat')
                self.assertIn('fallback_reason', info['metadata'])

    def test_fallback_disabled_raises_error(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'false'}):
            service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)

            with patch.object(service.strategy, 'assign_classes', side_effect=RuntimeError("CP-SAT failed")):
                with self.assertRaises(RuntimeError):
                    service.assign_classes(2)

    def test_no_fallback_for_greedy_failures(self):
        service = ClassAssignmentService(self.sample_df, strategy='greedy')

        with patch.object(service.strategy, 'assign_classes', side_effect=RuntimeError("Greedy failed")):
            with self.assertRaises(RuntimeError):
                service.assign_classes(2)

    def test_fallback_produces_valid_assignment(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)

            with patch.object(service.strategy, 'assign_classes', side_effect=RuntimeError("CP-SAT timeout")):
                classes = service.assign_classes(2)

                self.assertEqual(len(classes), 2)

                all_students = set()
                for class_set in classes:
                    all_students.update(class_set)

                self.assertEqual(len(all_students), 4)

    def test_fallback_preserves_solution_quality(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)

            with patch.object(service.strategy, 'assign_classes', side_effect=RuntimeError("CP-SAT failed")):
                classes = service.assign_classes(2)

                info = service.get_last_assignment_info()

                self.assertIn('solution_quality', info)
                self.assertGreater(info['solution_quality'], 0)

    def test_successful_cp_sat_no_fallback(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)

            classes = service.assign_classes(2)

            info = service.get_last_assignment_info()

            if info['strategy_used'] == 'cp_sat':
                self.assertFalse(info['metadata'].get('fallback_used', False))

    def test_fallback_tracks_original_strategy(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)

            with patch.object(service.strategy, 'assign_classes', side_effect=RuntimeError("Failed")):
                classes = service.assign_classes(2)

                info = service.get_last_assignment_info()

                self.assertEqual(info['metadata'].get('original_strategy'), 'cp_sat')
                self.assertEqual(info['strategy_used'], 'greedy')

    def test_fallback_environment_variable_default(self):
        with patch.dict(os.environ, {}, clear=True):
            service = ClassAssignmentService(self.sample_df, strategy='cp_sat', timeout_seconds=10)

            with patch.object(service.strategy, 'assign_classes', side_effect=RuntimeError("Failed")):
                classes = service.assign_classes(2)

                info = service.get_last_assignment_info()
                self.assertTrue(info['metadata'].get('fallback_used', False))


if __name__ == '__main__':
    unittest.main()
