# Moving Service Task Manager (Django)

A Django-based web application for managing moving service requests.  
Customers can book, view, edit, and cancel move schedules, while staff can manage requests through the Django admin panel.

This project focuses on clean Django architecture, authentication, form-based CRUD workflows, and PostgreSQL integration.

---

## Features

- User authentication (sign up, log in, log out)
- Custom Django User model with roles:
  - Customer
  - Driver
  - Staff
- Customers can:
  - Book a new move
  - View, edit, or cancel their own move requests
- Server-side form validation for scheduling
- PostgreSQL database integration
- Django admin interface for managing users and move requests

---

## Tech Stack

- Python 3
- Django
- PostgreSQL
- HTML & Django Templates
- Bootstrap (basic styling)

---

## Project Structure
```
moving_service/
├── manage.py
├── moving_service/
│ ├── settings.py
│ └── urls.py
├── accounts/ # authentication & custom user model
├── moves/ # move request CRUD logic
├── templates/ # shared templates (base, home, auth)
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.9+
- PostgreSQL
- `pip` and `venv`

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/bananamtieu/moving-service-django.git
cd moving-service-django
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a .env file in the project root (same level as manage.py):
```bash
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=moving_service_db
DB_USER=moving_service_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Set up PostgreSQL
```sql
Create the database and user:
CREATE DATABASE moving_service_db;
CREATE USER moving_service_user WITH PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE moving_service_db TO moving_service_user;
```

### 6. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser (admin access)
```bash
python manage.py createsuperuser
```

### 8. Run the development server
```bash
python manage.py runserver
```

Visit the app at:
```cpp
http://127.0.0.1:8000/
```

Admin panel:
```arduino
http://127.0.0.1:8000/admin/
```

## Usage

- Sign up as a customer to book move requests
- View, edit, or cancel scheduled moves
- Log in as an admin to manage users and move requests via Django Admin

## Future Improvements

- Driver assignment workflow
- Role-based dashboards (customer / driver / staff)
- Pricing estimation logic
- Docker-based deployment
- REST API layer

## Learning Goals

This project was built to practice:
- Django authentication and custom user models
- Form validation and CRUD workflows
- PostgreSQL integration
- Database migrations and schema evolution
- Clean project structure and best practices