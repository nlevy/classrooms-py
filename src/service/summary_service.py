from collections import defaultdict
from typing import List, Set, Dict, Any
from dataclasses import asdict
from .class_assignment_service import ClassAssignmentService
from src.server.dto import ClassSummaryDto

def calculate_friendless_students(service: ClassAssignmentService, class_students: Set[str]) -> int:
    count = 0
    for student in class_students:
        friends = set(service.G.neighbors(student))
        if not any(friend in class_students for friend in friends):
            count += 1
    return count

def calculate_unwanted_matches(service: ClassAssignmentService, class_students: Set[str]) -> int:
    count = 0
    for student in class_students:
        if student in service.not_with:
            unwanted = set(service.not_with[student])
            if any(other in class_students for other in unwanted):
                count += 1
    return count

def calculate_average_performance(service: ClassAssignmentService, students: Set[str], performance_type: str) -> float:
    perf_map = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
    scores = [perf_map[str(service.G.nodes[s][performance_type])] for s in students]
    return sum(scores) / len(scores) if scores else 0

def analyze_cluster_distribution(service: ClassAssignmentService, class_assignments: List[Set[str]]):
    cluster_classes = defaultdict(set)
    
    for class_idx, students in enumerate(class_assignments):
        for student in students:
            cluster_id = service.G.nodes[student]['cluster']
            cluster_classes[cluster_id].add(class_idx)
    
    total_clusters = len(cluster_classes)
    broken_clusters = sum(1 for classes in cluster_classes.values() if len(classes) > 1)
    badly_broken_clusters = sum(1 for classes in cluster_classes.values() if len(classes) > 2)
    
    return total_clusters, broken_clusters, badly_broken_clusters

def generate_class_summaries(service: ClassAssignmentService, class_assignments: List[Set[str]], 
                           original_students: List[Any]) -> Dict[str, Any]:
    classes_dict = {}
    summaries = []
    
    for i, students_set in enumerate(class_assignments):
        class_number = i + 1
        
        class_students = [s for s in original_students if s.name in students_set]
        class_students_dict = []
        for student in class_students:
            student_dict = vars(student)
            student_dict['gender'] = student.gender.value
            student_dict['academicPerformance'] = student.academicPerformance.value
            student_dict['behavioralPerformance'] = student.behavioralPerformance.value
            class_students_dict.append(student_dict)
        
        classes_dict[class_number] = class_students_dict
        
        males_count = sum(1 for s in students_set if service.G.nodes[s]['gender'] == 'MALE')
        
        summary = ClassSummaryDto(
            classNumber=class_number,
            studentsCount=len(students_set),
            malesCount=males_count,
            averageAcademicPerformance=calculate_average_performance(service, students_set, 'academic'),
            averageBehaviouralPerformance=calculate_average_performance(service, students_set, 'behavioral'),
            withoutFriends=calculate_friendless_students(service, students_set),
            unwantedMatches=calculate_unwanted_matches(service, students_set)
        )
        summaries.append(summary)
    
    return {
        "classes": classes_dict,
        "summaries": [asdict(s) for s in summaries]
    } 