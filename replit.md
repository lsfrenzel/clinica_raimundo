# Clínica Dr. Raimundo Nunes - Sistema de Gestão Médica

## Visão Geral
Sistema completo de gestão para clínica médica especializada em ginecologia e obstetrícia, com chatbot inteligente para agendamento de consultas, painel administrativo e gestão de pacientes.

## Estado Atual do Projeto ✅
- **Sistema Totalmente Funcional**: Chatbot, agendamentos, painel admin
- **Database Populado**: 9 especialidades, 5 médicos, 448 slots de agendamento
- **Chatbot IA**: Gemini API configurado com sistema rule-based como fallback
- **Agendamentos**: Funcionando perfeitamente via chatbot
- **Replit Environment**: Configurado e funcionando com PostgreSQL integrado

## Funcionalidades Principais

### 🤖 Chatbot Inteligente
- **IA Gemini**: Resposta natural e inteligente
- **Sistema Rule-Based**: Fallback robusto para garantir funcionamento
- **Fluxo Completo**: Especialidade → Médico → Horário → Dados → Confirmação
- **Agendamento Automático**: Criação direta no banco de dados
- **Multi-contexto**: Suporte a usuários autenticados e visitantes

### 🏥 Painel Administrativo  
- **Gestão de Agendamentos**: Visualizar, editar, cancelar
- **Controle de Médicos**: Cadastro e especialidades
- **Horários**: Configuração de agenda médica
- **Relatórios**: Acompanhamento de consultas

### 👥 Gestão de Pacientes
- **Cadastro Completo**: Dados pessoais e histórico
- **Integração**: Usuários autenticados + visitantes
- **Segurança**: Senhas criptografadas com bcrypt

## Tecnologias

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados principal
- **Gemini API**: Inteligência artificial conversacional
- **Flask-Login**: Sistema de autenticação

### Frontend
- **Jinja2**: Templates dinâmicos
- **Bootstrap**: Interface responsiva
- **JavaScript**: Interatividade do chatbot
- **CSS**: Estilização personalizada

## Arquitetura do Chatbot

### Sistema Híbrido Inteligente
1. **Gemini API** (Principal): IA conversacional avançada
2. **Rule-Based** (Fallback): Sistema robusto de regras
3. **Processamento de Ações**: Unificado para ambos sistemas

### Fluxo de Agendamento
```
Usuário → Especialidade → Médico → Horário → Dados → Confirmação → DB
```

### Ações Disponíveis
- `get_specialties`: Listar especialidades
- `select_specialty`: Processar especialidade escolhida  
- `show_doctors`: Mostrar médicos
- `select_doctor`: Processar médico escolhido
- `show_schedules`: Mostrar horários
- `select_schedule`: Processar horário
- `collect_patient_data`: Coletar dados do paciente
- `confirm_booking`: Confirmar dados
- `create_booking`: Criar agendamento no sistema

## Resolução de Problemas Recentes

### ✅ Problema: Chatbot não criava agendamentos
**Causa**: Sistema rule-based não tinha lógica completa de agendamento
**Solução**: 
- Expandido sistema rule-based com fluxo completo
- Melhorada lógica de reconhecimento de especialidades/médicos
- Implementada transição correta para `create_booking`
- Testado e validado: Agendamento ID 12 criado com sucesso

### ✅ Melhoria: Sistema de Fallback Robusto
- Rule-based agora processa agendamentos completos
- Funciona mesmo quando Gemini API falha
- Mantém qualidade de experiência

## Configuração e Deploy

### Variáveis de Ambiente Requeridas
- `DATABASE_URL`: Conexão PostgreSQL (configurado automaticamente no Replit)
- `SESSION_SECRET`: Chave para sessões Flask (configurado automaticamente no Replit)
- `GEMINI_API_KEY`: Chave da API Gemini (opcional - fallback rule-based ativo)

### Configuração Replit
- **Workflow**: Flask App rodando em 0.0.0.0:5000
- **Deploy**: Configurado para autoscale com Gunicorn
- **Proxy**: ProxyFix configurado para ambiente Replit
- **Database**: PostgreSQL integrado do Replit

### Comandos de Execução
```bash
uv run python main.py  # Desenvolvimento
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app  # Produção
```

### Banco de Dados
- **Schema**: SQLAlchemy models (criados automaticamente)
- **População**: Script `scripts/seed_data.py`
- **Conexão**: PostgreSQL via DATABASE_URL do Replit
- **Inicialização**: Execute `uv run python scripts/seed_data.py` para popular dados

## Próximas Melhorias Sugeridas
1. **Notificações**: SMS/Email de confirmação
2. **Pagamentos**: Integração com gateway de pagamento
3. **Relatórios**: Dashboard analítico avançado
4. **Mobile**: App nativo ou PWA
5. **Telemedicina**: Consultas online integradas

## Status de Testes
- ✅ Agendamento via chatbot funcionando
- ✅ Banco de dados populado e funcional
- ✅ Painel administrativo operacional
- ✅ Sistema de fallback testado e aprovado
- ✅ Fluxo completo de usuário validado

## Credenciais de Acesso (Desenvolvimento)
- **Admin**: admin@clinicadrraimundonunes.com.br / admin123
- **Médicos**: [email do médico] / medico123
- **Pacientes**: [email do paciente] / paciente123

---
**Última atualização**: 02/10/2025 - Sistema integrado ao Replit com PostgreSQL e deploy configurado