import os
import json
import logging
from models import Course, Competency, Role

logger = logging.getLogger(__name__)

# For backward compatibility and sample data generation
COURSES_FILE = 'data/courses.json'
ROLES_FILE = 'data/roles.json'
COMPETENCIES_FILE = 'data/competencies.json'

def get_all_data_from_db():
    """Load all data from the database"""
    try:
        from app import db, app
        
        # Use application context to query the database
        with app.app_context():
            courses = [course.to_dict() for course in Course.query.all()]
            roles = [role.to_dict() for role in Role.query.all()]
            competencies = [comp.to_dict() for comp in Competency.query.all()]
        
        logger.debug(f"Loaded data from database: {len(courses)} courses, {len(roles)} roles, {len(competencies)} competencies")
        
        return courses, roles, competencies
    except Exception as e:
        logger.error(f"Error loading data from database: {str(e)}")
        return [], [], []

def load_json_data(file_path):
    """Load data from a JSON file (kept for backward compatibility)"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"File not found: {file_path}")
            return []
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return []

def save_json_data(file_path, data):
    """Save data to a JSON file (kept for backward compatibility)"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving to {file_path}: {str(e)}")
        return False

def load_all_data():
    """Load all data from the database, or use JSON files as fallback"""
    # First try to get data from the database
    courses, roles, competencies = get_all_data_from_db()
    
    # If the database is empty, try JSON files (for backward compatibility)
    if not courses:
        logger.warning("No courses found in database, checking JSON files")
        courses = load_json_data(COURSES_FILE)
    
    if not competencies:
        logger.warning("No competencies found in database, checking JSON files")
        competencies = load_json_data(COMPETENCIES_FILE)
    
    if not roles:
        logger.warning("No roles found in database, checking JSON files")
        roles = load_json_data(ROLES_FILE)
    
    return courses, roles, competencies

def get_designations():
    """Get list of unique designations from roles data"""
    try:
        from app import db, app
        
        # Get unique designations from the database
        with app.app_context():
            designations = [result[0] for result in db.session.query(Role.designation).distinct().all()]
        
        if designations:
            return sorted(designations)
        else:
            return ["Director", "Deputy Secretary", "Joint Secretary", "Under Secretary", "Section Officer"]
    except Exception as e:
        logger.error(f"Error getting designations from database: {str(e)}")
        return ["Director", "Deputy Secretary", "Joint Secretary", "Under Secretary", "Section Officer"]

def get_ministries():
    """Get list of unique ministries from roles data"""
    try:
        from app import db, app
        
        # Get unique ministries from the database
        with app.app_context():
            ministries = [result[0] for result in db.session.query(Role.ministry).distinct().all()]
        
        if ministries:
            return sorted(ministries)
        else:
            return ["Ministry of Electronics and IT", "Ministry of Finance", "Ministry of Home Affairs", 
                    "Ministry of Defence", "Ministry of Education"]
    except Exception as e:
        logger.error(f"Error getting ministries from database: {str(e)}")
        return ["Ministry of Electronics and IT", "Ministry of Finance", "Ministry of Home Affairs", 
                "Ministry of Defence", "Ministry of Education"]

# Sample data creation functions
def create_sample_competencies():
    """Create sample competency data"""
    return [
        # Behavioral Competencies
        {
            "id": "B001",
            "code": "PPLMAN",
            "name": "People Management",
            "description": "Ability to manage teams and delegate tasks effectively",
            "type": "Behavioral"
        },
        {
            "id": "B002",
            "code": "COMMUN",
            "name": "Communication Skills",
            "description": "Ability to communicate clearly and effectively",
            "type": "Behavioral"
        },
        {
            "id": "B003",
            "code": "LEADER",
            "name": "Leadership",
            "description": "Ability to lead and motivate teams",
            "type": "Behavioral"
        },
        {
            "id": "B004",
            "code": "INTGRT",
            "name": "Integrity and Ethics",
            "description": "Adherence to ethical principles and standards",
            "type": "Behavioral"
        },
        {
            "id": "B005",
            "code": "COLLAB",
            "name": "Collaboration",
            "description": "Ability to work effectively with others",
            "type": "Behavioral"
        },
        
        # Functional Competencies
        {
            "id": "F001",
            "code": "POLICY",
            "name": "Policy Making",
            "description": "Ability to formulate and implement policies",
            "type": "Functional"
        },
        {
            "id": "F002",
            "code": "PRGMGT",
            "name": "Program Management",
            "description": "Ability to plan and execute programs effectively",
            "type": "Functional"
        },
        {
            "id": "F003",
            "code": "BUDGCT",
            "name": "Budgeting and Control",
            "description": "Skills in financial planning and management",
            "type": "Functional"
        },
        {
            "id": "F004",
            "code": "DATANA",
            "name": "Data Analysis",
            "description": "Ability to analyze and interpret data",
            "type": "Functional"
        },
        {
            "id": "F005",
            "code": "DGTSKL",
            "name": "Digital Skills",
            "description": "Proficiency in using digital tools and platforms",
            "type": "Functional"
        },
        
        # Domain Competencies
        {
            "id": "D001",
            "code": "ITGOV",
            "name": "IT Governance",
            "description": "Knowledge of IT governance frameworks and practices",
            "type": "Domain"
        },
        {
            "id": "D002",
            "code": "PUBLW",
            "name": "Public Law",
            "description": "Knowledge of constitutional and administrative law",
            "type": "Domain"
        },
        {
            "id": "D003",
            "code": "PBLHLTH",
            "name": "Public Health",
            "description": "Understanding of public health issues and policies",
            "type": "Domain"
        },
        {
            "id": "D004",
            "code": "INFRSEC",
            "name": "Information Security",
            "description": "Knowledge of cybersecurity principles and practices",
            "type": "Domain"
        },
        {
            "id": "D005",
            "code": "EDUCAT",
            "name": "Education Policy",
            "description": "Understanding of education sector and policies",
            "type": "Domain"
        }
    ]

