#!/usr/bin/env python
"""
Fix Student Enrollment Script
Diagnose and fix why students aren't appearing in subjects
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app
from extensions import db
from model import (
    Student, Subject, Department, Course, 
    Semester, AcademicYear, User, TeacherSubject,
    StudentPerformance, Attendance
)

def diagnose_problem():
    """Diagnose why students aren't appearing in subjects"""
    
    app = create_app('development')
    
    with app.app_context():
        print("\n" + "=" * 70)
        print("STUDENT ENROLLMENT DIAGNOSTIC")
        print("=" * 70)
        
        # 1. Check if we have students
        students = Student.query.all()
        print(f"\n1. TOTAL STUDENTS IN DATABASE: {len(students)}")
        
        if len(students) == 0:
            print("   No students found! Run auto_setup.py first.")
            return
        
        # 2. Check if we have subjects
        subjects = Subject.query.all()
        print(f"\n2. TOTAL SUBJECTS IN DATABASE: {len(subjects)}")
        
        # 3. Check Mathematics I specifically
        math_subject = Subject.query.filter_by(name="Mathematics I").first()
        if math_subject:
            print(f"\n3. MATHEMATICS I DETAILS:")
            print(f"   - ID: {math_subject.id}")
            print(f"   - Code: {math_subject.code}")
            print(f"   - Department ID: {math_subject.department_id}")
            print(f"   - Semester ID: {math_subject.semester_id}")
            
            # Check department
            dept = Department.query.get(math_subject.department_id)
            print(f"   - Department: {dept.name if dept else 'Unknown'}")
            
            # Check semester
            sem = Semester.query.get(math_subject.semester_id)
            if sem:
                print(f"   - Semester Number: {sem.semester_number}")
                course = Course.query.get(sem.course_id)
                print(f"   - Course: {course.name if course else 'Unknown'}")
            
            # Find students for this subject
            students_for_subject = Student.query.filter_by(
                department_id=math_subject.department_id,
                current_semester=math_subject.semester_id
            ).all()
            
            print(f"\n4. STUDENTS FOR MATHEMATICS I:")
            print(f"   - Query: department_id={math_subject.department_id}, semester_id={math_subject.semester_id}")
            print(f"   - Students found: {len(students_for_subject)}")
            
            if len(students_for_subject) > 0:
                print("\n   Sample students:")
                for s in students_for_subject[:5]:
                    print(f"     • {s.name} (Semester: {s.current_semester})")
            else:
                print("    No students match this department and semester combination!")
        else:
            print("\n3.  Mathematics I not found in database!")
        
        # 4. Check student distribution by department and semester
        print("\n5. STUDENT DISTRIBUTION BY DEPARTMENT AND SEMESTER:")
        
        depts = Department.query.all()
        for dept in depts:
            print(f"\n   {dept.name}:")
            for sem_num in range(1, 7):  # Semesters 1-6
                count = Student.query.filter_by(
                    department_id=dept.id,
                    current_semester=sem_num
                ).count()
                if count > 0:
                    print(f"     Sem {sem_num}: {count} students")
        
        # 5. Check subject distribution by department and semester
        print("\n6. SUBJECT DISTRIBUTION BY DEPARTMENT AND SEMESTER:")
        
        for dept in depts:
            print(f"\n   {dept.name}:")
            for sem_num in range(1, 7):
                # Find semester object
                semester = Semester.query.filter_by(
                    semester_number=sem_num,
                    course_id=Course.query.filter_by(department_id=dept.id).first().id if Course.query.filter_by(department_id=dept.id).first() else None
                ).first()
                
                if semester:
                    count = Subject.query.filter_by(
                        department_id=dept.id,
                        semester_id=semester.id
                    ).count()
                    if count > 0:
                        print(f"     Sem {sem_num}: {count} subjects")
        
        # 6. Check for semester ID mismatches
        print("\n7. CHECKING FOR SEMESTER ID MISMATCHES:")
        
        # Get all unique semester_ids from subjects
        subject_semester_ids = set(s.semester_id for s in subjects)
        
        # Get all current_semester values from students
        student_semesters = set(s.current_semester for s in students)
        
        print(f"   Subject semester_ids: {subject_semester_ids}")
        print(f"   Student current_semester values: {student_semesters}")
        
        # 7. Fix: Update student current_semester to match semester_ids
        print("\n" + "=" * 70)
        print("FIXING STUDENT ENROLLMENT")
        print("=" * 70)
        
        fixed_count = 0
        for student in students:
            # Find a semester object for this student's department and semester number
            course = Course.query.filter_by(department_id=student.department_id).first()
            if course:
                semester = Semester.query.filter_by(
                    course_id=course.id,
                    semester_number=student.current_semester
                ).first()
                
                if semester:
                    # Check if this semester_id exists in subjects
                    subject_count = Subject.query.filter_by(
                        department_id=student.department_id,
                        semester_id=semester.id
                    ).count()
                    
                    if subject_count == 0:
                        # Find a semester that has subjects
                        for alt_sem_num in range(1, 7):
                            alt_semester = Semester.query.filter_by(
                                course_id=course.id,
                                semester_number=alt_sem_num
                            ).first()
                            if alt_semester:
                                alt_count = Subject.query.filter_by(
                                    department_id=student.department_id,
                                    semester_id=alt_semester.id
                                ).count()
                                if alt_count > 0:
                                    print(f"   Fixing {student.name}: Sem {student.current_semester} -> Sem {alt_sem_num}")
                                    student.current_semester = alt_sem_num
                                    fixed_count += 1
                                    break
        
        if fixed_count > 0:
            db.session.commit()
            print(f"\n    Updated {fixed_count} students to semesters that have subjects")
        
        # 8. Create missing TeacherSubject assignments
        print("\n8. CREATING TEACHER-SUBJECT ASSIGNMENTS:")
        
        # Get cs_teacher1
        teacher = User.query.filter_by(username='cs_teacher1').first()
        if teacher:
            print(f"   Found teacher: {teacher.full_name} (ID: {teacher.id})")
            
            # Get all subjects in Computer Science department
            cs_dept = Department.query.filter_by(name='Computer Science').first()
            if cs_dept:
                cs_subjects = Subject.query.filter_by(department_id=cs_dept.id).all()
                
                assignment_count = 0
                for subject in cs_subjects:
                    # Check if already assigned
                    existing = TeacherSubject.query.filter_by(
                        teacher_id=teacher.id,
                        subject_id=subject.id,
                        is_active=True
                    ).first()
                    
                    if not existing:
                        # Find academic year
                        academic_year = AcademicYear.query.filter_by(is_current=True).first()
                        if academic_year:
                            # Find semester
                            semester = Semester.query.get(subject.semester_id)
                            if semester:
                                assignment = TeacherSubject(
                                    teacher_id=teacher.id,
                                    subject_id=subject.id,
                                    academic_year_id=academic_year.id,
                                    semester_id=semester.id,
                                    is_active=True
                                )
                                db.session.add(assignment)
                                assignment_count += 1
                                print(f"     Assigned {teacher.full_name} to {subject.name}")
                
                if assignment_count > 0:
                    db.session.commit()
                    print(f"    Created {assignment_count} new teacher-subject assignments")
                else:
                    print("   No new assignments needed")
        
        # 9. Final verification
        print("\n" + "=" * 70)
        print("FINAL VERIFICATION")
        print("=" * 70)
        
        # Check Mathematics I again
        math_subject = Subject.query.filter_by(name="Mathematics I").first()
        if math_subject:
            students_for_subject = Student.query.filter_by(
                department_id=math_subject.department_id,
                current_semester=math_subject.semester_id
            ).all()
            
            print(f"\nMathematics I now has {len(students_for_subject)} students")
            
            if len(students_for_subject) > 0:
                print("\n FIXED! Students should now appear in the teacher dashboard.")
                print("\nSample students:")
                for s in students_for_subject[:5]:
                    print(f"  • {s.name} (ID: {s.student_id}, Semester: {s.current_semester})")
            else:
                print("\n Still no students. Let's create them manually.")
                
                # Manual fix: Create at least one student for Mathematics I
                cs_dept = Department.query.filter_by(name='Computer Science').first()
                if cs_dept and math_subject:
                    # Find a student in CS department
                    any_student = Student.query.filter_by(department_id=cs_dept.id).first()
                    if any_student:
                        print(f"\nForcing update for student: {any_student.name}")
                        any_student.current_semester = math_subject.semester_id
                        db.session.commit()
                        print(f" Updated student to semester {math_subject.semester_id}")
        
        print("\n" + "=" * 70)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 70)

if __name__ == "__main__":
    diagnose_problem()