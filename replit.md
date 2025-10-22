# Clínica Dr. Raimundo Nunes - Sistema de Gestão Médica

## Overview
This project is a comprehensive management system for a medical clinic specializing in gynecology and obstetrics. Its core purpose is to streamline operations through an intelligent chatbot for appointment scheduling, a robust administrative panel, and efficient patient management. The system aims to provide a modern, user-friendly experience with advanced AI capabilities for patient interaction and backend tools for clinic staff. The project is fully functional, with a populated database, integrated AI, and a revolutionary design, positioning it for market potential in specialized medical services.

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
The system features a modern and revolutionary design characterized by:
- **Responsive Layout**: Designed for optimal viewing across desktop and mobile devices.
- **Color Palette**: Custom teal (#4B7D7B), emerald (#50C6A5), and gold (#C5A88D).
- **Typography**: Premium fonts like Playfair Display, Lato, and Montserrat.
- **Animations**: Utilizes AOS (Animate On Scroll) for smooth transitions and interactive elements like 3D hover effects on cards.
- **Design Patterns**: Incorporates gradients, floating buttons, and glassmorphism effects for a sophisticated look.
- **Key Page Designs**:
    - **Homepage**: Hero section with animated gradients, interactive cards, illustrated "How to Schedule" section, and animated grids for specialties/doctors.
    - **Authentication**: Two-column layout with branding, modern forms with inline icons, and soft gradients.
    - **Appointment Booking**: Modern progress bar, redesigned specialty cards, and benefit badges.
    - **Doctors Page**: Dedicated section for lead doctor, professional photos for all staff, and animated statistical cards.

### Technical Implementations
- **Hybrid Chatbot System**: Integrates Google Gemini API for intelligent conversational AI as the primary engine, with a robust rule-based system serving as a fallback for guaranteed functionality and database interaction.
- **Automated Appointment Workflow**: Handles the entire booking process from specialty selection to confirmation and database entry.
- **Comprehensive Admin Panel**: Features management for appointments, doctors, medical schedules, and reporting.
- **Secure Patient Management**: Includes complete patient registration with encrypted passwords (bcrypt).
- **Timezone Management**: All datetimes are stored in UTC in the database and converted to local time (Brasília UTC-3) for user display to prevent conflicts.

### Feature Specifications
- **Chatbot**: Supports multi-context conversations, automated scheduling, and access to database entities (specialties, doctors, schedules).
- **Appointment Management**: View, edit, and cancel appointments via the admin panel.
- **Doctor & Schedule Management**: Configure doctor availability and specialties.
- **Reporting**: Basic reporting on consultations.

### System Design Choices
- **Backend Framework**: Flask (Python) with SQLAlchemy for ORM.
- **Frontend Technologies**: Jinja2 for templating, Tailwind CSS (via CDN) for utility-first styling, AOS for animations, and custom JavaScript/CSS for interactivity.
- **Database**: PostgreSQL.
- **Authentication**: Flask-Login for user session management.
- **Deployment Strategy**: Configured for Replit (development) with Gunicorn and Railway (production) for automated deployment and database management. Includes scripts for automatic database migration and seeding.

## External Dependencies
- **PostgreSQL**: Primary relational database.
- **Google Gemini API**: For intelligent chatbot capabilities.
- **Tailwind CSS (CDN)**: Frontend utility-first CSS framework.
- **AOS (Animate On Scroll) Library**: For UI animations.
- **Gunicorn**: WSGI HTTP Server for production deployments.
- **Flask-Login**: Extension for user session management.
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapper.
- **bcrypt**: For password hashing.

## Recent Improvements

### ✅ Sistema de Agendamento de Consultas - Pesquisa Avançada de Horários (22/10/2025)

**Objetivo**: Melhorar significativamente a experiência do paciente ao pesquisar e agendar consultas, permitindo busca inteligente de horários disponíveis.

**Funcionalidades Implementadas:**

1. **Filtros Avançados na Página de Médicos** (`/medicos/<especialidade_id>`):
   - Filtro por data inicial
   - Filtro por período do dia (Manhã 6h-12h, Tarde 12h-18h, Noite 18h-24h)
   - Exibição de até 10 horários disponíveis por médico (anteriormente: 3)
   - Grid visual com 8 horários diretamente clicáveis
   - Botão "Agendar Próximo Horário" para agendamento rápido
   - Indicador de quantidade de horários encontrados
   - Mensagens claras quando não há horários nos filtros selecionados

2. **Visualização Múltipla de Horários** (`/horarios/<medico_id>`):
   - Filtro por data inicial, período do dia e visualização (1, 3 ou 7 dias)
   - **Vista de 1 dia**: Grid compacto mostrando todos os horários do dia
   - **Vista de múltiplos dias**: Cards separados por dia com cabeçalho destacado
   - Indicação visual do período (Manhã/Tarde/Noite) em cada horário
   - Animações e transições suaves para feedback visual
   - Navegação melhorada com instruções claras

3. **Melhorias Técnicas**:
   - Validação robusta de parâmetros com tratamento de erros
   - Lógica de filtragem eficiente por período
   - Busca inteligente em até 14 dias consecutivos
   - Valores padrão garantidos para todos os filtros
   - Templates sempre recebem variáveis necessárias (sem erros de referência)

**Benefícios para o Usuário:**
- ✅ Encontrar horários disponíveis é muito mais rápido e fácil
- ✅ Filtros permitem buscar horários que se encaixam na rotina do paciente
- ✅ Visualização de múltiplos dias facilita planejamento
- ✅ Interface moderna e intuitiva com feedback visual claro
- ✅ Menos cliques necessários para completar agendamento

**Compatibilidade**: Totalmente compatível com Railway deployment. Todas as queries usam SQLAlchemy ORM.