def create_sample_roles(competencies):
    """Create sample role data"""
    return [
        {
            "id": 1,
            "designation": "Director",
            "ministry": "Ministry of Electronics and IT",
            "competency_ids": ["B001", "B003", "F001", "F002", "D001", "D004"]
        },
        {
            "id": 2,
            "designation": "Deputy Secretary",
            "ministry": "Ministry of Electronics and IT",
            "competency_ids": ["B002", "B005", "F003", "F005", "D001", "D004"]
        },
        {
            "id": 3,
            "designation": "Joint Secretary",
            "ministry": "Ministry of Finance",
            "competency_ids": ["B001", "B003", "F001", "F003", "D002"]
        },
        {
            "id": 4,
            "designation": "Under Secretary",
            "ministry": "Ministry of Finance",
            "competency_ids": ["B002", "B004", "F003", "F004", "D002"]
        },
        {
            "id": 5,
            "designation": "Section Officer",
            "ministry": "Ministry of Home Affairs",
            "competency_ids": ["B002", "B005", "F004", "F005", "D002"]
        },
        {
            "id": 6,
            "designation": "Director",
            "ministry": "Ministry of Home Affairs",
            "competency_ids": ["B001", "B003", "F001", "F002", "D002"]
        },
        {
            "id": 7,
            "designation": "Joint Secretary",
            "ministry": "Ministry of Defence",
            "competency_ids": ["B001", "B003", "B004", "F001", "F002", "D002"]
        },
        {
            "id": 8,
            "designation": "Director",
            "ministry": "Ministry of Education",
            "competency_ids": ["B001", "B003", "F001", "F002", "D005"]
        },
        {
            "id": 9,
            "designation": "Deputy Secretary",
            "ministry": "Ministry of Education",
            "competency_ids": ["B002", "B005", "F002", "F005", "D005"]
        },
        {
            "id": 10,
            "designation": "Section Officer",
            "ministry": "Ministry of Finance",
            "competency_ids": ["B004", "B005", "F003", "F004", "D002"]
        }
    ]

