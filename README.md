# EduTrack - Course Management System

EduTrack is a lightweight course management system designed for schools. It allows teachers to create courses and assignments, while students can enroll in courses and submit assignments.

## Features

- **User Roles**: Two user types - Teacher and Student
- **Courses**: Create, update, delete, and view courses
- **Assignments**: Create assignments for courses and submit responses
- **Permissions**: Custom permission system to ensure proper access control
- **RESTful API**: Built with Django Rest Framework

## Tech Stack

- Python 3.10+
- Django 4.2
- Django Rest Framework
- PostgreSQL
- Docker & Docker Compose
- GitHub Actions for CI

## Project Structure

The project follows a modular architecture with separate apps for different concerns:

- **users**: Handles user authentication, profiles, and roles
- **courses**: Manages course creation, enrollment, and related operations
- **assignments**: Handles assignment creation, submission, and review

## Setup Instructions

### Using Docker (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/edutrack.git
   cd edutrack
   ```

2. Create a `.env` file with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgres://postgres:postgres@db:5432/edutrack
   ```

3. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

4. Run migrations:
   ```
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

6. Access the application:
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - API Documentation: http://localhost:8000/api/docs/

### Without Docker

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/edutrack.git
   cd edutrack
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your environment variables.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

## API Documentation

The API is self-documented using drf-spectacular, which provides Swagger and ReDoc interfaces:

- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Testing

Run tests with coverage:

```
docker-compose exec web python manage.py test
```

Or without Docker:

```
python manage.py test
```

For coverage report:

```
coverage run --source='.' manage.py test
coverage report
```

## Design Decisions

### User Model

I extended Django's built-in User model using a profile model (UserProfile) that contains additional fields like user type (Teacher/Student). This approach maintains compatibility with Django's authentication system while adding the necessary role-based functionality.

### Permissions

Custom permissions are implemented using DRF permission classes that check:
- Whether the user is authenticated
- Whether the user has the correct role for the requested action
- Whether the user has the necessary relationship to the resource (e.g., course owner, enrolled student)

### API Design

- Used ViewSets for standard CRUD operations
- Implemented custom actions for specific use cases (enrollment, submission review)
- Added filtering and pagination for list endpoints
- Used nested routes where appropriate (assignments within courses)

### Performance Considerations

- Added caching for course listing
- Implemented database optimization with select_related and prefetch_related
- Added throttling for API endpoints

## Assumptions

- Users can have only one role (Teacher or Student)
- A course can have only one teacher (the creator)
- Students can enroll in multiple courses
- Each assignment belongs to exactly one course
- A student can submit only once per assignment