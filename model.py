# model.py - Fix the StudentPerformance model
from datetime import datetime
from extensions import db
from flask_login import UserMixin

# =====================================================
# USER MODEL (All Roles)
# =====================================================

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Personal info
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    
    # Role and department
    role = db.Column(db.String(20), nullable=False)  # student/teacher/hod/coordinator/principal
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', back_populates='users', foreign_keys=[department_id])
    student_record = db.relationship('Student', back_populates='user', uselist=False)
    teacher_subjects = db.relationship('TeacherSubject', back_populates='teacher', lazy='dynamic')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic')
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False


# =====================================================
# DEPARTMENT MODEL
# =====================================================

class Department(db.Model):
    __tablename__ = "departments"
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hod_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    hod = db.relationship('User', foreign_keys=[hod_id], post_update=True)
    users = db.relationship('User', back_populates='department', foreign_keys='User.department_id')
    courses = db.relationship('Course', back_populates='department', lazy=True)
    subjects = db.relationship('Subject', back_populates='department', lazy=True)
    students = db.relationship('Student', back_populates='department', lazy=True)


# =====================================================
# COURSE MODEL
# =====================================================

class Course(db.Model):
    __tablename__ = "courses"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    duration_years = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', back_populates='courses')
    semesters = db.relationship('Semester', back_populates='course', lazy=True)
    students = db.relationship('Student', back_populates='course', lazy=True)


# =====================================================
# ACADEMIC YEAR MODEL
# =====================================================

class AcademicYear(db.Model):
    __tablename__ = "academic_years"
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(20), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    semesters = db.relationship('Semester', back_populates='academic_year', lazy=True)
    performances = db.relationship('StudentPerformance', back_populates='academic_year', lazy=True)


# =====================================================
# SEMESTER MODEL
# =====================================================

class Semester(db.Model):
    __tablename__ = "semesters"
    
    id = db.Column(db.Integer, primary_key=True)
    semester_number = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', back_populates='semesters')
    academic_year = db.relationship('AcademicYear', back_populates='semesters')
    subjects = db.relationship('Subject', back_populates='semester', lazy=True)


# =====================================================
# SUBJECT MODEL
# =====================================================

class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    credits = db.Column(db.Integer, default=3)
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', back_populates='subjects')
    semester = db.relationship('Semester', back_populates='subjects')
    teacher_assignments = db.relationship('TeacherSubject', back_populates='subject', lazy=True)
    student_performances = db.relationship('StudentPerformance', back_populates='subject', lazy=True)


# =====================================================
# TEACHER-SUBJECT ASSIGNMENT
# =====================================================

class TeacherSubject(db.Model):
    __tablename__ = "teacher_subjects"
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', back_populates='teacher_subjects')
    subject = db.relationship('Subject', back_populates='teacher_assignments')
    academic_year = db.relationship('AcademicYear')
    semester = db.relationship('Semester')


# =====================================================
# STUDENT MODEL
# =====================================================

class Student(db.Model):
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    current_semester = db.Column(db.Integer, default=1)
    batch_year = db.Column(db.Integer, nullable=False)
    admission_date = db.Column(db.Date, nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='student_record')
    course = db.relationship('Course', back_populates='students')
    department = db.relationship('Department', back_populates='students')
    performances = db.relationship('StudentPerformance', back_populates='student', lazy=True)


# =====================================================
# STUDENT PERFORMANCE MODEL - FIXED (NO teacher_id)
# =====================================================

