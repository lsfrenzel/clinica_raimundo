# Appointments blueprint - Sistema de agendamento
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from extensions import db

bp = Blueprint('appointments', __name__)

@bp.route('/agendar')
def agendar():
    """Página principal de agendamento - Passo 1: Escolher especialidade"""
    from models import Especialidade
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    return render_template('appointments/agendar.html', especialidades=especialidades)

@bp.route('/agendar-logado')
@login_required
def agendar_logado():
    """Página de agendamento após login"""
    return redirect(url_for('appointments.agendar'))

@bp.route('/medicos/<int:especialidade_id>')
@login_required
def medicos_por_especialidade(especialidade_id):
    """Passo 2: Escolher médico da especialidade"""
    from models import Especialidade
    especialidade = Especialidade.query.get_or_404(especialidade_id)
    medicos = especialidade.medicos.filter_by(ativo=True).all()
    
    # Buscar próximos horários disponíveis para cada médico
    for medico in medicos:
        medico.proximos_horarios = medico.get_proximos_horarios_livres(limite=3)
    
    return render_template('appointments/medicos.html', 
                         especialidade=especialidade, medicos=medicos)

@bp.route('/horarios/<int:medico_id>')
@login_required
def horarios_medico(medico_id):
    """Passo 3: Escolher horário específico do médico"""
    from models import Medico
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
@login_required
def confirmar():
    """Confirmação de agendamento"""
    if request.method == 'POST':
        # Dados do agendamento
        medico_id = request.form.get('medico_id')
        especialidade_id = request.form.get('especialidade_id')
        data_hora = request.form.get('data_hora')
        
        # Observações opcionais
        observacoes = request.form.get('observacoes', '')
        
        try:
            if not data_hora:
                raise ValueError("data_hora é obrigatório")
            inicio = datetime.fromisoformat(data_hora)
            fim = inicio + timedelta(minutes=30)  # Duração padrão
            
            from models import Agendamento
            # Criar agendamento (apenas para usuários logados)
            agendamento = Agendamento()
            agendamento.medico_id = medico_id
            agendamento.especialidade_id = especialidade_id
            agendamento.inicio = inicio
            agendamento.fim = fim
            agendamento.paciente_id = current_user.id
            agendamento.observacoes = observacoes
            
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
    
    from models import Medico
    medico = Medico.query.get_or_404(medico_id)
    
    return render_template('appointments/confirmar.html', 
                         medico=medico, data_hora=data_hora)

@bp.route('/sucesso/<int:agendamento_id>')
@login_required
def sucesso(agendamento_id):
    """Página de sucesso após agendamento"""
    from models import Agendamento
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verificar se o agendamento pertence ao usuário logado
    if agendamento.paciente_id != current_user.id:
        flash('Agendamento não encontrado.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('appointments/sucesso.html', agendamento=agendamento)

@bp.route('/meus-agendamentos')
@login_required
def meus_agendamentos():
    """Lista agendamentos do usuário logado"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    from models import Agendamento, Medico, User, Especialidade
    from sqlalchemy import or_
    from sqlalchemy.orm import joinedload
    
    # Buscar agendamentos com relacionamentos carregados (eager loading)
    agendamentos = Agendamento.query.options(
        joinedload(Agendamento.medico).joinedload(Medico.usuario),
        joinedload(Agendamento.especialidade)
    ).filter(
        or_(
            Agendamento.paciente_id == current_user.id,
            Agendamento.email_convidado == current_user.email
        )
    ).order_by(Agendamento.inicio.desc()).all()
    
    # Passar datetime atual para o template
    agora = datetime.utcnow()
    
    return render_template('appointments/meus_agendamentos.html', 
                         agendamentos=agendamentos,
                         agora=agora)