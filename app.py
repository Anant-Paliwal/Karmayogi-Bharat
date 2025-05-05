import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure PostgreSQL database
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///karmayogi.db"
    logger.warning("DATABASE_URL not found, using SQLite database instead")

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import recommender functionality
from recommender import generate_recommendations, get_competencies_for_role
from data_processor import load_all_data, get_designations, get_ministries

# Create all tables and seed the database
with app.app_context():
    # Import models
    from models import User, Course, Competency, Role, UserCourse
    
    # Create tables if they don't exist
    db.create_all()
    
    # Import and run database seeder
    from db_seeder import seed_database
    seed_database()

# Load initial data from database
courses, roles, competencies = load_all_data()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Form classes
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    designation = SelectField('Designation', validators=[DataRequired()])
    ministry = SelectField('Ministry', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one or login.')

# Routes
@app.route('/')
def index():
    """Render the home page"""
    designations = get_designations()
    ministries = get_ministries()
    return render_template('index.html', designations=designations, ministries=ministries)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    # Populate the form with dynamic choices for designation and ministry
    form.designation.choices = [(d, d) for d in get_designations()]
    form.ministry.choices = [(m, m) for m in get_ministries()]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            designation=form.designation.data,
            ministry=form.ministry.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        
        return redirect(next_page)
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get all courses the user is enrolled in
    enrolled_courses = UserCourse.query.filter_by(user_id=current_user.id).all()
    
    # Get the full course objects
    courses_with_progress = []
    for enrollment in enrolled_courses:
        course = Course.query.get(enrollment.course_id)
        if course:
            courses_with_progress.append({
                'course': course,
                'progress': enrollment.progress,
                'completed': enrollment.completed,
                'enrolled_at': enrollment.enrolled_at
            })
    
    return render_template('profile.html', 
                           user=current_user, 
                           courses=courses_with_progress)

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """API endpoint to get recommendations based on designation and ministry"""
    try:
        data = request.json
        designation = data.get('designation')
        ministry = data.get('ministry')
        
        if not designation or not ministry:
            return jsonify({
                'error': 'Missing designation or ministry'
            }), 400
        
        # Get competencies for this role
        logger.debug(f"Getting competencies for designation={designation}, ministry={ministry}")
        competencies = get_competencies_for_role(designation, ministry)
        
        # Generate learning path recommendations
        logger.debug(f"Generating recommendations for competencies: {competencies}")
        recommendations = generate_recommendations(designation, ministry, competencies)
        
        return jsonify({
            'competencies': competencies,
            'learning_path': recommendations
        })
    except Exception as e:
        logger.exception("Error generating recommendations")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/recommendations', methods=['GET'])
def show_recommendations():
    """Render the recommendations page"""
    designation = request.args.get('designation')
    ministry = request.args.get('ministry')
    
    if not designation or not ministry:
        return render_template('index.html', error="Please select both designation and ministry")
    
    # Get competencies for this role
    competencies = get_competencies_for_role(designation, ministry)
    
    # Generate learning path recommendations
    recommendations = generate_recommendations(designation, ministry, competencies)
    
    # Check which courses the user is already enrolled in (if logged in)
    enrolled_course_ids = []
    if current_user.is_authenticated:
        enrollments = UserCourse.query.filter_by(user_id=current_user.id).all()
        enrolled_course_ids = [enrollment.course_id for enrollment in enrollments]
    
    return render_template(
        'recommendations.html',
        designation=designation,
        ministry=ministry,
        competencies=competencies,
        recommendations=recommendations,
        enrolled_course_ids=enrolled_course_ids
    )

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    """Course detail page"""
    course = Course.query.get_or_404(course_id)
    
    # Get competencies for this course
    competency_ids = course.competency_ids.split(',') if course.competency_ids else []
    competencies = []
    
    for comp_id in competency_ids:
        comp = Competency.query.get(comp_id)
        if comp:
            competencies.append(comp)
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    if current_user.is_authenticated:
        enrollment = UserCourse.query.filter_by(
            user_id=current_user.id, 
            course_id=course_id
        ).first()
        is_enrolled = enrollment is not None
    
    return render_template(
        'course_detail.html',
        course=course,
        competencies=competencies,
        is_enrolled=is_enrolled,
        enrollment=enrollment
    )

@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll in a course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = UserCourse.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash(f'You are already enrolled in "{course.title}"', 'info')
    else:
        # Create new enrollment
        enrollment = UserCourse(
            user_id=current_user.id,
            course_id=course_id,
            progress=0.0,
            completed=False
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        flash(f'Successfully enrolled in "{course.title}"', 'success')
    
    # Redirect back to course detail
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/unenroll/<int:course_id>', methods=['POST'])
@login_required
def unenroll_course(course_id):
    """Unenroll from a course"""
    course = Course.query.get_or_404(course_id)
    
    # Find enrollment
    enrollment = UserCourse.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
        flash(f'Successfully unenrolled from "{course.title}"', 'success')
    else:
        flash(f'You are not enrolled in "{course.title}"', 'warning')
    
    # Redirect back to course detail
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/update_progress/<int:course_id>', methods=['POST'])
@login_required
def update_progress(course_id):
    """Update course progress"""
    # Find enrollment
    enrollment = UserCourse.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first_or_404()
    
    # Update progress
    new_progress = float(request.form.get('progress', 0))
    new_progress = max(0, min(100, new_progress))  # Ensure between 0-100
    
    enrollment.progress = new_progress
    enrollment.completed = new_progress >= 100
    enrollment.last_accessed = datetime.utcnow()
    
    db.session.commit()
    
    flash('Progress updated successfully', 'success')
    return redirect(url_for('course_detail', course_id=course_id))
