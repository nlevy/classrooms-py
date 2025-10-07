from typing import List, Set
import pandas as pd
import networkx as nx


class InputValidationError(Exception):
    """Raised when input data is invalid"""
    pass


class InputValidator:
    """Validates student input data for assignment algorithms"""

    @staticmethod
    def validate_student_data(df: pd.DataFrame) -> None:
        """
        Validate student input data

        Raises:
            InputValidationError: If data is invalid
        """
        if df.empty:
            raise InputValidationError("Student data is empty")

        # Check required columns
        required_columns = ['name', 'gender', 'academicPerformance', 'behavioralPerformance']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise InputValidationError(f"Missing required columns: {missing_columns}")

        # Check for duplicate student names
        duplicate_names = df[df.duplicated(subset=['name'], keep=False)]['name'].tolist()
        if duplicate_names:
            raise InputValidationError(f"Duplicate student names found: {duplicate_names}")

        # Validate friendship data and find isolated students
        InputValidator._validate_friendship_network(df)

    @staticmethod
    def _validate_friendship_network(df: pd.DataFrame) -> None:
        """
        Validate friendship network - ensure no students are completely isolated

        Raises:
            InputValidationError: If students with no friends are found
        """
        G = nx.Graph()

        # Add all students as nodes
        for _, student in df.iterrows():
            G.add_node(student['name'])

        # Add friendship edges
        for _, student in df.iterrows():
            student_name = student['name']
            has_friends = False

            for i in range(1, 5):
                friend = student[f'friend{i}']
                if pd.notna(friend) and friend != '':
                    # Check if friend exists in dataset
                    if friend not in df['name'].values:
                        raise InputValidationError(
                            f"Student '{student_name}' lists unknown friend '{friend}'"
                        )
                    G.add_edge(student_name, friend)
                    has_friends = True

            if not has_friends:
                raise InputValidationError(
                    f"Student '{student_name}' has no friends listed. "
                    "All students must have at least one friend."
                )

        # Additional network analysis
        isolated_nodes = list(nx.isolates(G))
        if isolated_nodes:
            raise InputValidationError(
                f"Students with no valid friendships: {isolated_nodes}. "
                "This may be due to one-way friendships or missing friend data."
            )

    @staticmethod
    def validate_assignment_parameters(num_students: int, num_classes: int) -> None:
        """
        Validate assignment parameters

        Raises:
            InputValidationError: If parameters are invalid
        """
        if num_classes <= 0:
            raise InputValidationError("Number of classes must be positive")

        if num_students <= 0:
            raise InputValidationError("Number of students must be positive")

        if num_classes > num_students:
            raise InputValidationError(
                f"Cannot create {num_classes} classes with only {num_students} students"
            )

        min_class_size = num_students // num_classes
        if min_class_size < 1:
            raise InputValidationError(
                f"Class size too small: {min_class_size}. "
                f"Reduce number of classes or increase number of students."
            )