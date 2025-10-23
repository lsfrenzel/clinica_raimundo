# Clínica Dr. Raimundo Nunes - Sistema de Gestão Médica

## Overview
This project is a comprehensive management system for a medical clinic specializing in gynecology and obstetrics. Its core purpose is to streamline operations through an intelligent chatbot for appointment scheduling, a robust administrative panel, and efficient patient management. The system aims to provide a modern, user-friendly experience with advanced AI capabilities for patient interaction and backend tools for clinic staff, positioning it for market potential in specialized medical services.

## User Preferences
- I prefer simple language and clear, concise explanations.
- I appreciate iterative development with regular updates.
- Please ask for confirmation before implementing significant changes or making architectural decisions.
- I prefer detailed explanations for complex features or problem resolutions.
- Ensure all datetime handling is robust, particularly concerning timezones, converting to UTC for storage and local time for display.
- Prioritize fixing issues by first understanding the root cause and then implementing a targeted solution.
- I expect robust logging for debugging and observability.
- Do not make changes to the existing structure of the database without prior discussion.

## System Architecture

### UI/UX Decisions
The system features a modern and revolutionary design with a responsive layout, custom color palette (teal, emerald, gold), and premium typography (Playfair Display, Lato, Montserrat). It utilizes AOS (Animate On Scroll) for smooth transitions and interactive elements, incorporating gradients, floating buttons, and glassmorphism effects. Key page designs include animated hero sections, modern authentication forms, redesigned appointment booking flows, and dedicated doctor pages with professional visuals.

### Technical Implementations
A hybrid chatbot system integrates Google Gemini AI for intelligent conversation, with a robust rule-based system for fallback and database interaction. It automates the entire appointment workflow, from selection to confirmation. A comprehensive admin panel manages appointments, doctors, schedules, and reporting. Secure patient management includes encrypted password registration. All datetimes are stored in UTC and converted to local time (Brasília UTC-3) for user display.

### Feature Specifications
The chatbot supports multi-context conversations, automated scheduling, and access to database entities. The system provides extensive appointment management (view, edit, cancel), doctor and schedule configuration, and basic consultation reporting. Advanced appointment searching includes filtering by date, time of day, and multi-day views with visual grids.

### System Design Choices
The backend is built with Flask (Python) using SQLAlchemy for ORM. The frontend uses Jinja2 for templating, Tailwind CSS (via CDN) for styling, AOS for animations, and custom JavaScript/CSS. PostgreSQL is the primary database, and Flask-Login handles authentication. The deployment strategy is configured for Replit (development) and Railway (production), including automated database migration and seeding scripts.

## External Dependencies
- **PostgreSQL**: Primary relational database.
- **Google Gemini API**: For intelligent chatbot capabilities.
- **Tailwind CSS (CDN)**: Frontend utility-first CSS framework.
- **AOS (Animate On Scroll) Library**: For UI animations.
- **Gunicorn**: WSGI HTTP Server for production deployments.
- **Flask-Login**: Extension for user session management.
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapper.
- **bcrypt**: For password hashing.