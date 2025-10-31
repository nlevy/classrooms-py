from enum import Enum
from typing import Dict, Any, Optional


class ErrorCode(str, Enum):
    """Error codes for client-side translation"""

    # Request validation errors (4xx)
    INVALID_CONTENT_TYPE = "INVALID_CONTENT_TYPE"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_STUDENT_DATA = "INVALID_STUDENT_DATA"

    # Student data validation errors
    EMPTY_STUDENT_DATA = "EMPTY_STUDENT_DATA"
    MISSING_REQUIRED_FIELDS = "MISSING_REQUIRED_FIELDS"
    DUPLICATE_STUDENT_NAMES = "DUPLICATE_STUDENT_NAMES"

    # Friendship validation errors
    STUDENT_NO_FRIENDS = "STUDENT_NO_FRIENDS"
    UNKNOWN_FRIEND = "UNKNOWN_FRIEND"
    ISOLATED_STUDENTS = "ISOLATED_STUDENTS"

    # Assignment parameter validation errors
    INVALID_CLASS_COUNT = "INVALID_CLASS_COUNT"
    INVALID_STUDENT_COUNT = "INVALID_STUDENT_COUNT"
    TOO_MANY_CLASSES = "TOO_MANY_CLASSES"
    CLASS_SIZE_TOO_SMALL = "CLASS_SIZE_TOO_SMALL"

    # Assignment execution errors (422)
    ASSIGNMENT_FAILED = "ASSIGNMENT_FAILED"
    NO_SOLUTION_FOUND = "NO_SOLUTION_FOUND"
    OPTIMIZATION_TIMEOUT = "OPTIMIZATION_TIMEOUT"

    # System errors (5xx)
    UNSUPPORTED_LANGUAGE = "UNSUPPORTED_LANGUAGE"
    TEMPLATE_NOT_AVAILABLE = "TEMPLATE_NOT_AVAILABLE"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class ErrorResponse:
    """Structured error response builder for client-side translation"""

    def __init__(
        self,
        code: ErrorCode,
        params: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ):
        """
        Create an error response

        Args:
            code: Error code for client-side translation lookup
            params: Parameters to substitute in translated message
            message: Human-readable message for debugging (optional, defaults to code value)
        """
        self.code = code
        self.params = params or {}
        self.message = message or code.value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to JSON-serializable dict

        Returns:
            Dict with error code, params, and debug message
        """
        return {
            "error": {
                "code": self.code.value,
                "params": self.params,
                "message": self.message  # For debugging/logging
            }
        }

    def to_tuple(self, status_code: int):
        """
        Return tuple for Flask jsonify response

        Args:
            status_code: HTTP status code

        Returns:
            Tuple of (dict, status_code) for Flask response
        """
        return self.to_dict(), status_code
