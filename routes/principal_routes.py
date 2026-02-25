# routes/principal_routes.py
from flask import Blueprint, render_template
from flask_login import login_required

principal_bp = Blueprint('principal', __name__, template_folder='templates/principal')

@principal_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('principal/dashboard.html')

@principal_bp.route('/analytics')
@login_required
def analytics():
    return render_template('principal/analytics.html')