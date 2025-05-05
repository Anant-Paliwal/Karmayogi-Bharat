import os
import logging
from app import app, db
from models import Course, Competency, Role
from data_processor import create_sample_competencies, create_sample_roles, create_sample_courses

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with sample data if it's empty"""
    with app.app_context():
        # Check if tables exist but are empty
        competency_count = Competency.query.count()
        role_count = Role.query.count()
        course_count = Course.query.count()
        
        if competency_count == 0 and role_count == 0 and course_count == 0:
            logger.info("Database is empty, seeding with sample data")
            
            # Get sample data
            competencies_data = create_sample_competencies()
            roles_data = create_sample_roles(competencies_data)
            courses_data = create_sample_courses()
            
            # Insert competencies
            for comp_data in competencies_data:
                competency = Competency(
                    id=comp_data.get('id'),
                    code=comp_data.get('code'),
                    name=comp_data.get('name'),
                    description=comp_data.get('description'),
                    type=comp_data.get('type')
                )
                db.session.add(competency)
            
            # Commit competencies to get IDs
            db.session.commit()
            logger.info(f"Added {len(competencies_data)} competencies")
            
            # Insert roles
            for role_data in roles_data:
                competency_ids = ",".join(role_data.get('competency_ids', []))
                role = Role(
                    designation=role_data.get('designation'),
                    ministry=role_data.get('ministry'),
                    competency_ids=competency_ids
                )
                db.session.add(role)
            
            # Commit roles
            db.session.commit()
            logger.info(f"Added {len(roles_data)} roles")
            
            # Insert courses
            for course_data in courses_data:
                competency_ids = ",".join(course_data.get('competency_ids', []))
                course = Course(
                    title=course_data.get('title'),
                    description=course_data.get('description'),
                    provider=course_data.get('provider'),
                    domain=course_data.get('domain'),
                    competency_ids=competency_ids,
                    level=course_data.get('level'),
                    duration_hours=course_data.get('duration_hours'),
                    course_type=course_data.get('course_type')
                )
                db.session.add(course)
            
            # Commit courses
            db.session.commit()
            logger.info(f"Added {len(courses_data)} courses")
            
            logger.info("Database seeded successfully!")
        else:
            logger.info(f"Database already contains data: {competency_count} competencies, {role_count} roles, {course_count} courses")

if __name__ == "__main__":
    seed_database()