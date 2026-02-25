# routes/student_routes.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from model import (
    User, Student, Subject, StudentPerformance, 
    AcademicYear, Department
)
from datetime import datetime

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    """Decorator to restrict access to students only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied. Student privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def calculate_grade(final_marks):
    """Calculate grade based on final marks (out of 20)"""
    if final_marks >= 18:
        return 'A+'
    elif final_marks >= 15:
        return 'A'
    elif final_marks >= 12:
        return 'B'
    elif final_marks >= 10:
        return 'C'
    else:
        return 'D'

def calculate_percentage(final_marks):
    """Calculate percentage from final marks"""
    return int((final_marks / 20) * 100)

def get_student_record(user_id):
    """Get student record for current user"""
    return Student.query.filter_by(user_id=user_id).first()

def get_feedback_by_risk(risk):
    """Get feedback message based on risk status"""
    feedback = {
        'Critical': {
            'message': 'You are in Critical level. Please concentrate more on your studies. Attend classes regularly.',
            'color': 'danger',
            'bg': '#dc3545',
            'text': 'white',
            'icon': 'exclamation-triangle'
        },
        'Average': {
            'message': 'You are Average. Try harder to improve. Focus on weak subjects.',
            'color': 'warning',
            'bg': '#ffc107',
            'text': '#2c3e50',
            'icon': 'exclamation-circle'
        },
        'Safe': {
            'message': 'You are Safe. Keep studying regularly. Maintain consistency.',
            'color': 'success',
            'bg': '#28a745',
            'text': 'white',
            'icon': 'check-circle'
        },
        'Best': {
            'message': 'Excellent Performance! Keep it up and aim higher.',
            'color': 'best',
            'bg': '#6f42c1',
            'text': 'white',
            'icon': 'star'
        }
    }
    return feedback.get(risk, feedback['Safe'])

# =====================================================
# STUDENT DASHBOARD
# =====================================================

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard showing overview"""
    student = get_student_record(current_user.id)
    
    if not student:
        flash('Student record not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all performances for this student
    performances = StudentPerformance.query.filter_by(
        student_id=student.id
    ).all()
    
    # Calculate overall statistics
    total_attendance = 0
    total_marks = 0
    subject_count = len(performances)
    
    risk_counts = {'Critical': 0, 'Average': 0, 'Safe': 0, 'Best': 0}
    
    for perf in performances:
        total_attendance += perf.attendance
        total_marks += perf.final_internal
        risk_counts[perf.risk_status] = risk_counts.get(perf.risk_status, 0) + 1
    
    avg_attendance = round(total_attendance / subject_count, 1) if subject_count > 0 else 0
    avg_marks = round(total_marks / subject_count, 1) if subject_count > 0 else 0
    overall_grade = calculate_grade(avg_marks)
    
    # Determine overall risk based on average
    if avg_attendance < 70 or avg_marks < 10:
        overall_risk = 'Critical'
    elif avg_marks < 12:
        overall_risk = 'Average'
    elif avg_marks >= 18 and avg_attendance >= 90:
        overall_risk = 'Best'
    else:
        overall_risk = 'Safe'
    
    # Prepare chart data
    chart_labels = []
    chart_data = []
    chart_colors = []
    
    for perf in performances[:10]:
        subject = Subject.query.get(perf.subject_id)
        if subject:
            chart_labels.append(subject.name[:15] + ('...' if len(subject.name) > 15 else ''))
            chart_data.append(perf.final_internal)
            
            if perf.risk_status == 'Critical':
                chart_colors.append('#dc3545')
            elif perf.risk_status == 'Average':
                chart_colors.append('#ffc107')
            elif perf.risk_status == 'Safe':
                chart_colors.append('#28a745')
            else:
                chart_colors.append('#6f42c1')
    
    import json
    return render_template('student/dashboard.html',
                         student=student,
                         avg_attendance=avg_attendance,
                         avg_marks=avg_marks,
                         overall_grade=overall_grade,
                         overall_risk=overall_risk,
                         risk_counts=risk_counts,
                         chart_labels=json.dumps(chart_labels),
                         chart_data=json.dumps(chart_data),
                         chart_colors=json.dumps(chart_colors),
                         now=datetime.now())


# =====================================================
# STUDENT PERFORMANCE DETAILS (WITH DIRECT FEEDBACK)
# =====================================================

@student_bp.route('/performance')
@login_required
@student_required
def performance():
    """Detailed performance view with subject-wise feedback"""
    student = get_student_record(current_user.id)
    
    if not student:
        flash('Student record not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all performances for this student
    performances = StudentPerformance.query.filter_by(
        student_id=student.id
    ).order_by(StudentPerformance.semester).all()
    
    # Prepare performance data with subject details and feedback
    performance_data = []
    for perf in performances:
        subject = Subject.query.get(perf.subject_id)
        if subject:
            percentage = calculate_percentage(perf.final_internal)
            grade = calculate_grade(perf.final_internal)
            
            # Get feedback based on risk
            feedback = get_feedback_by_risk(perf.risk_status)
            
            # Calculate marks needed for next grade
            if perf.final_internal >= 18:
                next_grade = "A+ (Max)"
                marks_needed = 0
            elif perf.final_internal >= 15:
                next_grade = "A+"
                marks_needed = round(18 - perf.final_internal, 1)
            elif perf.final_internal >= 12:
                next_grade = "A"
                marks_needed = round(15 - perf.final_internal, 1)
            elif perf.final_internal >= 10:
                next_grade = "B"
                marks_needed = round(12 - perf.final_internal, 1)
            else:
                next_grade = "C (Pass)"
                marks_needed = round(10 - perf.final_internal, 1)
            
            performance_data.append({
                'id': perf.id,
                'subject': subject,
                'internal1': perf.internal1,
                'internal2': perf.internal2,
                'seminar': perf.seminar,
                'assessment': perf.assessment,
                'attendance': perf.attendance,
                'final_marks': perf.final_internal,
                'percentage': percentage,
                'grade': grade,
                'risk_status': perf.risk_status,
                'semester': perf.semester,
                'feedback': feedback,
                'next_grade': next_grade,
                'marks_needed': marks_needed
            })
    
    # Group by semester
    performances_by_semester = {}
    for perf in performance_data:
        sem = perf['semester']
        if sem not in performances_by_semester:
            performances_by_semester[sem] = []
        performances_by_semester[sem].append(perf)
    
    return render_template('student/performance.html',
                         student=student,
                         performances=performance_data,
                         performances_by_semester=performances_by_semester,
                         now=datetime.now())


# =====================================================
# STUDENT NOTIFICATIONS (OPTIONAL - CAN BE REMOVED)
# =====================================================

@student_bp.route('/notifications')
@login_required
@student_required
def notifications():
    """Redirect to performance page since we're using direct feedback"""
    return redirect(url_for('student.performance'))


# =====================================================
# API ENDPOINTS
# =====================================================

@student_bp.route('/api/performance-summary')
@login_required
@student_required
def performance_summary():
    """API endpoint for performance summary charts"""
    student = get_student_record(current_user.id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get performances
    performances = StudentPerformance.query.filter_by(
        student_id=student.id
    ).all()
    
    # Prepare data
    subjects = []
    marks = []
    attendance = []
    colors = []
    
    for perf in performances[:10]:
        subject = Subject.query.get(perf.subject_id)
        if subject:
            subjects.append(subject.name[:15])
            marks.append(perf.final_internal)
            attendance.append(perf.attendance)
            
            if perf.risk_status == 'Critical':
                colors.append('#dc3545')
            elif perf.risk_status == 'Average':
                colors.append('#ffc107')
            elif perf.risk_status == 'Safe':
                colors.append('#28a745')
            else:
                colors.append('#6f42c1')
    
    return jsonify({
        'subjects': subjects,
        'marks': marks,
        'attendance': attendance,
        'colors': colors
    })