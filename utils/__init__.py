# utils/__init__.py
"""
Utils package for Student Performance Analysis System
"""

from utils.helpers import (
    DEPARTMENTS,
    DEPT_CODES,
    BATCH_MAPPING,
    SEMESTER_TO_YEAR,
    get_subjects_by_department_semester,
    get_all_subjects,
    get_all_departments,
    get_semesters_for_year,
    get_current_semester,
    get_semester_number,
    get_year_from_semester,
    get_batch_from_year,
    get_current_academic_year,
    generate_registration_number,
    generate_student_id,
    calculate_risk_status,
    calculate_final_internal,
    generate_password,
    format_phone_number
)

# Import AI Allocator
from utils.ai_allocator import TeacherSubjectAllocator

__all__ = [
    'DEPARTMENTS',
    'DEPT_CODES',
    'BATCH_MAPPING',
    'SEMESTER_TO_YEAR',
    'get_subjects_by_department_semester',
    'get_all_subjects',
    'get_all_departments',
    'get_semesters_for_year',
    'get_current_semester',
    'get_semester_number',
    'get_year_from_semester',
    'get_batch_from_year',
    'get_current_academic_year',
    'generate_registration_number',
    'generate_student_id',
    'calculate_risk_status',
    'calculate_final_internal',
    'generate_password',
    'format_phone_number',
    'TeacherSubjectAllocator'
]