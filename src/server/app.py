from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from typing import List
import pandas as pd
import logging
import json
import os
from .dto import StudentDto
from .error_codes import ErrorCode, ErrorResponse
from src.service.class_assignment_service import ClassAssignmentService
from src.service.summary_service import generate_class_summaries
from src.service.validators.input_validator import InputValidationError

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

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
            return ErrorResponse(
                code=ErrorCode.INVALID_CONTENT_TYPE,
                message="Content-Type must be application/json"
            ).to_tuple(415)

        data = request.json
        classes_number = request.args.get('classesNumber', type=int)

        if not classes_number:
            return ErrorResponse(
                code=ErrorCode.MISSING_PARAMETER,
                params={"parameter": "classesNumber"},
                message="classesNumber query parameter is required"
            ).to_tuple(400)

        try:
            students = [StudentDto.from_dict(student_data) for student_data in data]
        except (ValueError, TypeError) as e:
            app.logger.warning(f"Error converting student data: {str(e)}")
            return ErrorResponse(
                code=ErrorCode.INVALID_STUDENT_DATA,
                params={"details": str(e)},
                message=f"Invalid student data format: {str(e)}"
            ).to_tuple(400)
        except InputValidationError as e:
            app.logger.warning(f"Input validation error: {str(e)}")
            return e.to_response().to_tuple(400)

        try:
            df = create_dataframe(students)
            service = ClassAssignmentService(df)
            class_assignments = service.assign_classes(classes_number)

            response = generate_class_summaries(service, class_assignments, students)
            return jsonify(response)
        except InputValidationError as e:
            app.logger.warning(f"Input validation error during assignment: {str(e)}")
            return e.to_response().to_tuple(400)

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return ErrorResponse(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            params={"details": str(e)},
            message=str(e)
        ).to_tuple(500)

@app.route('/template', methods=['GET'])
def get_template():
    language = request.args.get('lang')
    template_name = f'template-{language}.json' if language else 'template-en.json'
    try:
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', template_name)
        with open(template_path, 'r') as f:
            template = json.load(f)
            return jsonify(template), 200, {'Content-Type': 'application/json'}
    except FileNotFoundError:
        return ErrorResponse(
            code=ErrorCode.UNSUPPORTED_LANGUAGE,
            params={"language": language},
            message=f"Unsupported language: {language}"
        ).to_tuple(404)
    except Exception as e:
        logging.error(f"Failed to load template: {str(e)}")
        return ErrorResponse(
            code=ErrorCode.TEMPLATE_NOT_AVAILABLE,
            message="Template not available"
        ).to_tuple(500)


if __name__ == '__main__':
    app.run(debug=True) 