#!/usr/bin/env python
"""
Even Semester Data Setup Script
Organizes students by even semesters (2, 4, 6, 8) with realistic data
"""

import sys
from pathlib import Path
from datetime import datetime
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app
from extensions import db
from model import (
    Student, Subject, StudentPerformance, Attendance, 
    User, TeacherSubject, AcademicYear, Department, Course
)

# =====================================================
# CONFIGURATION
# =====================================================

CURRENT_MONTH = 2
CURRENT_YEAR = 2026
TOTAL_CLASSES_PER_MONTH = 20

# Even Semesters
EVEN_SEMESTERS = [2, 4, 6, 8]

# Subjects by semester
SEMESTER_SUBJECTS = {
    2: [
        {"name": "Data Structures", "code": "CS201", "credits": 4},
        {"name": "Object Oriented Programming", "code": "CS202", "credits": 4},
        {"name": "Discrete Mathematics", "code": "CS203", "credits": 4},
        {"name": "Digital Logic", "code": "CS204", "credits": 4},
        {"name": "Web Development", "code": "CS205", "credits": 4},
    ],
    4: [
        {"name": "Database Management", "code": "CS401", "credits": 4},
        {"name": "Operating Systems", "code": "CS402", "credits": 4},
        {"name": "Computer Networks", "code": "CS403", "credits": 4},
        {"name": "Software Engineering", "code": "CS404", "credits": 4},
        {"name": "Design Analysis Algorithms", "code": "CS405", "credits": 4},
    ],
    6: [
        {"name": "Machine Learning", "code": "CS601", "credits": 4},
        {"name": "Compiler Design", "code": "CS602", "credits": 4},
        {"name": "Cloud Computing", "code": "CS603", "credits": 4},
        {"name": "Cyber Security", "code": "CS604", "credits": 4},
        {"name": "Mobile Computing", "code": "CS605", "credits": 4},
    ],
    8: [
        {"name": "Deep Learning", "code": "CS801", "credits": 4},
        {"name": "Blockchain", "code": "CS802", "credits": 4},
        {"name": "Big Data Analytics", "code": "CS803", "credits": 4},
        {"name": "Internet of Things", "code": "CS804", "credits": 4},
        {"name": "Project Work", "code": "CS805", "credits": 6},
    ]
}

# Teachers by subject
TEACHERS = [
    {"username": "cs_teacher1", "name": "Dr. Sharma", "subjects": ["Data Structures", "Operating Systems", "Database Management"]},
    {"username": "cs_teacher2", "name": "Prof. Verma", "subjects": ["Design Analysis Algorithms", "Compiler Design", "Machine Learning"]},
    {"username": "cs_teacher3", "name": "Dr. Patel", "subjects": ["Object Oriented Programming", "Cloud Computing", "Big Data Analytics"]},
    {"username": "cs_teacher4", "name": "Prof. Singh", "subjects": ["Computer Networks", "Cyber Security", "Deep Learning"]},
    {"username": "cs_teacher5", "name": "Dr. Kumar", "subjects": ["Discrete Mathematics", "Software Engineering", "Project Work"]},
]

