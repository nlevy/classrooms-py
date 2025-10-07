import os
from typing import Optional
import pandas as pd

from .base_strategy import BaseAssignmentStrategy
from .greedy_strategy import GreedyStrategy
from .cp_sat_strategy import CPSATStrategy


class StrategyFactory:
    """Factory for creating assignment strategy instances"""

    AVAILABLE_STRATEGIES = {
        'greedy': GreedyStrategy,
        'cp_sat': CPSATStrategy,
        'cpsat': CPSATStrategy,  # Alias
        # Backward compatibility aliases
        'legacy': GreedyStrategy,
        'legacy_greedy': GreedyStrategy,
    }

    @classmethod
    def create_strategy(
        cls,
        strategy_name: Optional[str] = None,
        df: Optional[pd.DataFrame] = None,
        timeout_seconds: int = 30,
        **kwargs
    ) -> BaseAssignmentStrategy:
        """
        Create assignment strategy instance

        Args:
            strategy_name: Strategy to use ('greedy', 'cp_sat'). If None, uses environment variable
            df: Student data DataFrame
            timeout_seconds: Timeout for optimization strategies
            **kwargs: Additional strategy-specific parameters

        Returns:
            Strategy instance

        Raises:
            ValueError: If strategy name is invalid
            ImportError: If required dependencies are missing
        """
        if df is None:
            raise ValueError("DataFrame is required")

        # Determine strategy from parameter or environment
        if strategy_name is None:
            strategy_name = os.getenv('ASSIGNMENT_ALGORITHM', 'cp_sat')

        strategy_name = strategy_name.lower()

        if strategy_name not in cls.AVAILABLE_STRATEGIES:
            available = ', '.join(cls.AVAILABLE_STRATEGIES.keys())
            raise ValueError(f"Unknown strategy '{strategy_name}'. Available: {available}")

        strategy_class = cls.AVAILABLE_STRATEGIES[strategy_name]

        # Create strategy instance with appropriate parameters
        try:
            if strategy_name in ['cp_sat', 'cpsat']:
                return strategy_class(df, timeout_seconds=timeout_seconds, **kwargs)
            else:
                return strategy_class(df, **kwargs)
        except ImportError as e:
            fallback_strategy = os.getenv('ASSIGNMENT_FALLBACK', 'true').lower() == 'true'
            if fallback_strategy and strategy_name in ['cp_sat', 'cpsat']:
                print(f"Warning: {e}")
                print("Falling back to greedy strategy")
                return GreedyStrategy(df, **kwargs)
            else:
                raise

    @classmethod
    def get_available_strategies(cls) -> list[str]:
        """Get list of available strategy names"""
        return list(cls.AVAILABLE_STRATEGIES.keys())

    @classmethod
    def get_default_strategy(cls) -> str:
        """Get default strategy name from environment or fallback"""
        return os.getenv('ASSIGNMENT_ALGORITHM', 'cp_sat')