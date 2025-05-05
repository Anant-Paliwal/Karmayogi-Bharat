from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    ministry = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with UserCourse
    enrollments = db.relationship('UserCourse', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'designation': self.designation,
            'ministry': self.ministry,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Define the Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    provider = db.Column(db.String(100))
    domain = db.Column(db.String(100))
    competency_ids = db.Column(db.String(255))  # Comma-separated IDs
    level = db.Column(db.String(50))  # Beginner, Intermediate, Advanced
    duration_hours = db.Column(db.Float)
    course_type = db.Column(db.String(50))  # Video, Interactive, etc.
    
    # Relationship with UserCourse
    enrollments = db.relationship('UserCourse', backref='course', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'provider': self.provider,
            'domain': self.domain,
            'competency_ids': self.competency_ids.split(',') if self.competency_ids else [],
            'level': self.level,
            'duration_hours': self.duration_hours,
            'course_type': self.course_type
        }

# Define the UserCourse model for enrollments
class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Float, default=0.0)  # 0.0 to 100.0 percent
    completed = db.Column(db.Boolean, default=False)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'progress': self.progress,
            'completed': self.completed,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }

# Define the Competency model
class Competency(db.Model):
    id = db.Column(db.String(10), primary_key=True)  # Using string ID like "B001"
    code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))  # Behavioral, Functional, Domain
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'type': self.type
        }

# Define the Role model
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(255), nullable=False)
    ministry = db.Column(db.String(255), nullable=False)
    competency_ids = db.Column(db.String(255))  # Comma-separated IDs
    
    def to_dict(self):
        return {
            'id': self.id,
            'designation': self.designation,
            'ministry': self.ministry,
            'competency_ids': self.competency_ids.split(',') if self.competency_ids else []
        }
