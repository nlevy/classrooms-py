from typing import Dict, Any, Optional

import networkx as nx
import pandas as pd

from src.server.error_codes import ErrorCode, ErrorResponse


class InputValidationError(Exception):
    """Raised when input data is invalid"""

    def __init__(
        self,
        code: ErrorCode,
        params: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ):
        """
        Create validation error with error code and parameters

        Args:
            code: Error code for client-side translation
            params: Parameters to substitute in translated message
            message: Human-readable message for debugging (optional)
        """
        self.code = code
        self.params = params or {}
        self.message = message or code.value
        super().__init__(self.message)

    def to_response(self) -> ErrorResponse:
        """Convert to structured error response"""
        return ErrorResponse(self.code, self.params, self.message)


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
            raise InputValidationError(
                code=ErrorCode.EMPTY_STUDENT_DATA,
                params={"count": 0},
                message="Student data is empty"
            )

        # Check required columns
        required_columns = ['name', 'gender', 'academicPerformance', 'behavioralPerformance']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise InputValidationError(
                code=ErrorCode.MISSING_REQUIRED_FIELDS,
                params={"fields": missing_columns},
                message=f"Missing required columns: {missing_columns}"
            )

        # Check for duplicate student names
        duplicate_names = df[df.duplicated(subset=['name'], keep=False)]['name'].tolist()
        if duplicate_names:
            raise InputValidationError(
                code=ErrorCode.DUPLICATE_STUDENT_NAMES,
                params={"duplicates": duplicate_names},
                message=f"Duplicate student names found: {duplicate_names}"
            )

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
                            code=ErrorCode.UNKNOWN_FRIEND,
                            params={"studentName": student_name, "friendName": friend},
                            message=f"Student '{student_name}' lists unknown friend '{friend}'"
                        )
                    G.add_edge(student_name, friend)
                    has_friends = True

            if not has_friends:
                raise InputValidationError(
                    code=ErrorCode.STUDENT_NO_FRIENDS,
                    params={"studentName": student_name},
                    message=f"Student '{student_name}' has no friends listed"
                )

        # Additional network analysis
        isolated_nodes = list(nx.isolates(G))
        if isolated_nodes:
            raise InputValidationError(
                code=ErrorCode.ISOLATED_STUDENTS,
                params={"students": isolated_nodes},
                message=f"Students with no valid friendships: {isolated_nodes}"
            )

    @staticmethod
    def validate_assignment_parameters(num_students: int, num_classes: int) -> None:
        """
        Validate assignment parameters

        Raises:
            InputValidationError: If parameters are invalid
        """
        if num_classes <= 0:
            raise InputValidationError(
                code=ErrorCode.INVALID_CLASS_COUNT,
                params={"classCount": num_classes},
                message="Number of classes must be positive"
            )

        if num_students <= 0:
            raise InputValidationError(
                code=ErrorCode.INVALID_STUDENT_COUNT,
                params={"studentCount": num_students},
                message="Number of students must be positive"
            )

        if num_classes > num_students:
            raise InputValidationError(
                code=ErrorCode.TOO_MANY_CLASSES,
                params={"classCount": num_classes, "studentCount": num_students},
                message=f"Cannot create {num_classes} classes with only {num_students} students"
            )

        min_class_size = num_students // num_classes
        if min_class_size < 1:
            raise InputValidationError(
                code=ErrorCode.CLASS_SIZE_TOO_SMALL,
                params={"minSize": min_class_size, "classCount": num_classes, "studentCount": num_students},
                message=f"Class size too small: {min_class_size}"
            )