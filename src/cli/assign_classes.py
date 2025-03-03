import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from tabulate import tabulate
from src.service.class_assignment_service import ClassAssignmentService
from src.service.summary_service import (
    calculate_friendless_students,
    calculate_unwanted_matches,
    analyze_cluster_distribution
)

def parse_args():
    parser = argparse.ArgumentParser(description='Assign students to classes based on various constraints')
    parser.add_argument('-csv', '--csv_path', 
                        type=str, 
                        required=True,
                        help='Path to the CSV file containing student data')
    parser.add_argument('-classes', '--num_classes', 
                        type=int, 
                        required=True,
                        help='Number of classes to create')
    return parser.parse_args()

def display_results(service, class_assignments):
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

def main():
    args = parse_args()
    
    try:
        # Load data
        df = pd.read_csv(args.csv_path)
        
        # Initialize service and assign classes
        service = ClassAssignmentService(df)
        class_assignments = service.assign_classes(args.num_classes)
        
        # Display results
        display_results(service, class_assignments)
        
    except FileNotFoundError:
        print(f"Error: Could not find CSV file at {args.csv_path}")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: The CSV file at {args.csv_path} is empty")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 