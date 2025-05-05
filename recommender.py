import logging
import numpy as np
import pandas as pd
from data_processor import load_all_data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Load data
courses, roles, competencies = load_all_data()

def get_competencies_for_role(designation, ministry):
    """
    Maps a role (designation + ministry) to relevant competencies
    
    Parameters:
    -----------
    designation : str
        The job designation of the official
    ministry : str
        The ministry/department of the official
        
    Returns:
    --------
    list
        List of competency objects with type, name, and description
    """
    logger.debug(f"Finding competencies for designation={designation}, ministry={ministry}")
    
    # Find matching role
    matching_roles = [role for role in roles if 
                      role.get('designation').lower() == designation.lower() and 
                      role.get('ministry').lower() == ministry.lower()]
    
    if not matching_roles:
        # Fallback: Try to find roles with similar designation if exact ministry match isn't found
        matching_roles = [role for role in roles if role.get('designation').lower() == designation.lower()]
        
    if not matching_roles:
        logger.warning(f"No matching role found for {designation} in {ministry}")
        # Return a default set of competencies
        return [comp for comp in competencies if comp.get('type') == 'Behavioral'][:3]
    
    # Get competency IDs associated with the role
    role = matching_roles[0]
    competency_ids = role.get('competency_ids', [])
    
    # Find the actual competency objects
    role_competencies = [comp for comp in competencies if comp.get('id') in competency_ids]
    
    # Group competencies by type
    behavioral = [c for c in role_competencies if c.get('type') == 'Behavioral']
    functional = [c for c in role_competencies if c.get('type') == 'Functional']
    domain = [c for c in role_competencies if c.get('type') == 'Domain']
    
    # Ensure we have at least some competencies from each type
    if not behavioral:
        behavioral = [c for c in competencies if c.get('type') == 'Behavioral'][:2]
    if not functional:
        functional = [c for c in competencies if c.get('type') == 'Functional'][:2]
    if not domain:
        domain = [c for c in competencies if c.get('type') == 'Domain'][:2]
    
    logger.debug(f"Found {len(behavioral)} behavioral, {len(functional)} functional, {len(domain)} domain competencies")
    
    return behavioral + functional + domain

def create_course_sequence(competencies, all_courses):
    """
    Creates a logical sequence of courses based on competencies
    
    Parameters:
    -----------
    competencies : list
        List of competency objects
    all_courses : list
        List of all available courses
        
    Returns:
    --------
    list
        Ordered list of courses forming a learning path
    """
    competency_ids = [comp.get('id') for comp in competencies]
    
    # Filter courses that match the competencies
    matching_courses = []
    for course in all_courses:
        course_competencies = course.get('competency_ids', [])
        if any(comp_id in course_competencies for comp_id in competency_ids):
            # Add a match score based on how many competencies it covers
            match_count = sum(1 for comp_id in competency_ids if comp_id in course_competencies)
            course = course.copy()
            course['match_score'] = match_count
            matching_courses.append(course)
    
    if not matching_courses:
        logger.warning("No courses found matching the competencies")
        return []
    
    # Sort courses by level (Beginner, Intermediate, Advanced)
    level_order = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
    
    # First sort by match score descending, then by level order
    matching_courses.sort(key=lambda x: (-x.get('match_score', 0), 
                                         level_order.get(x.get('level', "Intermediate"), 1)))
    
    # Group by competency type and level to create a balanced path
    behavioral_courses = [c for c in matching_courses 
                         if any(comp_id in c.get('competency_ids', []) 
                               for comp_id in [comp.get('id') for comp in competencies 
                                              if comp.get('type') == 'Behavioral'])]
    
    functional_courses = [c for c in matching_courses 
                         if any(comp_id in c.get('competency_ids', []) 
                               for comp_id in [comp.get('id') for comp in competencies 
                                              if comp.get('type') == 'Functional'])]
    
    domain_courses = [c for c in matching_courses 
                     if any(comp_id in c.get('competency_ids', []) 
                           for comp_id in [comp.get('id') for comp in competencies 
                                          if comp.get('type') == 'Domain'])]
    
    # Create a path with a mix of all three types, starting with basics
    path = []
    
    # Add beginner courses first
    for course_list in [behavioral_courses, functional_courses, domain_courses]:
        beginner_courses = [c for c in course_list if c.get('level') == 'Beginner']
        if beginner_courses:
            path.append(beginner_courses[0])
    
    # Then add intermediate courses
    for course_list in [behavioral_courses, functional_courses, domain_courses]:
        intermediate_courses = [c for c in course_list if c.get('level') == 'Intermediate']
        if intermediate_courses:
            path.append(intermediate_courses[0])
    
    # Finally add advanced courses
    for course_list in [behavioral_courses, functional_courses, domain_courses]:
        advanced_courses = [c for c in course_list if c.get('level') == 'Advanced']
        if advanced_courses:
            path.append(advanced_courses[0])
    
    # Remove duplicates while preserving order
    unique_path = []
    seen_ids = set()
    for course in path:
        if course.get('id') not in seen_ids:
            unique_path.append(course)
            seen_ids.add(course.get('id'))
    
    # Fill in with other relevant courses if we don't have enough
    for course in matching_courses:
        if course.get('id') not in seen_ids and len(unique_path) < 8:
            unique_path.append(course)
            seen_ids.add(course.get('id'))
    
    # Add order property to each course
    for i, course in enumerate(unique_path):
        course['order'] = i + 1
    
    return unique_path

