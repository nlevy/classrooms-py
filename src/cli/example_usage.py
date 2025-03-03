import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from tabulate import tabulate
from src.service.class_assignment_service import ClassAssignmentService
from src.service.summary_service import (
    calculate_friendless_students,
    calculate_unwanted_matches,
    analyze_cluster_distribution
)

# Initialize the service with DataFrame directly
df = pd.read_csv('src/cli/inputFile/sample.csv')  
service = ClassAssignmentService(df)

# Assign students to 6 classes
num_classes = 6
class_assignments = service.assign_classes(num_classes)

# Prepare table data
table_data = []
headers = ["Class", "Students", "Males", "Females", "Avg Behavioral", "Avg Academic", "Friendless", "Unwanted"]

for i, students in enumerate(class_assignments):
    stats = service.get_class_details([students])[0]
    males = sum(1 for s in students if service.G.nodes[s]['gender'] == 'MALE')
    females = len(students) - males
    friendless = calculate_friendless_students(service, students)
    unwanted = calculate_unwanted_matches(service, students)
    
    table_data.append([
        f"Class {i+1}",
        len(students),
        males,
        females,
        f"{stats['behavioral_score']:.2f}",
        f"{stats['academic_score']:.2f}",
        friendless,
        unwanted
    ])

# Print table
print("\nClass Statistics:")
print(tabulate(table_data, headers=headers, tablefmt="grid"))

# Calculate and print cluster statistics
total_clusters, broken_clusters, badly_broken = analyze_cluster_distribution(service, class_assignments)
print("\nCluster Statistics:")
print(f"Total clusters: {total_clusters}")
print(f"Broken clusters (split into 2+ classes): {broken_clusters}")
print(f"Badly broken clusters (split into 3+ classes): {badly_broken}") 