class StudentPerformance(db.Model):
    __tablename__ = "student_performances"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    attendance = db.Column(db.Float, nullable=False, default=0)  # Percentage
    internal1 = db.Column(db.Float, nullable=False, default=0)   # Marks out of 20
    internal2 = db.Column(db.Float, nullable=False, default=0)   # Marks out of 20
    seminar = db.Column(db.Float, nullable=False, default=0)     # Marks out of 5
    assessment = db.Column(db.Float, nullable=False, default=0)  # Marks out of 5
    
    total_marks = db.Column(db.Float, nullable=False, default=0)  # Out of 50
    final_internal = db.Column(db.Float, nullable=False, default=0)  # Converted to 25
    
    risk_status = db.Column(db.String(20), nullable=False, default='Safe')
    predicted_risk_probability = db.Column(db.Float, nullable=True)
    
    semester = db.Column(db.Integer, nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - NO teacher_id relationship
    student = db.relationship('Student', back_populates='performances')
    subject = db.relationship('Subject', back_populates='student_performances')
    academic_year = db.relationship('AcademicYear', back_populates='performances')
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'academic_year_id', 
                           name='unique_student_subject_per_year'),
    )


# =====================================================
# NOTIFICATION MODEL
# =====================================================

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for broadcast
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    type = db.Column(db.String(50), nullable=False)  # info / success / warning / danger
    target_role = db.Column(db.String(20), nullable=True)  # student/teacher/etc., null for all
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')


# =====================================================
# EXAM TIMETABLE
# =====================================================

class ExamTimetable(db.Model):
    __tablename__ = "exam_timetables"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    exam_type = db.Column(db.String(20), nullable=False)  # Internal1 / Internal2 / Semester
    exam_date = db.Column(db.Date, nullable=False)
    session = db.Column(db.String(10), nullable=False)  # 10AM or 2PM
    duration = db.Column(db.Integer, default=180)  # minutes

    status = db.Column(db.String(20), default="Pending")  # Pending / Approved

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    subject = db.relationship('Subject')
    department = db.relationship('Department')
    creator = db.relationship('User', foreign_keys=[created_by])


# =====================================================
# ROOM ALLOCATION
# =====================================================

class RoomAllocation(db.Model):
    __tablename__ = "room_allocations"

    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('exam_timetables.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    room_number = db.Column(db.String(20), nullable=False)
    block = db.Column(db.String(50), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    timetable = db.relationship('ExamTimetable')
    student = db.relationship('Student')


# =====================================================
# INVIGILATOR ASSIGNMENT
# =====================================================

class InvigilatorAssignment(db.Model):
    __tablename__ = "invigilator_assignments"

    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('exam_timetables.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    room_number = db.Column(db.String(20), nullable=False)
    block = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    timetable = db.relationship('ExamTimetable')
    teacher = db.relationship('User', foreign_keys=[teacher_id])


# =====================================================
# ATTENDANCE MODEL
# =====================================================

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Attendance data
    total_classes = db.Column(db.Integer, nullable=False, default=0)
    attended_classes = db.Column(db.Integer, nullable=False, default=0)
    attendance_percentage = db.Column(db.Integer, nullable=False, default=0)
    
    # Penalty
    penalty_amount = db.Column(db.Integer, nullable=False, default=0)
    penalty_status = db.Column(db.String(20), nullable=False, default='No Penalty')
    
    # Month and Semester tracking
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    
    # ML Prediction
    predicted_attendance_trend = db.Column(db.Float, nullable=True)
    risk_of_dropout = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student')
    subject = db.relationship('Subject')
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'month', 'year', 
                           name='unique_attendance_per_month'),
    )
    
    def calculate_penalty(self):
        """Calculate penalty based on attendance percentage"""
        if self.attendance_percentage >= 75:
            self.penalty_amount = 0
            self.penalty_status = 'No Penalty'
        elif self.attendance_percentage >= 70:
            self.penalty_amount = 200
            self.penalty_status = 'Low Penalty'
        elif self.attendance_percentage >= 60:
            self.penalty_amount = 500
            self.penalty_status = 'Medium Penalty'
        else:
            self.penalty_amount = 1000
            self.penalty_status = 'High Penalty'
        return self.penalty_amount


# =====================================================
# QUESTION PAPER MODEL
# =====================================================

class QuestionPaper(db.Model):
    __tablename__ = "question_papers"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_type = db.Column(db.String(20), nullable=False)

    file_path = db.Column(db.String(255), nullable=False)
    answer_key_path = db.Column(db.String(255), nullable=True)
    
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subject = db.relationship('Subject')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
