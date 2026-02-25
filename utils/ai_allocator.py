# utils/ai_allocator.py
"""
AI-based Teacher-Subject Allocator - Even Semesters Only (2,4,6,8)
With proper semester mapping
"""

from model import User, Subject, TeacherSubject, AcademicYear, Department, Semester
from extensions import db
import random
from collections import defaultdict
from utils.helpers import DEPARTMENTS, get_subjects_by_department_semester

class TeacherSubjectAllocator:
    """AI Allocator for assigning teachers to subjects - Even Semesters Only"""
    
    def __init__(self, department_id, academic_year="2025-2026"):
        self.department_id = department_id
        self.academic_year_str = academic_year
        self.academic_year_obj = None
        self.teachers = []
        self.subjects = []
        self.teacher_workload = {}
        self.subjects_by_semester = defaultdict(list)
        self.max_subjects_per_teacher = 5
        self.even_semesters = [2, 4, 6, 8]  # Even semesters
        
    def load_data_fast(self):
        """Load data quickly with minimal queries"""
        # Get academic year object
        self.academic_year_obj = AcademicYear.query.filter_by(
            year=self.academic_year_str
        ).first()
        
        if not self.academic_year_obj:
            from datetime import date
            start_year = int(self.academic_year_str.split('-')[0])
            end_year = int(self.academic_year_str.split('-')[1])
            self.academic_year_obj = AcademicYear(
                year=self.academic_year_str,
                start_date=date(start_year, 6, 1),
                end_date=date(end_year, 4, 30),
                is_current=True
            )
            db.session.add(self.academic_year_obj)
            db.session.flush()
        
        # Get department
        department = Department.query.get(self.department_id)
        dept_name = department.name if department else None
        
        # Get all teachers in the department
        self.teachers = User.query.filter_by(
            role='teacher',
            department_id=self.department_id,
            is_active=True
        ).all()
        
        print(f"\nFound {len(self.teachers)} teachers in {dept_name}")
        
        # Get ALL subjects for this department
        all_subjects = Subject.query.filter_by(
            department_id=self.department_id
        ).all()
        
        # Fix: Map subjects to correct semesters based on helpers.py
        self.subjects = []
        semester_map = {}
        
        # Create a mapping of subject name to correct semester from helpers
        if dept_name and dept_name in DEPARTMENTS:
            print(f"\nMapping subjects to correct semesters from helpers.py:")
            for sem_num, subject_names in DEPARTMENTS[dept_name].items():
                if sem_num in self.even_semesters:  # Only even semesters
                    print(f"   Semester {sem_num}: {len(subject_names)} subjects")
                    for subject_name in subject_names:
                        # Find this subject in database
                        for subject in all_subjects:
                            if subject.name == subject_name:
                                # Check if it needs to be updated
                                if subject.semester_id != sem_num:
                                    print(f"      Fixing: {subject_name} from Sem {subject.semester_id} -> Sem {sem_num}")
                                    subject.semester_id = sem_num
                                self.subjects.append(subject)
                                semester_map[subject.id] = sem_num
                                break
        
        # Commit any semester fixes
        if semester_map:
            db.session.commit()
            print(f"\nFixed semester mapping for {len(semester_map)} subjects")
        
        # If no subjects found from helpers, use all subjects (fallback)
        if not self.subjects:
            self.subjects = [s for s in all_subjects if s.semester_id in self.even_semesters]
            print(f"\nFallback: Found {len(self.subjects)} subjects in even semesters")
        
        # Group subjects by semester
        for subject in self.subjects:
            self.subjects_by_semester[subject.semester_id].append(subject)
        
        # Print subjects per semester after fixing
        print(f"\nSubjects by Semester (After Fixing):")
        for sem in self.even_semesters:
            count = len(self.subjects_by_semester.get(sem, []))
            if count > 0:
                print(f"   Semester {sem}: {count} subjects")
                for subject in self.subjects_by_semester.get(sem, [])[:3]:  # Show first 3
                    print(f"      - {subject.name}")
        
        # Get ALL active assignments for this department
        all_assignments = TeacherSubject.query.filter(
            TeacherSubject.academic_year_id == self.academic_year_obj.id,
            TeacherSubject.is_active == True
        ).all()
        
        # Create a set of assigned subject IDs
        self.assigned_subjects = {a.subject_id for a in all_assignments}
        
        # Calculate teacher workload
        self.teacher_workload = {}
        for assignment in all_assignments:
            teacher_id = assignment.teacher_id
            self.teacher_workload[teacher_id] = self.teacher_workload.get(teacher_id, 0) + 1
        
        # Print current workload
        print("\nCurrent Workload:")
        for teacher in self.teachers:
            workload = self.teacher_workload.get(teacher.id, 0)
            print(f"   {teacher.full_name}: {workload}/{self.max_subjects_per_teacher} subjects")
    
    def assign_teachers_fast(self):
        """Fast AI assignment algorithm for even semesters only"""
        self.load_data_fast()
        
        if not self.teachers:
            return {
                'success': False,
                'message': 'No teachers found in department',
                'assignments': []
            }
        
        if not self.subjects:
            return {
                'success': False,
                'message': f'No subjects found for even semesters {self.even_semesters}',
                'assignments': []
            }
        
        assignments = []
        failed_subjects = []
        
        # Track assignments per teacher
        teacher_assignment_count = {teacher.id: self.teacher_workload.get(teacher.id, 0) for teacher in self.teachers}
        
        print(f"\nAI Assigning subjects for even semesters {self.even_semesters}...")
        
        # Process each even semester separately
        for semester_id in sorted(self.even_semesters):
            subjects = self.subjects_by_semester.get(semester_id, [])
            if not subjects:
                print(f"\n   Semester {semester_id}: No subjects found")
                continue
            
            # Get unassigned subjects for this semester
            unassigned = [s for s in subjects if s.id not in self.assigned_subjects]
            
            if not unassigned:
                print(f"\n   Semester {semester_id}: All {len(subjects)} subjects already assigned")
                continue
            
            print(f"\n   Semester {semester_id}: {len(unassigned)} subjects to assign")
            
            # Create a pool of available teachers
            available_teachers = []
            for teacher in self.teachers:
                current_load = teacher_assignment_count.get(teacher.id, 0)
                if current_load < self.max_subjects_per_teacher:
                    slots_left = self.max_subjects_per_teacher - current_load
                    available_teachers.extend([teacher] * slots_left)
            
            random.shuffle(available_teachers)
            
            if not available_teachers:
                print(f"      Warning: No teachers available")
                failed_subjects.extend([s.name for s in unassigned])
                continue
            
            print(f"      Available teacher slots: {len(available_teachers)}")
            
            # Assign subjects
            for i, subject in enumerate(unassigned):
                if not available_teachers:
                    print(f"      Warning: Ran out of teachers")
                    failed_subjects.extend([s.name for s in unassigned[i:]])
                    break
                
                teacher = available_teachers.pop(0)
                
                assignment = TeacherSubject(
                    teacher_id=teacher.id,
                    subject_id=subject.id,
                    academic_year_id=self.academic_year_obj.id,
                    semester_id=subject.semester_id,  # This will now be correct (2,4,6,8)
                    is_active=True
                )
                assignments.append(assignment)
                
                teacher_assignment_count[teacher.id] += 1
                self.assigned_subjects.add(subject.id)
                
                print(f"      + Sem {subject.semester_id}: {subject.name[:30]:30} -> {teacher.full_name}")
        
        # Print final distribution
        print("\n" + "="*60)
        print("FINAL ASSIGNMENT DISTRIBUTION")
        print("="*60)
        
        # Group by semester for final summary
        final_by_semester = defaultdict(list)
        for subject_id in self.assigned_subjects:
            subject = Subject.query.get(subject_id)
            if subject and subject.semester_id in self.even_semesters:
                final_by_semester[subject.semester_id].append(subject.name)
        
        for sem in sorted(self.even_semesters):
            if final_by_semester[sem]:
                print(f"\nSemester {sem}: {len(final_by_semester[sem])} subjects")
                for subject in final_by_semester[sem][:3]:
                    print(f"   - {subject}")
        
        print("\nTeacher Workload:")
        for teacher in self.teachers:
            final_count = teacher_assignment_count.get(teacher.id, 0)
            print(f"   {teacher.full_name}: {final_count}/{self.max_subjects_per_teacher} subjects")
        
        print(f"\nTotal new assignments: {len(assignments)}")
        
        return {
            'success': True,
            'assignments': assignments,
            'failed_subjects': failed_subjects,
            'total_assigned': len(assignments),
            'teacher_distribution': {
                teacher.full_name: teacher_assignment_count.get(teacher.id, 0)
                for teacher in self.teachers
            }
        }
    
    def reset_assignments_fast(self):
        """Reset all active assignments"""
        self.load_data_fast()
        
        # Get subject IDs for even semesters
        subject_ids = [s.id for s in self.subjects]
        
        # Reset assignments
        result = TeacherSubject.query.filter(
            TeacherSubject.academic_year_id == self.academic_year_obj.id,
            TeacherSubject.is_active == True,
            TeacherSubject.subject_id.in_(subject_ids)
        ).update({'is_active': False}, synchronize_session=False)
        
        db.session.commit()
        
        print(f"\nReset {result} assignments")
        return result
    
    def get_assignment_stats_fast(self):
        """Get assignment statistics"""
        self.load_data_fast()
        
        stats = {
            'total_teachers': len(self.teachers),
            'total_subjects': len(self.subjects),
            'assigned_subjects': len(self.assigned_subjects),
            'unassigned_subjects': len(self.subjects) - len(self.assigned_subjects),
            'teacher_workload': {},
            'average_workload': 0,
            'max_capacity': self.max_subjects_per_teacher,
            'subjects_per_semester': {}
        }
        
        # Subjects per semester
        for sem in self.even_semesters:
            count = len(self.subjects_by_semester.get(sem, []))
            if count > 0:
                stats['subjects_per_semester'][f"Semester {sem}"] = count
        
        # Calculate workload
        total = 0
        for teacher in self.teachers:
            workload = self.teacher_workload.get(teacher.id, 0)
            stats['teacher_workload'][teacher.full_name] = workload
            total += workload
        
        if self.teachers:
            stats['average_workload'] = round(total / len(self.teachers), 2)
        
        return stats