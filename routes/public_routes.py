# routes/public_routes.py
from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@public_bp.route('/exam-timetable')
def exam_timetable():
    """Public exam timetable page"""
    return render_template('public/exam_timetable.html', title='Exam Timetable')

@public_bp.route('/room-allocation')
def room_allocation():
    """Public room allocation page"""
    return render_template('public/room_allocation.html', title='Room Allocation')

@public_bp.route('/invigilator-list')
def invigilator_list():
    """Public invigilator list page"""
    return render_template('public/invigilator_list.html', title='Invigilator List')

@public_bp.route('/notifications')
def notifications():
    """Public notifications page"""
    return render_template('public/notifications.html', title='Notifications')