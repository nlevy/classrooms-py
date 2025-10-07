from abc import ABC, abstractmethod
from typing import List, Set, Dict, Any
import pandas as pd
import networkx as nx


class AssignmentResult:
    """Wrapper for assignment results with metadata"""
    def __init__(self, classes: List[Set[str]], metadata: Dict[str, Any] = None):
        self.classes = classes
        self.metadata = metadata or {}
        self.algorithm_used = metadata.get('algorithm', 'unknown')
        self.execution_time = metadata.get('execution_time', 0)
        self.solution_quality = metadata.get('solution_quality', 0)


class BaseAssignmentStrategy(ABC):
    """Abstract base class for student assignment strategies"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.G = self._build_friendship_graph()
        self.not_with = self._build_not_with_dict()

    def _build_friendship_graph(self) -> nx.Graph:
        """Build friendship network graph"""
        G = nx.Graph()

        for _, student in self.df.iterrows():
            # Convert gender and performance values to strings
            gender = str(student['gender'])
            academic = str(student['academicPerformance'])
            behavioral = str(student['behavioralPerformance'])

            G.add_node(student['name'],
                      gender=gender,
                      academic=academic,
                      behavioral=behavioral,
                      cluster=student['clusterId'])

            # Add friendship edges
            for i in range(1, 5):
                friend = student[f'friend{i}']
                if pd.notna(friend) and friend.strip() != '':
                    G.add_edge(student['name'], friend)

        return G

    def _build_not_with_dict(self) -> Dict[str, List[str]]:
        """Build not-with constraints dictionary"""
        not_with = {}
        for _, student in self.df.iterrows():
            if pd.notna(student['notWith']):
                not_with[student['name']] = student['notWith'].split(',')
        return not_with

    @abstractmethod
    def assign_classes(self, num_classes: int) -> AssignmentResult:
        """
        Assign students to classes

        Args:
            num_classes: Number of classes to create

        Returns:
            AssignmentResult with classes and metadata
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name for logging/debugging"""
        pass

    @property
    @abstractmethod
    def supports_timeout(self) -> bool:
        """Whether this strategy supports timeout configuration"""
        pass