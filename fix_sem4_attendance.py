#!/usr/bin/env python

import sys
from pathlib import Path
from datetime import datetime
import random

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app
from extensions import db
from model import Student, Attendance, TeacherSubject

SEMESTER = 4
TOTAL_CLASSES = 20
MONTH = 2
YEAR = 2026

def fix():

    app = create_app("development")

    with app.app_context():

        students = Student.query.filter_by(current_semester=SEMESTER).all()

        teacher_subject = TeacherSubject.query.filter_by(
            semester_id=SEMESTER,
            is_active=True
        ).first()

        if not teacher_subject:
            print("No teacher subject mapping found")
            return

        subject_id = teacher_subject.subject_id
        teacher_id = teacher_subject.teacher_id

        for s in students:

            # delete old
            Attendance.query.filter_by(
                student_id=s.id,
                semester=SEMESTER
            ).delete()

            attended = random.randint(8, 20)
            percent = round((attended / TOTAL_CLASSES) * 100, 1)

            attendance = Attendance(
                student_id=s.id,
                subject_id=subject_id,
                teacher_id=teacher_id,
                total_classes=TOTAL_CLASSES,
                attended_classes=attended,
                attendance_percentage=percent,
                penalty_status="No Penalty",
                penalty_amount=0,
                month=MONTH,
                year=YEAR,
                semester=SEMESTER
            )

            db.session.add(attendance)

        db.session.commit()

        print("✅ Semester 4 attendance fixed successfully")

if __name__ == "__main__":
    fix()