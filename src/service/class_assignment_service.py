import pandas as pd
import networkx as nx
from collections import defaultdict
import random

class ClassAssignmentService:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.G = self._build_friendship_graph()
        self.not_with = self._build_not_with_dict()
        
    def _build_friendship_graph(self):
        # Create graph where nodes are students and edges represent friendships
        G = nx.Graph()
        
        for _, student in self.df.iterrows():
            # Convert gender and performance values to strings
            gender = str(student['gender'])  # Handle both string and enum cases
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
                if pd.notna(friend):
                    G.add_edge(student['name'], friend)
                    
        return G
    
    def _build_not_with_dict(self):
        not_with = {}
        for _, student in self.df.iterrows():
            if pd.notna(student['notWith']):
                not_with[student['name']] = student['notWith'].split(',')
        return not_with

    def _violates_not_with(self, student, class_set):
        if student not in self.not_with:
            return False
        return any(other in class_set for other in self.not_with[student])

    def assign_classes(self, num_classes):
        # Initialize classes
        classes = [set() for _ in range(num_classes)]
        unassigned_students = set(self.G.nodes())
        
        # First pass: try to assign students with their friends
        while unassigned_students:
            student = max(unassigned_students, 
                        key=lambda s: sum(1 for f in self.G.neighbors(s) if f in unassigned_students))
            
            best_class = self._find_best_class(student, classes, num_classes)
            self._assign_student_group(student, unassigned_students, classes[best_class])
            
            # More aggressive balancing
            if max(len(c) for c in classes) - min(len(c) for c in classes) > 1:
                self._balance_classes(classes, force_balance=True)
        
        return classes
    
    def _find_best_class(self, student, classes, num_classes):
        scores = []
        target_size = len(self.G.nodes()) // num_classes
        
        for i, class_set in enumerate(classes):
            # Check not_with constraint
            if self._violates_not_with(student, class_set):
                scores.append((float('inf'), i))
                continue
                
            # Stronger size penalty but not as dominant
            size_penalty = 2 * abs(len(class_set) - target_size)
            
            # Increased friend bonus - make it more important
            friend_bonus = 4 * sum(1 for f in self.G.neighbors(student) if f in class_set)
            
            # Gender balance
            current_male_ratio = self._calculate_class_stats(class_set)['male_ratio']
            gender_balance = abs(0.5 - current_male_ratio)
            
            # Performance balance
            perf_stats = self._calculate_class_stats(class_set)
            perf_balance = abs(2 - perf_stats['academic_score']) + abs(2 - perf_stats['behavioral_score'])
            
            # Combined score (lower is better)
            score = size_penalty - friend_bonus + gender_balance + perf_balance
            scores.append((score, i))
        
        return min(scores, key=lambda x: x[0])[1]
    
    def _assign_student_group(self, student, unassigned_students, target_class):
        if student in unassigned_students:
            unassigned_students.remove(student)
            target_class.add(student)
            
            # Try to assign more friends together (increased from 1 to 3)
            unassigned_friends = [f for f in self.G.neighbors(student) 
                                if f in unassigned_students and not self._violates_not_with(f, target_class)]
            # Take up to 3 friends to assign together
            for friend in sorted(unassigned_friends, 
                              key=lambda f: sum(1 for ff in self.G.neighbors(f) 
                                              if ff in target_class or ff in unassigned_friends),
                              reverse=True)[:3]:
                unassigned_students.remove(friend)
                target_class.add(friend)
    
    def _balance_classes(self, classes, force_balance=False):
        max_iterations = 100
        iteration = 0
        
        while iteration < max_iterations:
            max_class = max(range(len(classes)), key=lambda i: len(classes[i]))
            min_class = min(range(len(classes)), key=lambda i: len(classes[i]))
            
            if len(classes[max_class]) - len(classes[min_class]) <= 2:  # Increased tolerance
                break
            
            # Try to move students from largest to smallest class
            moved = False
            # Sort students by number of friends in target class
            students_to_try = sorted(classes[max_class],
                                   key=lambda s: len(set(self.G.neighbors(s)) & classes[min_class]),
                                   reverse=True)
            
            for student in students_to_try:
                if force_balance or self._can_move_student(student, classes[max_class], classes[min_class]):
                    classes[max_class].remove(student)
                    classes[min_class].add(student)
                    moved = True
                    break
            
            if not moved:
                break
            
            iteration += 1
    
    def _can_move_student(self, student, source_class, target_class):
        if self._violates_not_with(student, target_class):
            return False
            
        friends = set(self.G.neighbors(student))
        
        # Make friend requirements stricter
        remaining_friends = friends & (source_class - {student})
        new_friends = friends & target_class
        
        # Require at least one friend in target class
        if not new_friends:
            return False
            
        # Allow move only if student will still have friends in both classes
        return bool(remaining_friends)
    
    def _calculate_class_stats(self, class_students):
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
    
    def get_class_details(self, classes):
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