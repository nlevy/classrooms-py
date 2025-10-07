import time
from typing import List, Set, Dict, Any
try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    cp_model = None

from .base_strategy import BaseAssignmentStrategy, AssignmentResult


class CPSATStrategy(BaseAssignmentStrategy):
    """
    CP-SAT strategy with simplified, working constraints
    """

    def __init__(self, df, timeout_seconds: int = 30):
        super().__init__(df)
        self.timeout_seconds = timeout_seconds

        if not ORTOOLS_AVAILABLE:
            raise ImportError(
                "Google OR-Tools is required for CP-SAT strategy. "
                "Install with: pip install ortools"
            )

    @property
    def name(self) -> str:
        return "cp_sat"

    @property
    def supports_timeout(self) -> bool:
        return True

    def assign_classes(self, num_classes: int) -> AssignmentResult:
        """Execute CP-SAT based assignment with simplified model"""
        start_time = time.time()

        try:
            classes, solver_stats = self._solve_with_simple_cpsat(num_classes)
            execution_time = time.time() - start_time

            metadata = {
                'algorithm': self.name,
                'execution_time': execution_time,
                'solver_status': solver_stats['status'],
                'solver_time': solver_stats['solve_time'],
                'num_classes': num_classes,
                'num_students': len(self.G.nodes()),
                'timeout_used': self.timeout_seconds
            }

            return AssignmentResult(classes, metadata)

        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"CP-SAT assignment failed after {execution_time:.2f}s: {str(e)}")

    def _solve_with_simple_cpsat(self, num_classes: int) -> tuple[List[Set[str]], Dict[str, Any]]:
        """Solve with simplified CP-SAT model focusing on core constraints"""
        model = cp_model.CpModel()

        students = list(self.G.nodes())
        num_students = len(students)
        student_indices = {student: i for i, student in enumerate(students)}

        # Decision variables: x[student][class] = 1 if student assigned to class
        x = {}
        for s_idx, student in enumerate(students):
            x[s_idx] = {}
            for c in range(num_classes):
                x[s_idx][c] = model.NewBoolVar(f'x_{student}_{c}')

        # HARD CONSTRAINT 1: Each student assigned to exactly one class
        for s_idx in range(num_students):
            model.Add(sum(x[s_idx][c] for c in range(num_classes)) == 1)

        # HARD CONSTRAINT 2: Each student must have at least one friend in their class
        for s_idx, student in enumerate(students):
            friends = list(self.G.neighbors(student))
            if not friends:
                raise ValueError(f"Student {student} has no friends - invalid input data")

            friend_indices = [student_indices[f] for f in friends if f in student_indices]

            # For each class, if student is in that class, at least one friend must be too
            for c in range(num_classes):
                friends_in_same_class = [x[f_idx][c] for f_idx in friend_indices]
                if friends_in_same_class:
                    # If student is in class c, then sum of friends in class c >= 1
                    model.Add(sum(friends_in_same_class) >= x[s_idx][c])

        # HARD CONSTRAINT 3: Not-with restrictions
        for student, forbidden_list in self.not_with.items():
            if student not in student_indices:
                continue
            s_idx = student_indices[student]

            for forbidden in forbidden_list:
                if forbidden not in student_indices:
                    continue
                f_idx = student_indices[forbidden]

                # Students cannot be in the same class
                for c in range(num_classes):
                    model.Add(x[s_idx][c] + x[f_idx][c] <= 1)

        # SOFT CONSTRAINT: Balanced class sizes
        target_size = num_students // num_classes
        min_size = target_size - 1 if target_size > 1 else 1
        max_size = target_size + 2

        for c in range(num_classes):
            class_size = sum(x[s_idx][c] for s_idx in range(num_students))
            model.Add(class_size >= min_size)
            model.Add(class_size <= max_size)

        # OBJECTIVE: Maximize total friendships within classes
        friendship_vars = []
        for s_idx, student in enumerate(students):
            friends = list(self.G.neighbors(student))
            friend_indices = [student_indices[f] for f in friends if f in student_indices]

            for f_idx in friend_indices:
                if f_idx > s_idx:  # Avoid counting each friendship twice
                    for c in range(num_classes):
                        # Create variable: both student and friend in same class
                        friendship_var = model.NewBoolVar(f'friendship_{s_idx}_{f_idx}_{c}')
                        # friendship_var = 1 iff both are in class c
                        model.Add(friendship_var <= x[s_idx][c])
                        model.Add(friendship_var <= x[f_idx][c])
                        model.Add(friendship_var >= x[s_idx][c] + x[f_idx][c] - 1)
                        friendship_vars.append(friendship_var)

        # Maximize total friendships
        model.Maximize(sum(friendship_vars))

        # Solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.timeout_seconds
        solver.parameters.log_search_progress = False

        solve_start = time.time()
        status = solver.Solve(model)
        solve_time = time.time() - solve_start

        # Process results
        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            raise RuntimeError(f"CP-SAT solver failed with status: {solver.StatusName(status)}")

        # Extract solution
        classes = [set() for _ in range(num_classes)]
        for s_idx, student in enumerate(students):
            for c in range(num_classes):
                if solver.Value(x[s_idx][c]) == 1:
                    classes[c].add(student)
                    break

        solver_stats = {
            'status': solver.StatusName(status),
            'solve_time': solve_time,
            'objective_value': solver.ObjectiveValue() if status == cp_model.OPTIMAL else solver.BestObjectiveBound(),
            'num_variables': len([v for v in model.Proto().variables]),
            'num_constraints': len([c for c in model.Proto().constraints])
        }

        return classes, solver_stats