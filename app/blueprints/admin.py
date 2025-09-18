# Admin blueprint - Painel administrativo
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from models import User, Medico, Especialidade, Agendamento, Agenda, db

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator para verificar se usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acesso negado. Você precisa ser administrador.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Dashboard principal do admin"""
    # Estatísticas básicas
    total_agendamentos = Agendamento.query.count()
    agendamentos_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.inicio) == datetime.now().date()
    ).count()
    
    total_medicos = Medico.query.filter_by(ativo=True).count()
    total_pacientes = User.query.filter_by(role='paciente').count()
    
    # Agendamentos recentes
    agendamentos_recentes = Agendamento.query.order_by(
        Agendamento.created_at.desc()
    ).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         total_agendamentos=total_agendamentos,
                         agendamentos_hoje=agendamentos_hoje,
                         total_medicos=total_medicos,
                         total_pacientes=total_pacientes,
                         agendamentos_recentes=agendamentos_recentes)

@bp.route('/agenda')
@login_required
@admin_required
def agenda():
    """Visualização de agenda completa"""
    data_param = request.args.get('data')
    if data_param:
        try:
            data_selecionada = datetime.strptime(data_param, '%Y-%m-%d').date()
        except ValueError:
            data_selecionada = datetime.now().date()
    else:
        data_selecionada = datetime.now().date()
    
    # Buscar agendamentos do dia
    agendamentos = Agendamento.query.filter(
        db.func.date(Agendamento.inicio) == data_selecionada
    ).order_by(Agendamento.inicio).all()
    
    return render_template('admin/agenda.html', 
                         agendamentos=agendamentos,
                         data_selecionada=data_selecionada)

@bp.route('/medicos')
@login_required
@admin_required
def medicos():
    """Gerenciamento de médicos"""
    medicos = Medico.query.all()
    return render_template('admin/medicos.html', medicos=medicos)

@bp.route('/medicos/criar', methods=['GET', 'POST'])
@login_required
@admin_required
def criar_medico():
    """Criar novo médico"""
    if request.method == 'POST':
        # Criar usuário primeiro
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        crm = request.form.get('crm')
        bio = request.form.get('bio')
        
        # Verificar se email já existe
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return render_template('admin/criar_medico.html')
        
        # Criar usuário
        user = User(nome=nome, email=email, telefone=telefone, role='medico')
        user.set_password('123456')  # Senha temporária
        
        db.session.add(user)
        db.session.flush()  # Para obter o ID
        
        # Criar médico
        medico = Medico(user_id=user.id, crm=crm, bio=bio)
        
        db.session.add(medico)
        db.session.commit()
        
        flash(f'Médico {nome} criado com sucesso! Senha temporária: 123456', 'success')
        return redirect(url_for('admin.medicos'))
    
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    return render_template('admin/criar_medico.html', especialidades=especialidades)

@bp.route('/especialidades')
@login_required
@admin_required
def especialidades():
    """Gerenciamento de especialidades"""
    especialidades = Especialidade.query.all()
    return render_template('admin/especialidades.html', especialidades=especialidades)

@bp.route('/agendamentos')
@login_required
@admin_required
def agendamentos():
    """Lista todos os agendamentos"""
    page = request.args.get('page', 1, type=int)
    agendamentos = Agendamento.query.order_by(Agendamento.inicio.desc())\
                                   .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/agendamentos.html', agendamentos=agendamentos)