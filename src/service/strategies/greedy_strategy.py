import time
from typing import List, Set
from .base_strategy import BaseAssignmentStrategy, AssignmentResult


class GreedyStrategy(BaseAssignmentStrategy):
    """
    Greedy assignment strategy - fast graph-based assignment algorithm
    """

    @property
    def name(self) -> str:
        return "greedy"

    @property
    def supports_timeout(self) -> bool:
        return False

    def assign_classes(self, num_classes: int) -> AssignmentResult:
        """Execute the greedy assignment algorithm"""
        start_time = time.time()

        # Execute greedy algorithm logic
        classes = self._greedy_assign_classes(num_classes)

        execution_time = time.time() - start_time

        metadata = {
            'algorithm': self.name,
            'execution_time': execution_time,
            'num_classes': num_classes,
            'num_students': len(self.G.nodes())
        }

        return AssignmentResult(classes, metadata)

    def _greedy_assign_classes(self, num_classes: int) -> List[Set[str]]:
        """Greedy assignment algorithm logic"""
        classes = [set() for _ in range(num_classes)]
        unassigned_students = set(self.G.nodes())

        while unassigned_students:
            student = min(unassigned_students,
                         key=lambda s: (sum(1 for f in self.G.neighbors(s)
                                          if f in unassigned_students),
                                      len(list(self.G.neighbors(s)))))

            best_class = self._find_best_class(student, classes, num_classes)
            self._assign_student_group(student, unassigned_students, classes[best_class])

            if max(len(c) for c in classes) - min(len(c) for c in classes) > 1:
                self._balance_classes(classes, force_balance=True)

        if not self._validate_assignment(classes):
            print("Warning - Final assignment has students without friends in their classes")

        return classes

    def _find_best_class(self, student, classes, num_classes):
        """Find best class for student (original logic)"""
        scores = []
        target_size = len(self.G.nodes()) // num_classes

        for i, class_set in enumerate(classes):
            if self._violates_not_with(student, class_set):
                continue

            friends_in_class = sum(1 for f in self.G.neighbors(student) if f in class_set)

            if friends_in_class == 0:
                continue

            size_penalty = 2 * abs(len(class_set) - target_size)
            friend_bonus = 4 * friends_in_class

            current_male_ratio = self._calculate_class_stats(class_set)['male_ratio']
            gender_balance = abs(0.5 - current_male_ratio)

            perf_stats = self._calculate_class_stats(class_set)
            perf_balance = abs(2 - perf_stats['academic_score']) + abs(2 - perf_stats['behavioral_score'])

            score = size_penalty - friend_bonus + gender_balance + perf_balance
            scores.append((score, i))

        if not scores:
            scores = [(-(sum(1 for f in self.G.neighbors(student)
                           if f not in class_set)), i)
                     for i, class_set in enumerate(classes)]

        best_class = min(scores, key=lambda x: x[0])[1]
        return best_class

    def _assign_student_group(self, student, unassigned_students, target_class):
        """Assign student and friends to class (original logic)"""
        if student not in unassigned_students:
            return

        unassigned_students.remove(student)
        target_class.add(student)

        unassigned_friends = [f for f in self.G.neighbors(student)
                             if f in unassigned_students
                             and not self._violates_not_with(f, target_class)]

        friend_scores = []
        for friend in unassigned_friends:
            friends_in_class = sum(1 for f in self.G.neighbors(friend) if f in target_class)
            mutual_friends = sum(1 for f in self.G.neighbors(friend)
                               if f in unassigned_friends and f in self.G.neighbors(student))
            friend_scores.append((friends_in_class + mutual_friends, friend))

        for _, friend in sorted(friend_scores, reverse=True)[:2]:
            if friend in unassigned_students:
                unassigned_students.remove(friend)
                target_class.add(friend)

    def _balance_classes(self, classes, force_balance=False):
        """Balance class sizes (original logic)"""
        max_iterations = 50
        iteration = 0

        while iteration < max_iterations:
            max_class = max(range(len(classes)), key=lambda i: len(classes[i]))
            min_class = min(range(len(classes)), key=lambda i: len(classes[i]))

            if len(classes[max_class]) - len(classes[min_class]) <= 2:
                break

            moveable_students = []
            for student in classes[max_class]:
                friends_in_target = sum(1 for f in self.G.neighbors(student)
                                      if f in classes[min_class])

                safe_to_move = True
                for friend in self.G.neighbors(student):
                    if friend in classes[max_class]:
                        other_friends = sum(1 for f in self.G.neighbors(friend)
                                          if f in classes[max_class] and f != student)
                        if other_friends == 0:
                            safe_to_move = False
                            break

                if (friends_in_target > 0 or force_balance) and (safe_to_move or force_balance):
                    moveable_students.append((friends_in_target, student))

            if not moveable_students:
                break

            _, student_to_move = max(moveable_students)
            classes[max_class].remove(student_to_move)
            classes[min_class].add(student_to_move)

            iteration += 1

    def _violates_not_with(self, student, class_set):
        """Check not-with constraint violations"""
        if student not in self.not_with:
            return False
        return any(other in class_set for other in self.not_with[student])

    def _validate_assignment(self, classes):
        """Validate assignment quality"""
        for i, class_set in enumerate(classes):
            for student in class_set:
                if sum(1 for f in self.G.neighbors(student) if f in class_set) == 0:
                    friends = list(self.G.neighbors(student))
                    friend_classes = [(j+1, [f for f in friends if f in c])
                                    for j, c in enumerate(classes)]

                    for class_num, friends_in_class in friend_classes:
                        if friends_in_class:
                            classes[i].remove(student)
                            classes[class_num-1].add(student)
                            return True

                    return False
        return True

    def _calculate_class_stats(self, class_students):
        """Calculate class statistics"""
        if not class_students:
            return {'size': 0, 'male_ratio': 0, 'academic_score': 0, 'behavioral_score': 0}

        size = len(class_students)
        males = sum(1 for s in class_students if str(self.G.nodes[s]['gender']) == 'MALE')

        perf_map = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}

        academic_scores = [perf_map[str(self.G.nodes[s]['academic'])] for s in class_students]
        behavioral_scores = [perf_map[str(self.G.nodes[s]['behavioral'])] for s in class_students]

        return {
            'size': size,
            'male_ratio': males / size if size > 0 else 0,
            'academic_score': sum(academic_scores) / size if size > 0 else 0,
            'behavioral_score': sum(behavioral_scores) / size if size > 0 else 0
        }