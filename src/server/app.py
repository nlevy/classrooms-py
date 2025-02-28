from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from typing import List
import pandas as pd
import logging
import json
import os
from .dto import StudentDto
from src.service.class_assignment_service import ClassAssignmentService
from src.service.summary_service import generate_class_summaries

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Load template at startup
try:
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'template.json')
    with open(template_path, 'r') as f:
        TEMPLATE = json.load(f)
except Exception as e:
    logging.error(f"Failed to load template at startup: {str(e)}")
    TEMPLATE = None

def create_dataframe(students: List[StudentDto]) -> pd.DataFrame:
    students_data = []
    for student in students:
        student_dict = {
            'name': student.name,
            'school': student.school,
            'gender': student.gender.value,
            'academicPerformance': student.academicPerformance.value,
            'behavioralPerformance': student.behavioralPerformance.value,
            'comments': student.comments,
            'friend1': student.friend1,
            'friend2': student.friend2,
            'friend3': student.friend3,
            'friend4': student.friend4,
            'notWith': student.notWith,
            'clusterId': student.clusterId
        }
        students_data.append(student_dict)
    
    return pd.DataFrame(students_data)

@app.route('/classrooms', methods=['POST'])
def assign_classrooms():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        data = request.json
        classes_number = request.args.get('classesNumber', type=int)
        
        if not classes_number:
            return jsonify({"error": "classesNumber query parameter is required"}), 400
        
        try:
            students = [StudentDto.from_dict(student_data) for student_data in data]
        except (ValueError, TypeError) as e:
            app.logger.error(f"Error converting student data: {str(e)}")
            return jsonify({"error": f"Invalid student data format: {str(e)}"}), 400
        
        df = create_dataframe(students)
        service = ClassAssignmentService(df)
        class_assignments = service.assign_classes(classes_number)

        response = generate_class_summaries(service, class_assignments, students)
        return jsonify(response)
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/template', methods=['GET'])
def get_template():
    if TEMPLATE is None:
        return jsonify({"error": "Template not available"}), 500
    return jsonify(TEMPLATE), 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(debug=True) 