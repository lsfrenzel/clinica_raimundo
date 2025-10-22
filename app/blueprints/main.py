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
    
    from models import Medico, Agendamento, Especialidade
    from datetime import datetime, timedelta, timezone as tz
    from sqlalchemy.orm import joinedload
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Buscar médico logado
    medico = Medico.query.filter_by(user_id=current_user.id).first()
    if not medico:
        logger.error(f"Perfil médico não encontrado para user_id={current_user.id}")
        return render_template('error.html', 
                             message="Perfil médico não encontrado"), 404
    
    logger.info(f"Médico encontrado: ID={medico.id}, User={current_user.nome}")
    
    # Buscar TODOS os agendamentos do médico com relacionamentos carregados
    agendamentos = Agendamento.query.options(
        joinedload(Agendamento.especialidade),
        joinedload(Agendamento.paciente)
    ).filter(
        Agendamento.medico_id == medico.id
    ).order_by(Agendamento.inicio.desc()).all()
    
    logger.info(f"Total de agendamentos encontrados: {len(agendamentos)}")
    
    # Usar UTC para comparação consistente (como funciona em Meus Agendamentos)
    agora = datetime.utcnow()
    
    # Converter horários de UTC para timezone de Brasília para exibição
    brasilia_offset = tz(timedelta(hours=-3))
    
    for agendamento in agendamentos:
        # Converter de UTC para horário de Brasília
        if agendamento.inicio:
            agendamento.inicio_local = agendamento.inicio.replace(tzinfo=tz.utc).astimezone(brasilia_offset).replace(tzinfo=None)
        if agendamento.fim:
            agendamento.fim_local = agendamento.fim.replace(tzinfo=tz.utc).astimezone(brasilia_offset).replace(tzinfo=None)
    
    # Separar agendamentos futuros e passados (usando UTC)
    # Mostrar TODOS os agendamentos futuros, não apenas próximos 30 dias
    agendamentos_futuros = [a for a in agendamentos if a.inicio >= agora]
    agendamentos_passados = [a for a in agendamentos if a.inicio < agora]
    
    # Ordenar agendamentos futuros por data (próximos primeiro)
    agendamentos_futuros.sort(key=lambda a: a.inicio)
    
    logger.info(f"Agendamentos futuros: {len(agendamentos_futuros)}")
    logger.info(f"Agendamentos passados: {len(agendamentos_passados)}")
    
    # Estatísticas completas
    total_geral = len(agendamentos)
    total_futuros = len(agendamentos_futuros)
    total_passados = len(agendamentos_passados)
    confirmados = len([a for a in agendamentos_futuros if a.status == 'confirmado'])
    pendentes = len([a for a in agendamentos_futuros if a.status == 'agendado'])
    
    return render_template('painel_medico.html', 
                         medico=medico,
                         agendamentos=agendamentos_futuros,
                         agendamentos_passados=agendamentos_passados,
                         total_geral=total_geral,
                         total_futuros=total_futuros,
                         total_passados=total_passados,
                         confirmados=confirmados,
                         pendentes=pendentes)