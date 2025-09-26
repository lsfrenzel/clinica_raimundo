# Medical Clinic Management System

## Overview
This is a comprehensive medical clinic management system built with Flask, designed for Dr. Raimundo Nunes Clinic (Ginecologia e Obstetrícia). The system provides appointment booking, patient management, doctor scheduling, and administrative features.

## Current State
- ✅ **Application is running** on port 5000
- ✅ **Database configured** with PostgreSQL (Neon)
- ✅ **Dependencies installed** via uv package manager
- ✅ **Deployment configured** for Replit autoscale
- ✅ **Workflow configured** for development server

## Recent Changes (September 26, 2025)
- ✅ **Import Setup Complete**: Successfully imported and configured GitHub project for Replit
- ✅ **Database Setup**: Using existing PostgreSQL database with all environment variables
- ✅ **Workflow Configuration**: Set up Flask development server on port 5000 with webview output
- ✅ **Database Seeding**: Populated database with sample data including:
  - 9 medical specializations
  - 5 doctors with profiles and schedules
  - 5 sample patients
  - 434 available time slots
  - 10 sample appointments
  - 1 administrator account
- ✅ **Deployment Configuration**: Set up production deployment with Gunicorn
- ✅ **Project Verification**: All components working correctly in Replit environment

## Project Architecture

### Technology Stack
- **Backend**: Flask 3.1.2 with SQLAlchemy
- **Database**: PostgreSQL (Neon-hosted)
- **Frontend**: Tailwind CSS with responsive design
- **Authentication**: Flask-Login with bcrypt password hashing
- **Email**: Flask-Mail for notifications
- **Deployment**: Gunicorn on Replit autoscale

### File Structure
```
/
├── main.py                 # Application entry point
├── models.py              # Database models
├── extensions.py          # Flask extensions initialization
├── pyproject.toml         # Python dependencies
├── app/
│   ├── templates/         # Jinja2 templates
│   │   ├── base.html     # Base template with clinic styling
│   │   ├── index.html    # Homepage
│   │   ├── auth/         # Authentication templates
│   │   └── appointments/ # Appointment booking templates
│   └── blueprints/       # Flask blueprints
│       ├── main.py       # Homepage routes
│       ├── auth.py       # Authentication
│       ├── appointments.py # Appointment booking
│       ├── admin.py      # Admin panel
│       └── api.py        # API endpoints
└── scripts/
    └── seed_data.py      # Database seeding script
```

### Database Models
- **User**: Base user model with roles (admin, staff, medico, paciente)
- **Medico**: Doctor profiles with specializations
- **Especialidade**: Medical specializations
- **Agendamento**: Appointment bookings (supports both registered users and guests)
- **Agenda**: Doctor availability scheduling
- **Notificacao**: Email notifications system
- **Pagamento**: Payment tracking
- **LogAudit**: Security audit logs

### Key Features
1. **Patient Registration**: Both registered users and guest appointments
2. **Doctor Management**: Professional profiles with specializations
3. **Appointment Booking**: Real-time availability checking
4. **Admin Panel**: Administrative controls and reporting
5. **Email Notifications**: Automated appointment confirmations
6. **Responsive Design**: Mobile-friendly interface with clinic branding

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session security key
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`: Database credentials

## Development Notes
- Uses uv for Python package management
- Tailwind CSS via CDN (consider local build for production)
- Debug mode enabled in development
- Database tables auto-created on startup
- Flask-Migrate available for schema changes

## User Preferences
- Clean, medical professional design matching clinic branding
- Portuguese language interface
- Blue color scheme (#2563eb primary)
- Responsive mobile-first design