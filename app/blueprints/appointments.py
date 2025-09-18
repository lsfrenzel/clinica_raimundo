# Appointments blueprint - Sistema de agendamento
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from datetime import datetime, timedelta
from models import Especialidade, Medico, Agendamento, db

bp = Blueprint('appointments', __name__)

@bp.route('/agendar')
def agendar():
    """Página principal de agendamento - Passo 1: Escolher especialidade"""
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    return render_template('appointments/agendar.html', especialidades=especialidades)

@bp.route('/medicos/<int:especialidade_id>')
def medicos_por_especialidade(especialidade_id):
    """Passo 2: Escolher médico da especialidade"""
    especialidade = Especialidade.query.get_or_404(especialidade_id)
    medicos = especialidade.medicos.filter_by(ativo=True).all()
    
    # Buscar próximos horários disponíveis para cada médico
    for medico in medicos:
        medico.proximos_horarios = medico.get_proximos_horarios_livres(limite=3)
    
    return render_template('appointments/medicos.html', 
                         especialidade=especialidade, medicos=medicos)

@bp.route('/horarios/<int:medico_id>')
def horarios_medico(medico_id):
    """Passo 3: Escolher horário específico do médico"""
    medico = Medico.query.get_or_404(medico_id)
    data_param = request.args.get('data')
    
    if data_param:
        try:
            data_inicio = datetime.strptime(data_param, '%Y-%m-%d')
        except ValueError:
            data_inicio = datetime.now()
    else:
        data_inicio = datetime.now()
    
    horarios = medico.get_proximos_horarios_livres(data_inicio, limite=20)
    
    return render_template('appointments/horarios.html', 
                         medico=medico, horarios=horarios)

@bp.route('/confirmar', methods=['GET', 'POST'])
def confirmar():
    """Confirmação de agendamento"""
    if request.method == 'POST':
        # Dados do agendamento
        medico_id = request.form.get('medico_id')
        especialidade_id = request.form.get('especialidade_id')
        data_hora = request.form.get('data_hora')
        
        # Dados do paciente
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
        try:
            inicio = datetime.fromisoformat(data_hora)
            fim = inicio + timedelta(minutes=30)  # Duração padrão
            
            # Criar agendamento
            agendamento = Agendamento(
                medico_id=medico_id,
                especialidade_id=especialidade_id,
                inicio=inicio,
                fim=fim,
                nome_convidado=nome,
                email_convidado=email,
                telefone_convidado=telefone,
                paciente_id=current_user.id if current_user.is_authenticated else None
            )
            
            db.session.add(agendamento)
            db.session.commit()
            
            flash('Agendamento realizado com sucesso!', 'success')
            return redirect(url_for('appointments.sucesso', agendamento_id=agendamento.id))
            
        except Exception as e:
            flash('Erro ao realizar agendamento. Tente novamente.', 'error')
            return redirect(url_for('appointments.agendar'))
    
    # GET - Mostrar formulário de confirmação
    medico_id = request.args.get('medico_id')
    data_hora = request.args.get('data_hora')
    
    if not medico_id or not data_hora:
        return redirect(url_for('appointments.agendar'))
    
    medico = Medico.query.get_or_404(medico_id)
    
    return render_template('appointments/confirmar.html', 
                         medico=medico, data_hora=data_hora)

@bp.route('/sucesso/<int:agendamento_id>')
def sucesso(agendamento_id):
    """Página de sucesso após agendamento"""
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    return render_template('appointments/sucesso.html', agendamento=agendamento)

@bp.route('/meus-agendamentos')
def meus_agendamentos():
    """Lista agendamentos do usuário logado"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    agendamentos = Agendamento.query.filter_by(paciente_id=current_user.id)\
                                   .order_by(Agendamento.inicio.desc()).all()
    
    return render_template('appointments/meus_agendamentos.html', agendamentos=agendamentos)