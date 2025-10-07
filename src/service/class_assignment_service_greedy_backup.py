from collections import defaultdict

import networkx as nx
import pandas as pd

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

    def _violates_friends(self, student, class_set):
        return sum(1 for f in self.G.neighbors(student) if f in class_set) == 0

    def _validate_assignment(self, classes):
        for i, class_set in enumerate(classes):
            for student in class_set:
                if sum(1 for f in self.G.neighbors(student) if f in class_set) == 0:
                    friends = list(self.G.neighbors(student))
                    friend_classes = [(j+1, [f for f in friends if f in c]) 
                                    for j, c in enumerate(classes)]
                    
                    # Try to move student to a class with their friends
                    for class_num, friends_in_class in friend_classes:
                        if friends_in_class:  # If there are friends in this class
                            # Remove from current class
                            classes[i].remove(student)
                            # Add to new class
                            classes[class_num-1].add(student)
                            return True
                    
                    return False
        return True

    def assign_classes(self, num_classes):
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
        scores = []
        target_size = len(self.G.nodes()) // num_classes
        
        valid_classes = []
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
        if student not in unassigned_students:
            return
        
        unassigned_students.remove(student)
        target_class.add(student)
        
        # Get all unassigned friends that can be moved
        unassigned_friends = [f for f in self.G.neighbors(student) 
                             if f in unassigned_students 
                             and not self._violates_not_with(f, target_class)]
        
        # Sort friends by:
        # 1. Number of their friends already in target class
        # 2. Number of their friends that are also friends with the main student
        friend_scores = []
        for friend in unassigned_friends:
            friends_in_class = sum(1 for f in self.G.neighbors(friend) if f in target_class)
            mutual_friends = sum(1 for f in self.G.neighbors(friend) 
                               if f in unassigned_friends and f in self.G.neighbors(student))
            friend_scores.append((friends_in_class + mutual_friends, friend))
        
        # Take up to 2 friends, prioritizing those with highest scores
        for _, friend in sorted(friend_scores, reverse=True)[:2]:
            if friend in unassigned_students:  # Double check still unassigned
                unassigned_students.remove(friend)
                target_class.add(friend)
    
    def _balance_classes(self, classes, force_balance=False):
        max_iterations = 50
        iteration = 0
        
        while iteration < max_iterations:
            max_class = max(range(len(classes)), key=lambda i: len(classes[i]))
            min_class = min(range(len(classes)), key=lambda i: len(classes[i]))
            
            if len(classes[max_class]) - len(classes[min_class]) <= 2:
                break
            
            # Find students that can be moved safely
            moveable_students = []
            for student in classes[max_class]:
                # Check if student has friends in target class
                friends_in_target = sum(1 for f in self.G.neighbors(student) 
                                      if f in classes[min_class])
                
                # Check if moving student won't isolate their friends in current class
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
    
    def _can_move_student(self, student, source_class, target_class):
        if self._violates_not_with(student, target_class):
            return False
            
        friends = set(self.G.neighbors(student))
        
        # Check if student will have friends in target class
        new_friends = friends & target_class
        if not new_friends:
            return False
            
        # Check if student will still have friends in source class
        remaining_friends = friends & (source_class - {student})
        if not remaining_friends:
            return False
            
        # Check that no student in source class will be left friendless
        for source_student in source_class - {student}:
            source_student_friends = set(self.G.neighbors(source_student))
            # If student was their only friend, can't move
            if source_student_friends & (source_class - {student}) == set() and student in source_student_friends:
                return False
                
        return True
    
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