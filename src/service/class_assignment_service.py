import logging
import os
from collections import defaultdict
from typing import List, Set, Dict, Any, Optional

import pandas as pd

from .evaluators.solution_evaluator import SolutionEvaluator
from .strategies.strategy_factory import StrategyFactory
from .validators.input_validator import InputValidator, InputValidationError

# Configure logging
logger = logging.getLogger(__name__)

class ClassAssignmentService:
    def __init__(self, df: pd.DataFrame, strategy: Optional[str] = None, timeout_seconds: Optional[int] = None):
        """
        Initialize ClassAssignmentService with improved architecture

        Args:
            df: Student data DataFrame
            strategy: Assignment strategy ('cp_sat', 'legacy'). If None, uses environment variable
            timeout_seconds: Timeout for optimization. If None, uses environment variable
        """
        # Validate input data
        try:
            InputValidator.validate_student_data(df)
        except InputValidationError as e:
            logger.warning(f"Input validation failed: {e}")
            raise

        self.df = df

        # Get configuration from environment if not provided
        if strategy is None:
            strategy = os.getenv('ASSIGNMENT_ALGORITHM', 'cp_sat')
        if timeout_seconds is None:
            timeout_seconds = int(os.getenv('ASSIGNMENT_TIMEOUT', '30'))

        self.strategy_name = strategy
        self.timeout_seconds = timeout_seconds

        # Create strategy instance
        self.strategy = StrategyFactory.create_strategy(
            strategy_name=strategy,
            df=df,
            timeout_seconds=timeout_seconds
        )

        # Keep backward compatibility properties
        self.G = self.strategy.G
        self.not_with = self.strategy.not_with

        # Initialize evaluator
        self.evaluator = SolutionEvaluator(self.G, self.not_with)

        logger.info(f"Initialized ClassAssignmentService with strategy: {self.strategy.name}")

    def assign_classes(self, num_classes: int) -> List[Set[str]]:
        """
        Assign students to classes using the configured strategy

        Args:
            num_classes: Number of classes to create

        Returns:
            List of sets, each containing student names for a class

        Raises:
            InputValidationError: If assignment parameters are invalid
            RuntimeError: If assignment fails
        """
        try:
            # Validate assignment parameters
            InputValidator.validate_assignment_parameters(len(self.df), num_classes)

            logger.info(f"Starting assignment with {len(self.df)} students to {num_classes} classes using {self.strategy.name} strategy")

            # Execute assignment strategy with fallback handling
            result = self._execute_with_fallback(num_classes)

            # Evaluate solution quality
            evaluation = self.evaluator.evaluate_solution(result.classes)

            # Log results
            logger.info(f"Assignment completed in {result.execution_time:.2f}s")
            logger.info(f"Solution quality score: {evaluation['overall_score']:.1f}/100")

            if evaluation['students_without_friends']:
                logger.warning(f"Students without friends: {len(evaluation['students_without_friends'])}")
            if evaluation['not_with_violations']:
                logger.error(f"Not-with violations: {len(evaluation['not_with_violations'])}")

            # Store evaluation in result metadata
            result.metadata['evaluation'] = evaluation
            self._last_result = result

            return result.classes

        except Exception as e:
            logger.error(f"Assignment failed: {e}")
            raise

    def get_class_details(self, classes):
        """Get detailed information about class composition (backward compatibility)"""
        details = []
        for i, class_students in enumerate(classes):
            stats = self._calculate_class_stats(class_students)

            # Get clusters in this class
            clusters = defaultdict(list)
            for student in class_students:
                cluster_id = self.G.nodes[student]['cluster']
                clusters[cluster_id].append(student)

            # Format cluster information
            cluster_info = []
            for cluster_id, students in clusters.items():
                cluster_info.append(f"Cluster {cluster_id}: {len(students)} students")

            details.append({
                'class': i + 1,
                'size': stats['size'],
                'male_ratio': stats['male_ratio'],
                'academic_score': stats['academic_score'],
                'behavioral_score': stats['behavioral_score'],
                'clusters': cluster_info,
                'students': sorted(list(class_students))
            })
        return details

    def _calculate_class_stats(self, class_students):
        """Calculate class statistics (backward compatibility)"""
        if not class_students:
            return {'size': 0, 'male_ratio': 0, 'academic_score': 0, 'behavioral_score': 0}

        size = len(class_students)
        males = sum(1 for s in class_students if str(self.G.nodes[s]['gender']) == 'MALE')

        # Convert performance levels to scores
        perf_map = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}

        academic_scores = [perf_map[str(self.G.nodes[s]['academic'])] for s in class_students]
        behavioral_scores = [perf_map[str(self.G.nodes[s]['behavioral'])] for s in class_students]

        return {
            'size': size,
            'male_ratio': males / size if size > 0 else 0,
            'academic_score': sum(academic_scores) / size if size > 0 else 0,
            'behavioral_score': sum(behavioral_scores) / size if size > 0 else 0
        }

    def get_last_assignment_info(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about the last assignment

        Returns:
            Dictionary with assignment metadata and evaluation, or None if no assignment made
        """
        if hasattr(self, '_last_result'):
            return {
                'strategy_used': self._last_result.algorithm_used,
                'execution_time': self._last_result.execution_time,
                'metadata': self._last_result.metadata,
                'solution_quality': self._last_result.metadata.get('evaluation', {}).get('overall_score', 0)
            }
        return None

    def get_available_strategies(self) -> List[str]:
        """
        Get list of available assignment strategies

        Returns:
            List of strategy names
        """
        return StrategyFactory.get_available_strategies()

    def switch_strategy(self, strategy_name: str, timeout_seconds: Optional[int] = None) -> None:
        """
        Switch to a different assignment strategy

        Args:
            strategy_name: New strategy to use
            timeout_seconds: Timeout for new strategy (optional)
        """
        if timeout_seconds is None:
            timeout_seconds = self.timeout_seconds

        self.strategy = StrategyFactory.create_strategy(
            strategy_name=strategy_name,
            df=self.df,
            timeout_seconds=timeout_seconds
        )

        self.strategy_name = strategy_name
        self.timeout_seconds = timeout_seconds

        # Update references
        self.G = self.strategy.G
        self.not_with = self.strategy.not_with
        self.evaluator = SolutionEvaluator(self.G, self.not_with)

        logger.info(f"Switched to strategy: {strategy_name}")

    def _execute_with_fallback(self, num_classes: int):
        """Execute assignment with automatic fallback for CP-SAT failures"""
        try:
            return self.strategy.assign_classes(num_classes)
        except Exception as e:
            # Check if this is a CP-SAT strategy failure and fallback is enabled
            fallback_enabled = os.getenv('ASSIGNMENT_FALLBACK', 'true').lower() == 'true'
            is_cpsat_strategy = self.strategy.name == 'cp_sat'

            if fallback_enabled and is_cpsat_strategy:
                logger.warning(f"CP-SAT strategy failed: {e}")
                logger.warning("Falling back to greedy strategy")

                # Create greedy strategy and execute
                from .strategies.greedy_strategy import GreedyStrategy
                greedy_strategy = GreedyStrategy(self.df)
                result = greedy_strategy.assign_classes(num_classes)

                # Update result metadata to indicate fallback was used
                result.metadata['fallback_used'] = True
                result.metadata['original_strategy'] = 'cp_sat'
                result.metadata['fallback_reason'] = str(e)

                return result
            else:
                # Re-raise the original exception if no fallback
                raise