def generate_recommendations(designation, ministry, role_competencies):
    """
    Generate personalized course recommendations based on role and competencies
    
    Parameters:
    -----------
    designation : str
        The job designation of the official
    ministry : str
        The ministry/department of the official
    role_competencies : list
        List of competencies needed for the role
        
    Returns:
    --------
    list
        Ordered list of course recommendations
    """
    logger.debug(f"Generating recommendations for {designation} in {ministry}")
    
    # Create a learning path based on competencies
    learning_path = create_course_sequence(role_competencies, courses)
    
    # If we can't find enough courses based on exact competency matches,
    # use content-based similarity to add more recommendations
    if len(learning_path) < 5 and courses:
        logger.debug("Not enough courses found, adding recommendations based on content similarity")
        
        # Prepare course content for TF-IDF
        course_texts = []
        course_ids = []
        for course in courses:
            # Combine title, description, and domain for better matching
            text = f"{course.get('title', '')} {course.get('description', '')} {course.get('domain', '')}"
            course_texts.append(text)
            course_ids.append(course.get('id'))
        
        # Use TF-IDF to vectorize course content
        tfidf = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = tfidf.fit_transform(course_texts)
            
            # If we have at least one course in learning_path, use it as a reference
            if learning_path:
                # Get the IDs of courses already in the learning path
                existing_ids = [course.get('id') for course in learning_path]
                
                # Find the indices of these courses in our course_ids list
                reference_indices = [i for i, cid in enumerate(course_ids) if cid in existing_ids]
                
                if reference_indices:
                    # Calculate similarity between all courses and our reference courses
                    similarity_scores = np.zeros(len(course_ids))
                    for idx in reference_indices:
                        course_similarity = cosine_similarity(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()
                        similarity_scores += course_similarity
                    
                    # Get top similar courses that aren't already in the learning path
                    similar_course_indices = similarity_scores.argsort()[::-1]
                    
                    # Add top similar courses to learning path
                    for idx in similar_course_indices:
                        course_id = course_ids[idx]
                        if course_id not in existing_ids and len(learning_path) < 8:
                            # Find the course by id
                            similar_course = next((c for c in courses if c.get('id') == course_id), None)
                            if similar_course:
                                similar_course = similar_course.copy()
                                similar_course['order'] = len(learning_path) + 1
                                learning_path.append(similar_course)
                                existing_ids.append(course_id)
        except Exception as e:
            logger.exception("Error in content-based recommendation")
    
    # Ensure each course has a duration and level
    for course in learning_path:
        if 'duration_hours' not in course:
            course['duration_hours'] = 2.0  # Default duration
        if 'level' not in course:
            course['level'] = 'Intermediate'  # Default level
    
    return learning_path
