from flask import Flask, render_template
from config import config
from extensions import db, login_manager, migrate, mail
import os
from datetime import datetime
import gc
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
      from model import User  # Changed from 'models' to 'model'
      return User.query.get(int(user_id))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Context processor for templates
    @app.context_processor
    def utility_processor():
        return {'now': datetime.now()}
    @app.after_request
    def after_request(response):
    # Force garbage collection
     gc.collect()
     return response
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.principal_routes import principal_bp
    from routes.hod_routes import hod_bp
    from routes.teacher_routes import teacher_bp
    from routes.student_routes import student_bp
    from routes.coordinator_routes import coordinator_bp
    from routes.public_routes import public_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(principal_bp, url_prefix='/principal')
    app.register_blueprint(hod_bp, url_prefix='/hod')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(coordinator_bp, url_prefix='/coordinator')
    app.register_blueprint(public_bp)  # No prefix for public routes

    # Create upload directories
    with app.app_context():
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(os.path.join(upload_dir, 'profile_pics'), exist_ok=True)
        os.makedirs(os.path.join(upload_dir, 'question_papers'), exist_ok=True)
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)