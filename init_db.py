#!/usr/bin/env python
"""
Database Initialization Script for Student Performance Analysis System
Run this script to create database tables and populate with initial data
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date
from werkzeug.security import generate_password_hash

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("=" * 60)
print("STUDENT PERFORMANCE ANALYSIS SYSTEM")
print("=" * 60)
print(f"Current directory: {Path(__file__).resolve().parent}")
print("-" * 60)

try:
    from app import create_app
    from extensions import db
    from model import *
    print("SUCCESS: All modules imported successfully!")
except ImportError as e:
    print(f"ERROR: Import failed - {e}")
    sys.exit(1)

# =====================================================
# CONFIGURATION
# =====================================================

# Default passwords
STUDENT_PASSWORD = "1234"
TEACHER_PASSWORD = "123"
HOD_PASSWORD = "hod123"
COORDINATOR_PASSWORD = "coord123"
PRINCIPAL_PASSWORD = "123"

# College information
COLLEGE_NAME = "Government Arts College, Chennai"

# =====================================================
# DATABASE INITIALIZATION FUNCTIONS
#=====================================================

def init_db():
    """Initialize the database by creating all tables"""
    print("\n" + "=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    
    # Create app context
    app = create_app('development')
    
    with app.app_context():
        # Get database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"\nDatabase path: {db_path}")
        
        # Create instance directory if it doesn't exist
        instance_dir = os.path.dirname(db_path)
        if instance_dir and not os.path.exists(instance_dir):
            os.makedirs(instance_dir)
            print(f"Created instance directory: {instance_dir}")
        
        # Drop all tables and create new ones
        print("\nDropping existing tables...")
        db.drop_all()
        print("Tables dropped successfully!")
        
        print("\nCreating new tables...")
        db.create_all()
        print("Tables created successfully!")
        
        # Seed the database
        print("\nSeeding database with initial data...")
        seed_database()
        
        # Verify the setup
        verify_database()
        
        print("\n" + "=" * 60)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("  python app.py")
        print("\nLogin Credentials:")
        print("-" * 40)
        print("Principal: username=principal, password=123")
        print("HOD: username=hod_cs, password=hod123")
        print("Teacher: username=cs_teacher1, password=123")
        print("Student: username=cs_stu1, password=1234")
        print("Coordinator: username=coordinator, password=coord123 (No Department)")
        print("=" * 60)

def seed_database():
    """Seed the database with initial data"""
    
    # Step 1: Create Departments
    print("\n1. Creating Departments...")
    departments = create_departments()
    db.session.flush()
    print(f"   - Created {len(departments)} departments")
    
    # Step 2: Create Academic Year
    print("\n2. Creating Academic Year...")
    academic_year = create_academic_year()
    db.session.flush()
    print(f"   - Created academic year: {academic_year.year}")
    
    # Step 3: Create Courses
    print("\n3. Creating Courses...")
    courses = create_courses(departments)
    db.session.flush()
    print(f"   - Created {len(courses)} courses")
    
    # Step 4: Create Semesters
    print("\n4. Creating Semesters...")
    semesters = create_semesters(courses, academic_year)
    db.session.flush()
    print(f"   - Created {len(semesters)} semesters")
    
    # Step 5: Create Subjects
    print("\n5. Creating Subjects...")
    subjects = create_subjects(departments, semesters)
    db.session.flush()
    print(f"   - Created {len(subjects)} subjects")
    
    # Step 6: Create Principal
    print("\n6. Creating Principal...")
    principal = create_principal()
    db.session.flush()
    print(f"   - Created principal: {principal.full_name}")
    
    # Step 7: Create HODs
    print("\n7. Creating HODs...")
    hods = create_hods(departments)
    db.session.flush()
    print(f"   - Created {len(hods)} HODs")
    
    # Step 8: Create Coordinators (No Department)
    print("\n8. Creating Coordinators...")
    coordinators = create_coordinators()  # No department parameter
    db.session.flush()
    print(f"   - Created {len(coordinators)} coordinators (No Department)")
    
    # Step 9: Create Teachers
    print("\n9. Creating Teachers...")
    teachers_by_dept = create_teachers(departments)
    db.session.flush()
    total_teachers = sum(len(t) for t in teachers_by_dept.values())
    print(f"   - Created {total_teachers} teachers")
    
    # Step 10: Create Students
    print("\n10. Creating Students...")
    students_by_dept = create_students(departments, courses)
    db.session.flush()
    total_students = sum(len(s) for s in students_by_dept.values())
    print(f"   - Created {total_students} students")
    
    # Commit all changes
    db.session.commit()
    print("\nDATABASE SEEDING COMPLETED SUCCESSFULLY!")

# =====================================================
# CREATION FUNCTIONS
# =====================================================

def create_departments():
    """Create departments"""
    departments = []
    dept_data = [
        {"code": "CS", "name": "Computer Science"},
        {"code": "BCA", "name": "Computer Applications"},
        {"code": "COM_FIN", "name": "Commerce Finance"},
        {"code": "COM_COOP", "name": "Commerce Co-op"},
        {"code": "ENG", "name": "English"},
        {"code": "ECO", "name": "Economics"},
        {"code": "HIS", "name": "History"}
    ]
    
    for data in dept_data:
        dept = Department(
            code=data["code"],
            name=data["name"]
        )
        db.session.add(dept)
        departments.append(dept)
    
    return departments

def create_academic_year():
    """Create current academic year"""
    current_year = datetime.now().year
    if datetime.now().month >= 6:
        year_str = f"{current_year}-{current_year + 1}"
        start_date = date(current_year, 6, 1)
        end_date = date(current_year + 1, 4, 30)
    else:
        year_str = f"{current_year - 1}-{current_year}"
        start_date = date(current_year - 1, 6, 1)
        end_date = date(current_year, 4, 30)
    
    academic_year = AcademicYear(
        year=year_str,
        start_date=start_date,
        end_date=end_date,
        is_current=True
    )
    db.session.add(academic_year)
    return academic_year

def create_courses(departments):
    """Create courses for each department"""
    courses = []
    dept_dict = {dept.name: dept for dept in departments}
    
    course_data = [
        ("Computer Science", "B.Sc Computer Science", "BSC_CS", 3),
        ("Computer Applications", "BCA", "BCA", 3),
        ("Commerce Finance", "B.Com Finance", "BCOM_FIN", 3),
        ("Commerce Co-op", "B.Com Co-op", "BCOM_COOP", 3),
        ("English", "B.A English", "BA_ENG", 3),
        ("Economics", "B.A Economics", "BA_ECO", 3),
        ("History", "B.A History", "BA_HIS", 3)
    ]
    
    for dept_name, course_name, course_code, duration in course_data:
        dept = dept_dict.get(dept_name)
        if dept:
            course = Course(
                name=course_name,
                code=course_code,
                duration_years=duration,
                department_id=dept.id
            )
            db.session.add(course)
            courses.append(course)
    
    return courses

def create_semesters(courses, academic_year):
    """Create semesters for each course"""
    semesters = []
    
    for course in courses:
        for sem_num in range(1, 7):  # 6 semesters for 3-year course
            semester = Semester(
                semester_number=sem_num,
                course_id=course.id,
                academic_year_id=academic_year.id,
                start_date=academic_year.start_date,
                end_date=academic_year.end_date
            )
            db.session.add(semester)
            semesters.append(semester)
    
    return semesters

# In init_db.py, replace the create_subjects function:

def create_subjects(departments, semesters):
    """Create subjects for each department and semester from helpers.py"""
    subjects = []
    
    # Get all subjects from helpers.py
    from utils.helpers import get_all_subjects
    all_subjects = get_all_subjects()
    
    # Map semesters by department and semester number
    semester_map = {}
    for sem in semesters:
        course = Course.query.get(sem.course_id)
        if course:
            dept = Department.query.get(course.department_id)
            if dept:
                key = (dept.name, sem.semester_number)
                semester_map[key] = sem
    
    # Create subjects from helpers.py
    for subject_info in all_subjects:
        dept_name = subject_info['department']
        dept = None
        for d in departments:
            if d.name == dept_name:
                dept = d
                break
        
        if not dept:
            continue
            
        semester_num = subject_info['semester']
        key = (dept_name, semester_num)
        semester = semester_map.get(key)
        
        if not semester:
            continue
        
        # Check if subject already exists
        existing = Subject.query.filter_by(code=subject_info['code']).first()
        if not existing:
            subject = Subject(
                name=subject_info['name'],
                code=subject_info['code'],
                credits=subject_info['credits'],
                department_id=dept.id,
                semester_id=semester.id
            )
            db.session.add(subject)
            subjects.append(subject)
            print(f"   Created: {subject_info['code']} - {subject_info['name']}")
    
    return subjects

def create_principal():
    """Create principal user"""
    principal = User(
        username="principal",
        email="principal@education.com",
        full_name="Dr. Rajesh Kumar",
        role="principal",
        password_hash=generate_password_hash(PRINCIPAL_PASSWORD),
        is_active=True
    )
    db.session.add(principal)
    return principal

def create_hods(departments):
    """Create HODs for each department"""
    hods = []
    hod_names = [
        ("Computer Science", "Dr. Srinivasan"),
        ("Computer Applications", "Dr. Lakshmi"),
        ("Commerce Finance", "Dr. Venkatesh"),
        ("Commerce Co-op", "Dr. Meena"),
        ("English", "Dr. Sharmila"),
        ("Economics", "Dr. Kumar"),
        ("History", "Dr. Rajan")
    ]
    
    dept_dict = {dept.name: dept for dept in departments}
    
    for dept_name, hod_name in hod_names:
        dept = dept_dict.get(dept_name)
        if dept:
            username = f"hod_{dept.code.lower()}"
            hod = User(
                username=username,
                email=f"{username}@college.edu",
                full_name=hod_name,
                role="hod",
                department_id=dept.id,
                password_hash=generate_password_hash(HOD_PASSWORD),
                is_active=True
            )
            db.session.add(hod)
            hods.append(hod)
    
    return hods

def create_coordinators():
    """Create coordinators - NO DEPARTMENT (as requested)"""
    coordinators = []
    
    # Create a single coordinator with no department
    coordinator = User(
        username="coordinator",
        email="coordinator@college.edu",
        full_name="Mr. Elamathi",
        role="coordinator",
        department_id=None,  # No department
        password_hash=generate_password_hash(COORDINATOR_PASSWORD),
        is_active=True
    )
    db.session.add(coordinator)
    coordinators.append(coordinator)
    
    return coordinators

def create_teachers(departments):
    """Create 6 teachers per department"""
    teachers_by_dept = {}
    
    for dept in departments:
        teachers = []
        for i in range(1, 7):  # 6 teachers per department
            username = f"{dept.code.lower()}_teacher{i}"
            teacher = User(
                username=username,
                email=f"{username}@college.edu",
                full_name=f"{dept.name} Teacher {i}",
                role="teacher",
                department_id=dept.id,
                password_hash=generate_password_hash(TEACHER_PASSWORD),
                is_active=True
            )
            db.session.add(teacher)
            teachers.append(teacher)
        
        teachers_by_dept[dept.id] = teachers
    
    return teachers_by_dept

def create_students(departments, courses):
    """Create 5 students per department"""
    students_by_dept = {}
    
    # Map courses by department
    course_dict = {}
    for course in courses:
        course_dict[course.department_id] = course
    
    for dept in departments:
        students = []
        course = course_dict.get(dept.id)
        
        if course:
            for i in range(1, 6):  # 5 students per department
                reg_number = f"{dept.code}{i:03d}"
                username = f"{dept.code.lower()}_stu{i}"
                
                user = User(
                    username=username,
                    email=f"{username}@college.edu",
                    full_name=f"{dept.name} Student {i}",
                    role="student",
                    department_id=dept.id,
                    password_hash=generate_password_hash(STUDENT_PASSWORD),
                    is_active=True
                )
                db.session.add(user)
                db.session.flush()
                
                student = Student(
                    registration_number=reg_number,
                    student_id=f"{dept.code}_{i}",
                    name=f"{dept.name} Student {i}",
                    email=f"{username}@college.edu",
                    phone=f"98765432{i:02d}",
                    user_id=user.id,
                    course_id=course.id,
                    department_id=dept.id,
                    current_semester=2,
                    batch_year=2025,
                    admission_date=date(2025, 6, 15),
                    is_active=True
                )
                db.session.add(student)
                students.append(student)
        
        students_by_dept[dept.id] = students
    
    return students_by_dept

# =====================================================
# VERIFICATION FUNCTION
# =====================================================

def verify_database():
    """Verify the database setup"""
    print("\n" + "-" * 40)
    print("DATABASE VERIFICATION")
    print("-" * 40)
    
    print("\nTable Counts:")
    print(f"  Users: {User.query.count()}")
    print(f"  Departments: {Department.query.count()}")
    print(f"  Courses: {Course.query.count()}")
    print(f"  Semesters: {Semester.query.count()}")
    print(f"  Subjects: {Subject.query.count()}")
    print(f"  Students: {Student.query.count()}")
    
    print("\nUsers by Role:")
    print(f"  Principal: {User.query.filter_by(role='principal').count()}")
    print(f"  HOD: {User.query.filter_by(role='hod').count()}")
    print(f"  Coordinator: {User.query.filter_by(role='coordinator').count()}")
    print(f"  Teacher: {User.query.filter_by(role='teacher').count()}")
    print(f"  Student: {User.query.filter_by(role='student').count()}")
    
    # Verify coordinator has no department
    coordinator = User.query.filter_by(role='coordinator').first()
    if coordinator:
        print(f"\nCoordinator Details:")
        print(f"  Username: {coordinator.username}")
        print(f"  Department ID: {coordinator.department_id} (No Department - Correct)")

# =====================================================
# MAIN EXECUTION
# =====================================================

if __name__ == "__main__":
    init_db()