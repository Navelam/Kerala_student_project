# routes/auth_routes.py
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from utils.ai_allocator import TeacherSubjectAllocator
from extensions import db, login_manager
from model import User  # Remove Notification import temporarily

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID"""
    return db.session.get(User, int(user_id))

def get_roles():
    """Get all available roles for dropdown"""
    return [
        {'value': 'student', 'label': 'Student'},
        {'value': 'teacher', 'label': 'Teacher'},
        {'value': 'hod', 'label': 'Head of Department (HOD)'},
        {'value': 'coordinator', 'label': 'Coordinator'},
        {'value': 'principal', 'label': 'Principal'}
    ]

# =====================================================
# LOGIN ROUTE - FIXED VERSION
# =====================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with role selection - FIXED REDIRECT ISSUE"""
    # If user is already logged in, redirect to their dashboard
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_role = request.form.get('role')
        remember = True if request.form.get('remember') else False

        # Validation
        if not username or not password or not selected_role:
            flash('Please fill in all fields and select a role', 'warning')
            return render_template('auth/login.html', roles=get_roles())

        # Find user based on username/email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        # Check if user exists
        if not user:
            flash('Invalid credentials', 'danger')
            return render_template('auth/login.html', roles=get_roles())

        # Verify password
        if not check_password_hash(user.password_hash, password):
            flash('Invalid credentials', 'danger')
            return render_template('auth/login.html', roles=get_roles())

        # CRITICAL: Verify the user's role matches the selected role
        if user.role != selected_role:
            flash(f'This account is registered as {user.role}, not as {selected_role}', 'danger')
            return render_template('auth/login.html', roles=get_roles())

        # Check if account is active
        if not user.is_active:
            flash('Your account is deactivated. Please contact administrator.', 'warning')
            return render_template('auth/login.html', roles=get_roles())

        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Login the user
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')

        # Redirect based on user role
        return redirect_to_dashboard(user)

    # GET request - show login form
    return render_template('auth/login.html', roles=get_roles())

def redirect_to_dashboard(user):
    """Redirect user to their respective dashboard based on role"""
    if user.role == 'student':
        return redirect(url_for('student.dashboard'))
    elif user.role == 'teacher':
        return redirect(url_for('teacher.dashboard'))
    elif user.role == 'hod':
        return redirect(url_for('hod.dashboard'))
    elif user.role == 'coordinator':
        return redirect(url_for('coordinator.dashboard'))
    elif user.role == 'principal':
        return redirect(url_for('principal.dashboard'))
    else:
        # Fallback for unknown roles
        return redirect(url_for('public.index'))

# =====================================================
# DASHBOARD REDIRECT
# =====================================================

@auth_bp.route('/dashboard-redirect')
@login_required
def dashboard_redirect():
    """Redirect user to their respective dashboard based on role"""
    return redirect_to_dashboard(current_user)

# =====================================================
# LOGOUT
# =====================================================

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

# =====================================================
# PROFILE ROUTES
# =====================================================

@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile"""
    return render_template('auth/profile.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))

        if len(new_password) < 3:
            flash('Password must be at least 3 characters long', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html')

# =====================================================
# NOTIFICATION ROUTES
# =====================================================

@auth_bp.route('/notifications')
@login_required
def notifications():
    """View user notifications"""
    return render_template('auth/notifications.html')

# =====================================================
# FORGOT PASSWORD
# =====================================================

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password request"""
    if request.method == 'POST':
        email = request.form.get('email')
        flash('Password reset instructions have been sent to your email.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

# =====================================================
# REGISTER ROUTE
# =====================================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)
    
    if request.method == 'POST':
        # This is simplified - you can expand as needed
        flash('Registration is currently disabled. Please contact administrator.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', roles=get_roles())

# =====================================================
# CONTEXT PROCESSOR
# =====================================================

@auth_bp.context_processor
def utility_processor():
    """Add utility functions to template context"""
    return {
        'now': datetime.now()
    }
@auth_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Update user
        current_user.full_name = full_name
        current_user.email = email
        current_user.phone = phone
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('hod.profile' if current_user.role == 'hod' else 'teacher.dashboard'))
    
    return render_template('auth/edit_profile.html')