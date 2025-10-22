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

### ✅ Assistente Virtual Sofia - Inteligência Avançada com Gemini AI (22/10/2025)

**Objetivo**: Transformar o assistente virtual em uma ferramenta verdadeiramente inteligente com acesso completo ao banco de dados e capacidades conversacionais avançadas.

**Funcionalidades Implementadas:**

1. **Motor de IA Google Gemini** (`chatbot_service.py`):
   - Integração completa com Google Gemini AI (modelo gemini-2.5-flash)
   - System prompt avançado com contexto dinâmico do banco de dados
   - Fallback automático para OpenAI (se disponível) ou sistema baseado em regras
   - Temperatura configurada para conversas naturais e empáticas
   - Respostas em formato JSON estruturado para processamento consistente

2. **Acesso Completo ao Banco de Dados**:
   - **Consultas**: Buscar especialidades, médicos, horários disponíveis, agendamentos
   - **Criação**: Agendar novas consultas com validação completa
   - **Modificação**: Cancelar e remarcar agendamentos existentes
   - **Análise**: Estatísticas da clínica, histórico de consultas, métricas
   - **Contexto do usuário**: Informações personalizadas baseadas no histórico

3. **Capacidades Avançadas**:
   - Gerenciamento de contexto conversacional (lembra informações da conversa)
   - Validação inteligente de dados antes de criar agendamentos
   - Sugestões contextuais baseadas no histórico do usuário
   - Tratamento de timezone (Brasília UTC-3) automático
   - Verificação de conflitos de agendamento em tempo real
   - Respostas empáticas e personalizadas usando o nome do paciente

4. **Interface Premium** (`app/templates/chatbot.html`):
   - Design sofisticado com gradientes e glassmorphism
   - Mensagens com avatares e animações suaves
   - Renderização rica de dados (especialidades, médicos, horários)
   - Botões interativos para ações rápidas
   - Cards clicáveis para seleção de especialidades/médicos/horários
   - Indicador de status online com animação pulsante
   - Loading indicator premium durante processamento

5. **Ações Rápidas Disponíveis**:
   - Agendar Consulta
   - Ver Especialidades
   - Ver Médicos
   - Meus Agendamentos
   - Remarcar Consulta

**System Prompt Contextual**:
O assistente possui um system prompt extremamente detalhado que inclui:
- Informações atualizadas da clínica (número de médicos, especialidades)
- Personalidade definida (Sofia - empática e profissional)
- Capacidades e limitações claramente definidas
- Diretrizes de comunicação (o que fazer e o que evitar)
- Contexto do usuário atual (agendamentos recentes, histórico)
- Formato de resposta obrigatório em JSON

**Tecnologias**:
- Google Gemini API (gemini-2.5-flash) - Motor principal
- OpenAI API - Fallback secundário
- SQLAlchemy ORM - Acesso ao banco de dados
- Flask - Backend API
- JavaScript vanilla - Frontend interativo

**Benefícios**:
- ✅ Conversas naturais e inteligentes com IA avançada
- ✅ Acesso completo aos dados da clínica em tempo real
- ✅ Agendamento, cancelamento e reagendamento via chat
- ✅ Interface visual rica e moderna
- ✅ Respostas personalizadas baseadas no histórico do usuário
- ✅ Fallback garantido mesmo sem API key
- ✅ Experiência premium para os pacientes

**Compatibilidade**: Totalmente compatível com Railway deployment. Suporta GEMINI_API_KEY via secrets.

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

### ✅ Correção de Timezone no Filtro de Horários (22/10/2025)

**Problema Identificado**: O filtro de horários disponíveis não estava funcionando corretamente no Railway com PostgreSQL devido a um problema de timezone. Agendamentos salvos em UTC (horário universal) não estavam sendo corretamente comparados com as agendas em horário local de Brasília (UTC-3).

**Cenário do Bug**:
- Paciente agenda consulta para 15/10/2025 às 21:00 (Brasília)
- Sistema salva como 16/10/2025 às 00:00 (UTC)
- Ao buscar horários disponíveis para 15/10, o sistema não encontrava esse agendamento
- Resultado: horário aparecia como disponível mesmo já estando agendado

**Solução Implementada**:

1. **Conversão Correta de Range de Datas**:
   - Cada dia de busca é convertido para um range completo em horário de Brasília
   - O range é então convertido para UTC para consultar o banco de dados
   - Exemplo: dia 15/10 em Brasília = 15/10 03:00 UTC até 16/10 02:59 UTC

2. **Normalização de Horários para Comparação**:
   - Agendamentos recuperados do banco (em UTC) são convertidos para Brasília
   - Apenas o horário (time) é extraído para comparar com `agenda.hora_inicio`
   - Garante comparação precisa entre horários ocupados e disponíveis

3. **Arquivos Modificados**:
   - `app/blueprints/appointments.py`:
     - Função `horarios_medico()` (linha 113-221)
     - Função `medicos_por_especialidade()` (linha 25-126)

**Benefícios**:
- ✅ Filtros de horários agora funcionam corretamente no Railway
- ✅ Agendamentos noturnos são corretamente identificados
- ✅ Não há mais conflitos de duplo agendamento
- ✅ Sistema mantém compatibilidade total com PostgreSQL em produção

**Nota Técnica**: A solução segue o padrão de armazenar datetimes em UTC no banco de dados e converter para timezone local (Brasília UTC-3) apenas para display e comparações lógicas. Este é o padrão recomendado para aplicações multi-timezone.

### ✅ Refinamento de Lógica de Timezone - Boundary Handling (22/10/2025)

**Problema Identificado**: A implementação anterior usava `datetime.max.time()` que pode causar problemas de precisão de ponto flutuante e comportamento indefinido em comparações de limite de dia.

**Solução Implementada**:

1. **Boundary Exclusivo (Exclusive End)**:
   - Alterado de `fim_dia_brasilia = datetime.combine(data, datetime.max.time())` para usar o próximo dia à meia-noite
   - Novo padrão: `[00:00 Brasília, próximo dia 00:00 Brasília)` (exclusive)
   - Isso é mais determinístico e evita problemas de precisão

2. **Operador de Comparação**:
   - Alterado de `Agendamento.inicio <= fim_dia_utc` para `Agendamento.inicio < fim_dia_utc`
   - Garante que agendamentos exatamente à meia-noite sejam contabilizados apenas no próximo dia
   - Elimina duplicação de slots entre dias consecutivos

3. **Arquivos Modificados**:
   - `app/blueprints/appointments.py`:
     - Função `medicos_por_especialidade()` (linhas 69-85)
     - Função `horarios_medico()` (linhas 177-194)

**Benefícios**:
- ✅ Lógica de boundary mais robusta e determinística
- ✅ Não há mais problemas de precisão com datetime.max.time()
- ✅ Garantia de que slots não são duplicados em transições de dia
- ✅ Consultas ao banco de dados são mais precisas

**Aprovação Técnica**: Revisado e aprovado pelo Architect. Código produção-ready para Railway deployment.