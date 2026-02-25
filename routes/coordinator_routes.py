# routes/coordinator_routes.py
from flask import Blueprint, render_template
from flask_login import login_required

coordinator_bp = Blueprint('coordinator', __name__, template_folder='templates/coordinator')

@coordinator_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('coordinator/dashboard.html')

@coordinator_bp.route('/create_timetable')
@login_required
def create_timetable():
    return render_template('coordinator/create_timetable.html')

@coordinator_bp.route('/room_allocation')
@login_required
def room_allocation():
    return render_template('coordinator/room_allocation.html')

@coordinator_bp.route('/invigilator_allocation')
@login_required
def invigilator_allocation():
    return render_template('coordinator/invigilator_allocation.html')