# Students by semester (even semesters)
STUDENTS_BY_SEMESTER = {
    2: [
        {"reg_no": "CS2025001", "name": "Aarav Sharma", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2025002", "name": "Vihaan Patel", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2025003", "name": "Vivaan Singh", "attendance_range": "low", "marks_range": "low"},
        {"reg_no": "CS2025004", "name": "Ananya Gupta", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2025005", "name": "Diya Reddy", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2025006", "name": "Advik Kumar", "attendance_range": "low", "marks_range": "low"},
        {"reg_no": "CS2025007", "name": "Kabir Malhotra", "attendance_range": "critical", "marks_range": "critical"},
        {"reg_no": "CS2025008", "name": "Ishaan Mehta", "attendance_range": "medium", "marks_range": "medium"},
    ],
    4: [
        {"reg_no": "CS2024001", "name": "Prisha Joshi", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2024002", "name": "Rudra Choudhury", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024003", "name": "Sanya Kapoor", "attendance_range": "low", "marks_range": "low"},
        {"reg_no": "CS2024004", "name": "Arjun Nair", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2024005", "name": "Ishita Bhatt", "attendance_range": "critical", "marks_range": "critical"},
        {"reg_no": "CS2024006", "name": "Yash Desai", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024007", "name": "Myra Menon", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2024008", "name": "Shaurya Thakur", "attendance_range": "low", "marks_range": "low"},
    ],
    6: [
        {"reg_no": "CS2023086", "name": "Vedant Patel", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2023087", "name": "Pranav Patel", "attendance_range": "low", "marks_range": "low"},
        {"reg_no": "CS2023088", "name": "Karthik Patel", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2023089", "name": "Nikhil Patel", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2023090", "name": "Rahul Patel", "attendance_range": "critical", "marks_range": "critical"},
        {"reg_no": "CS2024046", "name": "Dhruv Verma", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2024047", "name": "Rudra Verma", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024048", "name": "Samar Verma", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2024049", "name": "Aayush Verma", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024050", "name": "Veer Verma", "attendance_range": "low", "marks_range": "low"},
        {"reg_no": "CS2024051", "name": "Ritvik Verma", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024052", "name": "Yuvaan Verma", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024053", "name": "Ranveer Verma", "attendance_range": "low", "marks_range": "low"},
        {"reg_no": "CS2024054", "name": "Vedant Verma", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024055", "name": "Pranav Verma", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2024056", "name": "Karthik Verma", "attendance_range": "low", "marks_range": "low"},
        {"reg_no": "CS2024057", "name": "Nikhil Verma", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024058", "name": "Rahul Verma", "attendance_range": "critical", "marks_range": "critical"},
        {"reg_no": "CS2024059", "name": "Raj Verma", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2024060", "name": "Amit Verma", "attendance_range": "low", "marks_range": "low"},
    ],
    8: [
        {"reg_no": "CS2022106", "name": "Atharv Singh", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2022107", "name": "Krishna Singh", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2022108", "name": "Shaurya Singh", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2022109", "name": "Yash Singh", "attendance_range": "low", "marks_range": "low"},
        {"reg_no": "CS2022110", "name": "Dhruv Singh", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2022111", "name": "Rudra Singh", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2022112", "name": "Samar Singh", "attendance_range": "critical", "marks_range": "critical"},
        {"reg_no": "CS2022113", "name": "Aayush Singh", "attendance_range": "medium", "marks_range": "medium"},
        {"reg_no": "CS2022114", "name": "Veer Singh", "attendance_range": "high", "marks_range": "high"},
        {"reg_no": "CS2022115", "name": "Ritvik Singh", "attendance_range": "medium", "marks_range": "medium"},
    ]
}

# Attendance ranges by category (out of 20)
ATTENDANCE_RANGES = {
    'critical': list(range(5, 11)),     # 5-10 days (25-50%)
    'low': list(range(10, 14)),         # 10-13 days (50-65%)
    'medium': list(range(14, 17)),      # 14-16 days (70-80%)
    'high': list(range(17, 20)),        # 17-19 days (85-95%)
    'perfect': [20]                      # 20 days (100%)
}

# Marks ranges by category (out of 20)
MARKS_RANGES = {
    'critical': list(range(0, 8)),      # 0-7 marks (F)
    'low': list(range(8, 11)),          # 8-10 marks (D)
    'medium': list(range(11, 15)),      # 11-14 marks (C)
    'high': list(range(15, 18)),        # 15-17 marks (B)
    'perfect': list(range(18, 21))      # 18-20 marks (A/A+)
}

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_grade(marks):
    """Get grade based on marks out of 20"""
    if marks >= 18:
        return 'A+'
    elif marks >= 16:
        return 'A'
    elif marks >= 14:
        return 'B+'
    elif marks >= 12:
        return 'B'
    elif marks >= 10:
        return 'C'
    elif marks >= 8:
        return 'D'
    else:
        return 'F'

def get_risk_status(attendance, marks, semester):
    """Determine risk status based on attendance, marks and semester"""
    attendance_pct = (attendance / TOTAL_CLASSES_PER_MONTH) * 100
    
    # Higher semesters have stricter criteria
    if semester >= 8:
        if attendance_pct < 75 or marks < 12:
            return 'Critical'
        elif attendance_pct < 80 or marks < 14:
            return 'High Risk'
        elif attendance_pct < 85 or marks < 16:
            return 'Average'
        else:
            return 'Safe'
    elif semester >= 6:
        if attendance_pct < 70 or marks < 10:
            return 'Critical'
        elif attendance_pct < 75 or marks < 12:
            return 'High Risk'
        elif attendance_pct < 80 or marks < 14:
            return 'Average'
        else:
            return 'Safe'
    else:
        if attendance_pct < 65 or marks < 8:
            return 'Critical'
        elif attendance_pct < 70 or marks < 10:
            return 'High Risk'
        elif attendance_pct < 75 or marks < 12:
            return 'Average'
        else:
            return 'Safe'

def get_penalty_status(attended):
    """Determine penalty status"""
    percent = (attended / TOTAL_CLASSES_PER_MONTH) * 100
    if percent >= 90:
        return 'No Penalty'
    elif percent >= 80:
        return 'Low Penalty'
    elif percent >= 70:
        return 'Medium Penalty'
    else:
        return 'High Penalty'

def get_penalty_amount(status):
    """Get penalty amount"""
    penalties = {
        'No Penalty': 0,
        'Low Penalty': 200,
        'Medium Penalty': 500,
        'High Penalty': 1000
    }
    return penalties.get(status, 0)

def get_teacher_for_subject(subject_name, teachers_dict):
    """Get teacher for a subject"""
    for teacher_info in TEACHERS:
        if subject_name in teacher_info['subjects']:
            username = teacher_info['username']
            if username in teachers_dict:
                return teachers_dict[username]
    # Return first teacher as default
    return list(teachers_dict.values())[0] if teachers_dict else None

# =====================================================
# STUDENT CREATION FUNCTIONS
# =====================================================

def create_student_performance_records(student, semester, student_data, subjects, teachers_dict, academic_year):
    """
    Create attendance and performance records for a single student
    """
    # Get attendance and marks based on the student's range
    att_range = student_data.get('attendance_range', 'medium')
    marks_range = student_data.get('marks_range', 'medium')
    
    # Select a random subject for this student
    subject = random.choice(subjects)
    
    # Get attendance value from ranges
    attended = random.choice(ATTENDANCE_RANGES.get(att_range, ATTENDANCE_RANGES['medium']))
    attendance_percent = round((attended / TOTAL_CLASSES_PER_MONTH) * 100, 1)
    
    # Get marks value from ranges
    marks = random.choice(MARKS_RANGES.get(marks_range, MARKS_RANGES['medium']))
    
    # Calculate grade and risk
    grade = get_grade(marks)
    risk = get_risk_status(attended, marks, semester)
    
    # Calculate penalty
    penalty_status = get_penalty_status(attended)
    penalty_amount = get_penalty_amount(penalty_status)
    
    # Find teacher for this subject
    teacher = get_teacher_for_subject(subject.name, teachers_dict)
    teacher_id = teacher.id if teacher else None
    
    # Create attendance for February 2026
    attendance_feb = Attendance(
        student_id=student.id,
        subject_id=subject.id,
        teacher_id=teacher_id,
        total_classes=TOTAL_CLASSES_PER_MONTH,
        attended_classes=attended,
        attendance_percentage=attendance_percent,
        penalty_amount=penalty_amount,
        penalty_status=penalty_status,
        month=2,  # February
        year=2026,
        semester=semester
    )
    db.session.add(attendance_feb)
    
    # Create attendance for January 2026 (with slight variation)
    jan_attended = max(5, min(20, attended + random.randint(-2, 2)))
    jan_percent = round((jan_attended / TOTAL_CLASSES_PER_MONTH) * 100, 1)
    jan_penalty_status = get_penalty_status(jan_attended)
    jan_penalty_amount = get_penalty_amount(jan_penalty_status)
    
    attendance_jan = Attendance(
        student_id=student.id,
        subject_id=subject.id,
        teacher_id=teacher_id,
        total_classes=TOTAL_CLASSES_PER_MONTH,
        attended_classes=jan_attended,
        attendance_percentage=jan_percent,
        penalty_amount=jan_penalty_amount,
        penalty_status=jan_penalty_status,
        month=1,  # January
        year=2026,
        semester=semester
    )
    db.session.add(attendance_jan)
    
    # Create performance record
    internal1 = random.randint(40, 65)
    internal2 = random.randint(40, 65)
    seminar = random.randint(7, 10)
    assessment = random.randint(7, 10)
    total_marks = internal1 + internal2 + seminar + assessment
    
    performance = StudentPerformance(
        student_id=student.id,
        subject_id=subject.id,
        attendance=attendance_percent,
        internal1=internal1,
        internal2=internal2,
        seminar=seminar,
        assessment=assessment,
        total_marks=total_marks,
        final_internal=marks,
        risk_status=risk,
        semester=semester,
        academic_year_id=academic_year.id
    )
    db.session.add(performance)
    
    # Print summary for this student
    print(f"      └─ Att: {attended}/20 ({attendance_percent}%), Marks: {marks}/20 ({grade}), Risk: {risk}")
    
    # Flush to ensure records are saved
    db.session.flush()
    
    return True

def create_students_for_semester(semester, semester_students, course, dept, subjects_by_semester, teachers_dict, academic_year):
    """
    Create students for a specific semester with proper student_id values
    and generate all attendance and performance records
    """
    print(f"\n  Semester {semester}:")
    
    # Get the maximum existing student_id to ensure uniqueness
    max_id = db.session.query(db.func.max(Student.student_id)).scalar() or 0
    current_id = max_id
    
    for idx, student_data in enumerate(semester_students):
        # Increment student_id for each new student
        current_id += 1
        student_id_val = current_id
        
        # Check if student already exists by registration number
        student = Student.query.filter_by(registration_number=student_data['reg_no']).first()
        
        if not student:
            # Create new student with ALL required fields
            student = Student(
                registration_number=student_data['reg_no'],
                student_id=student_id_val,  # CRITICAL: This must NOT be None
                name=student_data['name'],
                email=f"{student_data['name'].lower().replace(' ', '.')}@spas.edu",
                phone=f"9{random.randint(100000000, 999999999)}",
                user_id=None,
                course_id=course.id,
                department_id=dept.id,
                current_semester=semester,
                batch_year=2025 if semester <= 4 else 2024 if semester <= 6 else 2023,
                admission_date=datetime(2025, 6, 1) if semester <= 4 else datetime(2024, 6, 1),
                is_active=True
                # created_at will be auto-set by default
            )
            db.session.add(student)
            db.session.flush()  # Get the student.id
            print(f"    ✓ Created {student.registration_number} - {student.name}")
        else:
            # Update existing student's semester
            student.current_semester = semester
            db.session.flush()
            print(f"    ✓ Updated {student.registration_number} - {student.name}")
        
        # Now create attendance and performance records for this student
        create_student_performance_records(
            student=student,
            semester=semester,
            student_data=student_data,
            subjects=subjects_by_semester[semester],
            teachers_dict=teachers_dict,
            academic_year=academic_year
        )

# =====================================================
# MAIN SETUP FUNCTION
# =====================================================

def setup_even_semesters():
    """Setup complete data for all even semesters"""
    
    app = create_app('development')
    
    with app.app_context():
        print("\n" + "=" * 80)
        print("EVEN SEMESTERS DATA SETUP (2, 4, 6, 8)")
        print("=" * 80)
        
        # Get department
        dept = Department.query.filter_by(name='Computer Science').first()
        if not dept:
            dept = Department(name='Computer Science', code='CS')
            db.session.add(dept)
            db.session.commit()
            print(f"✓ Created department: {dept.name}")
        else:
            print(f"✓ Found department: {dept.name}")
        
        # Get course
        course = Course.query.filter_by(name='B.Sc Computer Science').first()
        if not course:
            course = Course(
                name='B.Sc Computer Science',
                code='BSC-CS',
                duration_years=3,
                department_id=dept.id
            )
            db.session.add(course)
            db.session.commit()
            print(f"✓ Created course: {course.name}")
        else:
            print(f"✓ Found course: {course.name}")
        
        # Get academic year
        academic_year = AcademicYear.query.filter_by(is_current=True).first()
        if not academic_year:
            academic_year = AcademicYear(
                year="2025-2026",
                is_current=True,
                start_date=datetime(2025, 6, 1),
                end_date=datetime(2026, 4, 30)
            )
            db.session.add(academic_year)
            db.session.commit()
            print(f"✓ Created academic year: {academic_year.year}")
        else:
            print(f"✓ Found academic year: {academic_year.year}")
        
        # Create teachers
        print("\n[1] Creating teachers...")
        teachers_dict = {}
        for teacher_info in TEACHERS:
            teacher = User.query.filter_by(username=teacher_info['username']).first()
            if not teacher:
                teacher = User(
                    username=teacher_info['username'],
                    email=f"{teacher_info['username']}@spas.edu",
                    full_name=teacher_info['name'],
                    role='teacher',
                    department_id=dept.id
                )
                teacher.set_password('password')
                db.session.add(teacher)
                db.session.flush()
                print(f"  ✓ Created teacher: {teacher.full_name} ({teacher.username})")
            else:
                print(f"  ✓ Found teacher: {teacher.full_name}")
            teachers_dict[teacher_info['username']] = teacher
        
        db.session.commit()
        
        # Create subjects by semester
        print("\n[2] Creating subjects for even semesters...")
        subjects_by_semester = {}
        for semester in EVEN_SEMESTERS:
            subjects_by_semester[semester] = []
            for subject_data in SEMESTER_SUBJECTS[semester]:
                subject = Subject.query.filter_by(
                    name=subject_data['name'],
                    semester_id=semester
                ).first()
                if not subject:
                    subject = Subject(
                        name=subject_data['name'],
                        code=subject_data['code'],
                        credits=subject_data['credits'],
                        semester_id=semester,
                        department_id=dept.id
                    )
                    db.session.add(subject)
                    db.session.flush()
                    print(f"  ✓ Created: Sem {semester} - {subject_data['name']}")
                else:
                    print(f"  ✓ Found: Sem {semester} - {subject_data['name']}")
                subjects_by_semester[semester].append(subject)
        
        db.session.commit()
        
        # Assign teachers to subjects
        print("\n[3] Assigning teachers to subjects...")
        for semester, subjects in subjects_by_semester.items():
            for subject in subjects:
                teacher = get_teacher_for_subject(subject.name, teachers_dict)
                if teacher:
                    existing = TeacherSubject.query.filter_by(
                        teacher_id=teacher.id,
                        subject_id=subject.id,
                        academic_year_id=academic_year.id,
                        is_active=True
                    ).first()
                    
                    if not existing:
                        assignment = TeacherSubject(
                            teacher_id=teacher.id,
                            subject_id=subject.id,
                            academic_year_id=academic_year.id,
                            semester_id=semester,
                            is_active=True
                        )
                        db.session.add(assignment)
                        print(f"  ✓ Assigned {teacher.full_name} to {subject.name}")
                    else:
                        print(f"  ✓ Already assigned: {subject.name}")
        
        db.session.commit()
        
        # Clear existing data
        print("\n[4] Clearing existing data...")
        Attendance.query.delete()
        StudentPerformance.query.delete()
        # Don't delete students, just their performance data
        db.session.commit()
        print("  ✓ Existing performance and attendance data cleared")
        
        # Create student data
        print("\n[5] Creating student data for even semesters...")
        
        for semester in EVEN_SEMESTERS:
            semester_students = STUDENTS_BY_SEMESTER.get(semester, [])
            
            # Call the function to create students for this semester
            create_students_for_semester(
                semester=semester,
                semester_students=semester_students,
                course=course,
                dept=dept,
                subjects_by_semester=subjects_by_semester,
                teachers_dict=teachers_dict,
                academic_year=academic_year
            )
        
        db.session.commit()
        
        # Calculate totals
        total_students = Student.query.count()
        total_performance = StudentPerformance.query.count()
        total_attendance = Attendance.query.count()
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✓ Even Semesters: 2, 4, 6, 8")
        print(f"✓ Total Students: {total_students}")
        print(f"✓ Performance Records: {total_performance}")
        print(f"✓ Attendance Records: {total_attendance}")
        
        print("\n" + "-" * 80)
        print("STUDENTS BY SEMESTER")
        print("-" * 80)
        
        for semester in EVEN_SEMESTERS:
            semester_students = Student.query.filter_by(current_semester=semester).all()
            print(f"\nSemester {semester}: {len(semester_students)} students")
            
            # Show first 3 students as sample
            for i, student in enumerate(semester_students[:3]):
                perf = StudentPerformance.query.filter_by(student_id=student.id).first()
                if perf:
                    print(f"  {i+1}. {student.registration_number} - {student.name}: "
                          f"{perf.final_internal}/20 ({perf.risk_status})")
        
        print("\n" + "=" * 80)
        print("SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Restart your Flask application")
        print("  2. Check HOD Dashboard → Student Performance")
        print("  3. Filter by semester to see even semesters (2, 4, 6, 8)")
        print("  4. Each semester will have realistic student data")
        print("\nTeacher login credentials:")
        for teacher_info in TEACHERS:
            print(f"  • {teacher_info['name']}: {teacher_info['username']} / password")

if __name__ == "__main__":
    setup_even_semesters()