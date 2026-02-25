#!/usr/bin/env python
"""
Fix Student Semesters Script
Updates student semesters to match available subjects and distributes students evenly
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app
from extensions import db
from model import Student, Subject, Department, Course, Semester

def fix_student_semesters():
    """Fix student semesters to match subjects"""
    
    app = create_app('development')
    
    with app.app_context():
        print("\n" + "="*60)
        print("FIXING STUDENT SEMESTERS")
        print("="*60)
        
        # Get all departments
        departments = Department.query.all()
        print(f"\nFound {len(departments)} departments")
        
        total_fixed = 0
        total_students = 0
        
        for dept in departments:
            print(f"\n{'-'*40}")
            print(f"Department: {dept.name}")
            print(f"{'-'*40}")
            
            # Get all subjects for this department
            subjects = Subject.query.filter_by(department_id=dept.id).all()
            if not subjects:
                print(f"   No subjects found for {dept.name}")
                continue
            
            # Get unique semester IDs from subjects
            subject_semester_ids = set(s.semester_id for s in subjects)
            
            # Get semester numbers for these IDs
            semesters = Semester.query.filter(Semester.id.in_(subject_semester_ids)).all()
            valid_semester_numbers = sorted(set(s.semester_number for s in semesters))
            
            print(f"\n   Subjects exist in semesters: {valid_semester_numbers}")
            
            # Get all students in this department
            students = Student.query.filter_by(department_id=dept.id).all()
            if not students:
                print(f"   No students found in {dept.name}")
                continue
            
            print(f"\n   Total students: {len(students)}")
            total_students += len(students)
            
            # Show current distribution
            print("\n   Current semester distribution:")
            current_dist = {}
            for student in students:
                if student.current_semester not in current_dist:
                    current_dist[student.current_semester] = 0
                current_dist[student.current_semester] += 1
            
            for sem in sorted(current_dist.keys()):
                print(f"      Semester {sem}: {current_dist[sem]} students")
            
            # Fix students in invalid semesters
            fixed_in_dept = 0
            for student in students:
                if student.current_semester not in valid_semester_numbers:
                    # Find closest valid semester
                    closest_sem = min(valid_semester_numbers, 
                                    key=lambda x: abs(x - student.current_semester))
                    print(f"      Fixing {student.name}: Sem {student.current_semester} -> Sem {closest_sem}")
                    student.current_semester = closest_sem
                    fixed_in_dept += 1
                    total_fixed += 1
            
            if fixed_in_dept > 0:
                db.session.flush()
                print(f"\n   Fixed {fixed_in_dept} students in {dept.name}")
            
            # Show new distribution
            new_dist = {}
            for student in students:
                if student.current_semester not in new_dist:
                    new_dist[student.current_semester] = 0
                new_dist[student.current_semester] += 1
            
            print("\n   New semester distribution:")
            for sem in sorted(new_dist.keys()):
                print(f"      Semester {sem}: {new_dist[sem]} students")
        
        # Commit all changes
        if total_fixed > 0:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"Successfully fixed {total_fixed} out of {total_students} students")
            print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print(f"All {total_students} students already in valid semesters")
            print(f"{'='*60}")

def distribute_students_evenly():
    """Distribute students evenly across all semesters 1-8"""
    
    app = create_app('development')
    
    with app.app_context():
        print("\n" + "="*60)
        print("DISTRIBUTING STUDENTS EVENLY ACROSS SEMESTERS")
        print("="*60)
        
        # Get all departments
        departments = Department.query.all()
        print(f"\nFound {len(departments)} departments")
        
        all_semesters = [1, 2, 3, 4, 5, 6, 7, 8]
        total_updated = 0
        
        for dept in departments:
            print(f"\n{'-'*40}")
            print(f"Department: {dept.name}")
            print(f"{'-'*40}")
            
            # Get all students in this department
            students = Student.query.filter_by(department_id=dept.id).all()
            if not students:
                print(f"   No students found in {dept.name}")
                continue
            
            print(f"\n   Total students: {len(students)}")
            
            # Show current distribution
            print("\n   Current distribution:")
            current_dist = {}
            for student in students:
                if student.current_semester not in current_dist:
                    current_dist[student.current_semester] = 0
                current_dist[student.current_semester] += 1
            
            for sem in all_semesters:
                count = current_dist.get(sem, 0)
                print(f"      Semester {sem}: {count} students")
            
            # Calculate how many students per semester (evenly distributed)
            students_per_semester = len(students) // 8
            remainder = len(students) % 8
            
            print(f"\n   Target distribution:")
            for i, sem in enumerate(all_semesters):
                target = students_per_semester + (1 if i < remainder else 0)
                print(f"      Semester {sem}: {target} students")
            
            # Create list of target counts for each semester
            target_counts = {}
            for i, sem in enumerate(all_semesters):
                target_counts[sem] = students_per_semester + (1 if i < remainder else 0)
            
            # Redistribute students
            semester_lists = {sem: [] for sem in all_semesters}
            
            # First, keep students already in correct semesters if possible
            for student in students:
                current_sem = student.current_semester
                if current_sem in all_semesters and len(semester_lists[current_sem]) < target_counts[current_sem]:
                    semester_lists[current_sem].append(student)
            
            # Distribute remaining students
            remaining_students = [s for s in students if not any(s in lst for lst in semester_lists.values())]
            
            for sem in all_semesters:
                while len(semester_lists[sem]) < target_counts[sem] and remaining_students:
                    student = remaining_students.pop(0)
                    semester_lists[sem].append(student)
                    if student.current_semester != sem:
                        print(f"   Moving {student.name}: Sem {student.current_semester} -> Sem {sem}")
                        student.current_semester = sem
                        total_updated += 1
            
            # Handle any remaining students (should not happen)
            if remaining_students:
                for student in remaining_students:
                    for sem in all_semesters:
                        if len(semester_lists[sem]) < target_counts[sem]:
                            semester_lists[sem].append(student)
                            if student.current_semester != sem:
                                print(f"   Moving {student.name}: Sem {student.current_semester} -> Sem {sem}")
                                student.current_semester = sem
                                total_updated += 1
                            break
            
            db.session.flush()
        
        # Commit all changes
        if total_updated > 0:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"Successfully redistributed {total_updated} students")
            print(f"{'='*60}")
            
            # Show final distribution
            print("\nFinal distribution across all departments:")
            for dept in departments:
                students = Student.query.filter_by(department_id=dept.id).all()
                if students:
                    print(f"\n{dept.name}:")
                    dist = {}
                    for student in students:
                        if student.current_semester not in dist:
                            dist[student.current_semester] = 0
                        dist[student.current_semester] += 1
                    for sem in all_semesters:
                        print(f"   Semester {sem}: {dist.get(sem, 0)} students")
        else:
            print(f"\n{'='*60}")
            print("No changes needed - students already evenly distributed")
            print(f"{'='*60}")

if __name__ == "__main__":
    print("\n1. Fix student semesters to match subjects")
    print("2. Distribute students evenly across all semesters")
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == '1':
        fix_student_semesters()
    elif choice == '2':
        distribute_students_evenly()
    else:
        print("Invalid choice")