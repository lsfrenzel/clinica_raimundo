# Main blueprint - Homepage and general routes
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage com agendamento rápido"""
    from models import Especialidade, Medico
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    medicos = Medico.query.filter_by(ativo=True).limit(6).all()
    return render_template('index.html', especialidades=especialidades, medicos=medicos)

@bp.route('/sobre')
def sobre():
    """Página sobre a clínica"""
    return render_template('sobre.html')

@bp.route('/especialidades')
def especialidades():
    """Lista todas as especialidades"""
    from models import Especialidade
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    return render_template('especialidades.html', especialidades=especialidades)

@bp.route('/medicos')
def medicos():
    """Lista todos os médicos"""
    from models import Medico
    medicos = Medico.query.filter_by(ativo=True).all()
    return render_template('medicos.html', medicos=medicos)

@bp.route('/chatbot')
def chatbot():
    """Página do chatbot inteligente"""
    return render_template('chatbot.html')

@bp.route('/painel-medico')
@login_required
def painel_medico():
    """Painel para médicos visualizarem seus agendamentos"""
    if not current_user.is_medico():
        return render_template('error.html', 
                             message="Acesso restrito a médicos"), 403
    
    from models import Medico, Agendamento
    from datetime import datetime, timedelta
    
    # Buscar médico logado
    medico = Medico.query.filter_by(user_id=current_user.id).first()
    if not medico:
        return render_template('error.html', 
                             message="Perfil médico não encontrado"), 404
    
    # Data de hoje e próximos dias (usando UTC para consistência com agendamentos)
    hoje = datetime.utcnow()
    data_limite = hoje + timedelta(days=30)
    
    # Agendamentos futuros
    agendamentos = Agendamento.query.filter(
        Agendamento.medico_id == medico.id,
        Agendamento.inicio >= hoje,
        Agendamento.inicio <= data_limite
    ).order_by(Agendamento.inicio).all()
    
    # Estatísticas básicas
    total_agendamentos = len(agendamentos)
    confirmados = len([a for a in agendamentos if a.status == 'confirmado'])
    pendentes = len([a for a in agendamentos if a.status == 'agendado'])
    
    return render_template('painel_medico.html', 
                         medico=medico,
                         agendamentos=agendamentos,
                         total_agendamentos=total_agendamentos,
                         confirmados=confirmados,
                         pendentes=pendentes)