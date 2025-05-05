# Karmayogi Bharat - AI-Powered Learning Path Recommender

![Karmayogi Bharat Logo](static/img/recommendation-system.svg)

A next-generation learning recommendation platform for government officials, featuring personalized learning pathways.

## Description

The Karmayogi Bharat Learning Path Recommender is an AI-powered platform that creates personalized learning journeys for government officials based on their roles. The system maps a government official's designation and ministry to required competencies (behavioral, functional, and domain) and recommends a tailored sequence of courses to help them develop these competencies.

### Key Features

- **Role-based Competency Mapping**: Automatically identifies required competencies based on designation and ministry
- **Personalized Learning Paths**: Recommends courses based on identified competencies
- **User Authentication**: Complete user registration and login system
- **Course Enrollment**: Users can enroll in recommended courses
- **Progress Tracking**: Track completion status and progress for enrolled courses
- **Interactive UI**: Modern, responsive interface with animations and visual elements
- **Database Integration**: Stores all data in PostgreSQL database for persistence and scalability

## Technology Stack

- **Backend**: Python, Flask
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **UI Enhancements**: Particle.js, AOS animations
- **Form Handling**: Flask-WTF with form validation

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/karmayogi-bharat-recommender.git
cd karmayogi-bharat-recommender
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install Flask Flask-Login Flask-SQLAlchemy Flask-WTF email-validator gunicorn psycopg2-binary SQLAlchemy Werkzeug WTForms python-dotenv
```

The key dependencies include:
- Flask 2.3.3 or higher
- Flask-Login 0.6.2 or higher
- Flask-SQLAlchemy 3.1.1 or higher
- Flask-WTF 1.2.1 or higher
- psycopg2-binary 2.9.9 or higher (PostgreSQL adapter)
- gunicorn 21.2.0 or higher (for production deployment)

4. Configure environment variables:
Create a `.env` file with the following variables:
```
DATABASE_URL=postgresql://username:password@localhost:5432/karmayogi
SECRET_KEY=your_secret_key
```

5. Initialize the database:
```bash
# The application will create tables and seed data automatically on first run
python main.py
```

## Usage

1. Start the application:
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

2. Open your browser and navigate to `http://localhost:5000`

3. Register a new account with your official role details

4. Get personalized learning recommendations based on your role

5. Enroll in courses and track your progress

## User Interface

The application features a modern, responsive interface designed for an optimal user experience:

### Home Page
- Welcome section with animated particle background
- Information about the Karmayogi Bharat initiative
- Quick navigation to recommendations and login/registration

### User Dashboard
- Overview of enrolled courses
- Progress tracking with visual indicators
- Recommended courses based on your role

### Recommendation Page
- Personalized learning path visualization
- Course cards with detailed information
- Filter and sort options for course discovery

### Course Detail Page
- Comprehensive course information
- Enrollment options
- Progress tracking for enrolled courses

## AI Recommendation System

The recommendation engine consists of three main components:

### 1. Role-Competency Mapping
The system associates each combination of designation and ministry with a set of required competencies across three categories:
- **Behavioral Competencies**: Leadership, communication, collaboration, etc.
- **Functional Competencies**: Policy-making, program management, data analysis, etc.
- **Domain Competencies**: Subject-specific knowledge areas relevant to the ministry

### 2. Course-Competency Analysis
Courses are tagged with competencies they help develop. The recommendation algorithm:
- Identifies courses that address the required competencies
- Analyzes metadata (level, duration, course type)
- Considers prerequisite relationships and logical learning sequences

### 3. Learning Path Generation
The final step creates a personalized learning path by:
- Prioritizing courses based on competency importance
- Sequencing courses in a logical learning order
- Balancing course types (video, interactive, blended)
- Considering progression from beginner to advanced levels

## Database Schema

The application uses the following main data models:

- **User**: Stores user authentication and profile information
- **Role**: Maps designations and ministries to required competencies
- **Competency**: Defines behavioral, functional, and domain competencies
- **Course**: Contains course information and metadata
- **UserCourse**: Tracks user enrollments and progress

## Project Structure

```
karmayogi-bharat-recommender/
├── app.py            # Application initialization
├── data_processor.py # Data handling functions
├── db_seeder.py      # Database seeding script
├── main.py           # Application entry point
├── models.py         # Database models
├── recommender.py    # Recommendation engine
├── static/           # Static assets (CSS, JS, images)
├── templates/        # HTML templates
├── data/             # JSON fallback data (if needed)
├── instance/         # Local database files
└── README.md
```

## Development and Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m "Add feature"`
4. Push to your branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Karmayogi Bharat platform for inspiration
- Indian government's initiatives for civil servant capacity building