def create_sample_courses():
    """Create sample course data"""
    return [
        {
            "id": 1,
            "title": "Effective Leadership in Government",
            "description": "Learn key leadership skills for government officials",
            "provider": "iGOT Karmayogi",
            "domain": "Leadership",
            "competency_ids": ["B001", "B003"],
            "level": "Intermediate",
            "duration_hours": 8.0,
            "course_type": "Video"
        },
        {
            "id": 2,
            "title": "Communication Skills for Public Officials",
            "description": "Enhance your communication abilities in a government setting",
            "provider": "iGOT Karmayogi",
            "domain": "Communication",
            "competency_ids": ["B002"],
            "level": "Beginner",
            "duration_hours": 4.0,
            "course_type": "Interactive"
        },
        {
            "id": 3,
            "title": "Policy Formulation and Implementation",
            "description": "Comprehensive guide to creating and implementing effective policies",
            "provider": "LBSNAA",
            "domain": "Policy",
            "competency_ids": ["F001"],
            "level": "Advanced",
            "duration_hours": 12.0,
            "course_type": "Blended"
        },
        {
            "id": 4,
            "title": "Government Program Management",
            "description": "Learn to manage large-scale government programs effectively",
            "provider": "iGOT Karmayogi",
            "domain": "Management",
            "competency_ids": ["F002"],
            "level": "Intermediate",
            "duration_hours": 10.0,
            "course_type": "Video"
        },
        {
            "id": 5,
            "title": "Budget Planning and Financial Management",
            "description": "Master the art of government budgeting and financial control",
            "provider": "Ministry of Finance",
            "domain": "Finance",
            "competency_ids": ["F003"],
            "level": "Intermediate",
            "duration_hours": 8.0,
            "course_type": "Interactive"
        },
        {
            "id": 6,
            "title": "Data Analytics for Decision Making",
            "description": "Use data to make better policy decisions",
            "provider": "iGOT Karmayogi",
            "domain": "Data Science",
            "competency_ids": ["F004"],
            "level": "Beginner",
            "duration_hours": 6.0,
            "course_type": "Interactive"
        },
        {
            "id": 7,
            "title": "Digital Skills for Government Officials",
            "description": "Essential digital tools and platforms for modern governance",
            "provider": "NIELIT",
            "domain": "Digital",
            "competency_ids": ["F005"],
            "level": "Beginner",
            "duration_hours": 4.0,
            "course_type": "Video"
        },
        {
            "id": 8,
            "title": "IT Governance and Management",
            "description": "Framework for managing IT resources in government",
            "provider": "Ministry of Electronics and IT",
            "domain": "IT",
            "competency_ids": ["D001"],
            "level": "Advanced",
            "duration_hours": 10.0,
            "course_type": "Blended"
        },
        {
            "id": 9,
            "title": "Administrative Law for Practitioners",
            "description": "Practical guide to administrative law for government officials",
            "provider": "LBSNAA",
            "domain": "Law",
            "competency_ids": ["D002"],
            "level": "Intermediate",
            "duration_hours": 8.0,
            "course_type": "Video"
        },
        {
            "id": 10,
            "title": "Cybersecurity Fundamentals",
            "description": "Essential cybersecurity principles for government systems",
            "provider": "Ministry of Electronics and IT",
            "domain": "Security",
            "competency_ids": ["D004"],
            "level": "Beginner",
            "duration_hours": 6.0,
            "course_type": "Interactive"
        },
        {
            "id": 11,
            "title": "Team Collaboration and Management",
            "description": "Techniques for fostering team collaboration in government offices",
            "provider": "iGOT Karmayogi",
            "domain": "Management",
            "competency_ids": ["B001", "B005"],
            "level": "Intermediate",
            "duration_hours": 5.0,
            "course_type": "Interactive"
        },
        {
            "id": 12,
            "title": "Ethics in Public Service",
            "description": "Navigating ethical dilemmas in government roles",
            "provider": "LBSNAA",
            "domain": "Ethics",
            "competency_ids": ["B004"],
            "level": "Beginner",
            "duration_hours": 4.0,
            "course_type": "Video"
        },
        {
            "id": 13,
            "title": "Advanced Cybersecurity for Government",
            "description": "Protecting critical government infrastructure from cyber threats",
            "provider": "CERT-In",
            "domain": "Security",
            "competency_ids": ["D004"],
            "level": "Advanced",
            "duration_hours": 12.0,
            "course_type": "Blended"
        },
        {
            "id": 14,
            "title": "Education Policy Implementation",
            "description": "Strategies for implementing education policies effectively",
            "provider": "Ministry of Education",
            "domain": "Education",
            "competency_ids": ["D005", "F001"],
            "level": "Intermediate",
            "duration_hours": 8.0,
            "course_type": "Video"
        },
        {
            "id": 15,
            "title": "Digital Transformation in Government",
            "description": "Leading digital initiatives in government organizations",
            "provider": "iGOT Karmayogi",
            "domain": "Digital",
            "competency_ids": ["F005", "D001"],
            "level": "Advanced",
            "duration_hours": 10.0,
            "course_type": "Blended"
        },
        {
            "id": 16,
            "title": "Public Speaking for Government Officials",
            "description": "Master the art of public speaking and presentation",
            "provider": "iGOT Karmayogi",
            "domain": "Communication",
            "competency_ids": ["B002"],
            "level": "Intermediate",
            "duration_hours": 6.0,
            "course_type": "Video"
        },
        {
            "id": 17,
            "title": "Leadership in Crisis Management",
            "description": "Leading teams effectively during crisis situations",
            "provider": "LBSNAA",
            "domain": "Leadership",
            "competency_ids": ["B001", "B003"],
            "level": "Advanced",
            "duration_hours": 8.0,
            "course_type": "Interactive"
        },
        {
            "id": 18,
            "title": "Government Data Management",
            "description": "Best practices for managing government data",
            "provider": "Ministry of Electronics and IT",
            "domain": "Data",
            "competency_ids": ["F004", "D001"],
            "level": "Intermediate",
            "duration_hours": 7.0,
            "course_type": "Video"
        },
        {
            "id": 19,
            "title": "Strategic Planning for Public Sector",
            "description": "Developing and implementing strategic plans in government",
            "provider": "iGOT Karmayogi",
            "domain": "Planning",
            "competency_ids": ["F001", "F002"],
            "level": "Advanced",
            "duration_hours": 10.0,
            "course_type": "Blended"
        },
        {
            "id": 20,
            "title": "Building Collaborative Teams",
            "description": "Creating and nurturing effective teams in government",
            "provider": "iGOT Karmayogi",
            "domain": "Management",
            "competency_ids": ["B001", "B005"],
            "level": "Beginner",
            "duration_hours": 5.0,
            "course_type": "Interactive"
        }
    ]
