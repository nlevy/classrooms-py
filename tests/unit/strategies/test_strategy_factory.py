import unittest
import os
import pandas as pd
from unittest.mock import patch
from src.service.strategies.strategy_factory import StrategyFactory
from src.service.strategies.greedy_strategy import GreedyStrategy
from src.service.strategies.cp_sat_strategy import CPSATStrategy


class TestStrategyFactory(unittest.TestCase):

    def setUp(self):
        self.sample_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'gender': ['FEMALE', 'MALE', 'MALE', 'MALE'],
            'academicPerformance': ['HIGH', 'MEDIUM', 'LOW', 'HIGH'],
            'behavioralPerformance': ['HIGH', 'MEDIUM', 'LOW', 'MEDIUM'],
            'friend1': ['Bob', 'Alice', 'David', 'Charlie'],
            'friend2': ['', '', '', ''],
            'friend3': ['', '', '', ''],
            'friend4': ['', '', '', ''],
            'notWith': ['', '', '', ''],
            'clusterId': [1, 1, 2, 2]
        })

    def test_create_greedy_strategy(self):
        strategy = StrategyFactory.create_strategy('greedy', self.sample_df)

        self.assertIsInstance(strategy, GreedyStrategy)
        self.assertEqual(strategy.name, 'greedy')

    def test_create_cp_sat_strategy(self):
        strategy = StrategyFactory.create_strategy('cp_sat', self.sample_df, timeout_seconds=20)

        self.assertIsInstance(strategy, CPSATStrategy)
        self.assertEqual(strategy.name, 'cp_sat')

    def test_create_strategy_with_alias(self):
        strategy = StrategyFactory.create_strategy('cpsat', self.sample_df)

        self.assertIsInstance(strategy, CPSATStrategy)

    def test_create_legacy_strategy(self):
        strategy = StrategyFactory.create_strategy('legacy', self.sample_df)

        self.assertIsInstance(strategy, GreedyStrategy)

    def test_invalid_strategy_name(self):
        with self.assertRaises(ValueError) as context:
            StrategyFactory.create_strategy('invalid_strategy', self.sample_df)

        self.assertIn('Unknown strategy', str(context.exception))

    def test_missing_dataframe(self):
        with self.assertRaises(ValueError) as context:
            StrategyFactory.create_strategy('greedy', df=None)

        self.assertEqual(str(context.exception), "DataFrame is required")

    def test_get_available_strategies(self):
        strategies = StrategyFactory.get_available_strategies()

        self.assertIsInstance(strategies, list)
        self.assertIn('greedy', strategies)
        self.assertIn('cp_sat', strategies)
        self.assertIn('cpsat', strategies)
        self.assertIn('legacy', strategies)

    def test_get_default_strategy_from_environment(self):
        with patch.dict(os.environ, {'ASSIGNMENT_ALGORITHM': 'greedy'}):
            default = StrategyFactory.get_default_strategy()
            self.assertEqual(default, 'greedy')

    def test_get_default_strategy_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            default = StrategyFactory.get_default_strategy()
            self.assertEqual(default, 'cp_sat')

    def test_create_strategy_from_environment(self):
        with patch.dict(os.environ, {'ASSIGNMENT_ALGORITHM': 'greedy'}):
            strategy = StrategyFactory.create_strategy(strategy_name=None, df=self.sample_df)
            self.assertIsInstance(strategy, GreedyStrategy)

    def test_case_insensitive_strategy_name(self):
        strategy = StrategyFactory.create_strategy('GREEDY', self.sample_df)
        self.assertIsInstance(strategy, GreedyStrategy)

        strategy = StrategyFactory.create_strategy('Cp_Sat', self.sample_df)
        self.assertIsInstance(strategy, CPSATStrategy)

    def test_cp_sat_with_timeout(self):
        strategy = StrategyFactory.create_strategy('cp_sat', self.sample_df, timeout_seconds=15)

        self.assertIsInstance(strategy, CPSATStrategy)
        self.assertEqual(strategy.timeout_seconds, 15)

    @patch('src.service.strategies.cp_sat_strategy.ORTOOLS_AVAILABLE', False)
    def test_cp_sat_fallback_when_ortools_missing(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            strategy = StrategyFactory.create_strategy('cp_sat', self.sample_df)

            self.assertIsInstance(strategy, GreedyStrategy)

    @patch('src.service.strategies.cp_sat_strategy.ORTOOLS_AVAILABLE', False)
    def test_cp_sat_error_when_no_fallback(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'false'}):
            with self.assertRaises(ImportError):
                StrategyFactory.create_strategy('cp_sat', self.sample_df)

    @patch('src.service.strategies.cp_sat_strategy.ORTOOLS_AVAILABLE', False)
    def test_fallback_only_for_cp_sat(self):
        with patch.dict(os.environ, {'ASSIGNMENT_FALLBACK': 'true'}):
            strategy = StrategyFactory.create_strategy('greedy', self.sample_df)
            self.assertIsInstance(strategy, GreedyStrategy)

    def test_strategy_receives_dataframe(self):
        strategy = StrategyFactory.create_strategy('greedy', self.sample_df)

        self.assertTrue(hasattr(strategy, 'df'))
        self.assertEqual(len(strategy.df), 4)

    def test_all_available_strategies_createable(self):
        for strategy_name in ['greedy', 'legacy', 'legacy_greedy']:
            strategy = StrategyFactory.create_strategy(strategy_name, self.sample_df)
            self.assertIsNotNone(strategy)


if __name__ == '__main__':
    unittest.main()
