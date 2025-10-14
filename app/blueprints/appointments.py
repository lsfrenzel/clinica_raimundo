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
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Iniciando agendamento para usuário {current_user.id}")
            logger.info(f"Dados recebidos - medico_id: {medico_id}, especialidade_id: {especialidade_id}, data_hora: {data_hora}")
            
            if not data_hora:
                raise ValueError("data_hora é obrigatório")
            if not medico_id:
                raise ValueError("medico_id é obrigatório")
            if not especialidade_id:
                raise ValueError("especialidade_id é obrigatório")
                
            # Converter datetime local para UTC para consistência
            # O formulário HTML datetime-local envia horário local (naive)
            # Precisamos assumir que é horário de Brasília (UTC-3)
            from datetime import timezone
            inicio_naive = datetime.fromisoformat(data_hora)
            
            # Assumir que o horário recebido está no timezone de Brasília (UTC-3)
            # e converter para UTC para armazenamento consistente
            brasilia_offset = timezone(timedelta(hours=-3))
            inicio_brasilia = inicio_naive.replace(tzinfo=brasilia_offset)
            inicio = inicio_brasilia.astimezone(timezone.utc).replace(tzinfo=None)
            
            fim = inicio + timedelta(minutes=30)  # Duração padrão
            
            logger.info(f"Horário recebido (local): {inicio_naive}")
            logger.info(f"Horário convertido para UTC: {inicio}")
            
            from models import Agendamento
            # Criar agendamento (apenas para usuários logados)
            agendamento = Agendamento()
            agendamento.medico_id = int(medico_id)
            agendamento.especialidade_id = int(especialidade_id)
            agendamento.inicio = inicio
            agendamento.fim = fim
            agendamento.paciente_id = current_user.id
            agendamento.observacoes = observacoes
            
            logger.info(f"Agendamento criado em memória: {agendamento}")
            
            db.session.add(agendamento)
            db.session.flush()  # Flush para obter o ID antes do commit
            
            logger.info(f"Agendamento com ID {agendamento.id} adicionado à sessão")
            
            db.session.commit()
            
            logger.info(f"Agendamento {agendamento.id} confirmado no banco de dados")
            
            # Verificar se o agendamento foi salvo
            agendamento_salvo = Agendamento.query.get(agendamento.id)
            if not agendamento_salvo:
                logger.error(f"ERRO: Agendamento {agendamento.id} não foi encontrado no banco após commit!")
                raise Exception("Falha ao salvar agendamento no banco de dados")
            
            logger.info(f"Agendamento {agendamento.id} verificado e confirmado no banco")
            
            flash('Agendamento realizado com sucesso!', 'success')
            return redirect(url_for('appointments.sucesso', agendamento_id=agendamento.id))
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao realizar agendamento: {str(e)}", exc_info=True)
            db.session.rollback()
            flash(f'Erro ao realizar agendamento: {str(e)}. Tente novamente.', 'error')
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

@bp.route('/detalhes/<int:agendamento_id>')
@login_required
def detalhes(agendamento_id):
    """Detalhes do agendamento"""
    from models import Agendamento
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verificar se o agendamento pertence ao usuário logado
    if agendamento.paciente_id != current_user.id and agendamento.email_convidado != current_user.email:
        flash('Agendamento não encontrado.', 'error')
        return redirect(url_for('main.index'))
    
    # Converter horário para Brasília para exibição
    from datetime import timezone as tz
    brasilia_offset = tz(timedelta(hours=-3))
    if agendamento.inicio:
        agendamento.inicio_local = agendamento.inicio.replace(tzinfo=tz.utc).astimezone(brasilia_offset).replace(tzinfo=None)
    if agendamento.fim:
        agendamento.fim_local = agendamento.fim.replace(tzinfo=tz.utc).astimezone(brasilia_offset).replace(tzinfo=None)
    
    return render_template('appointments/detalhes.html', agendamento=agendamento)

@bp.route('/cancelar/<int:agendamento_id>', methods=['POST'])
@login_required
def cancelar(agendamento_id):
    """Cancelar agendamento"""
    from models import Agendamento
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verificar se o agendamento pertence ao usuário logado
    if agendamento.paciente_id != current_user.id and agendamento.email_convidado != current_user.email:
        flash('Agendamento não encontrado.', 'error')
        return redirect(url_for('main.index'))
    
    # Verificar se pode ser cancelado (24h de antecedência)
    if not agendamento.pode_ser_cancelado():
        flash('Não é possível cancelar agendamentos com menos de 24h de antecedência.', 'error')
        return redirect(url_for('appointments.meus_agendamentos'))
    
    # Cancelar agendamento
    agendamento.status = 'cancelado'
    db.session.commit()
    
    flash('Agendamento cancelado com sucesso.', 'success')
    return redirect(url_for('appointments.meus_agendamentos'))

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
    
    # Usar UTC para comparação consistente (agendamentos já estão em UTC)
    agora = datetime.utcnow()
    
    # Converter horários para timezone de Brasília para exibição
    from datetime import timezone as tz
    brasilia_offset = tz(timedelta(hours=-3))
    
    for agendamento in agendamentos:
        # Converter de UTC para horário de Brasília para exibição
        if agendamento.inicio:
            agendamento.inicio_local = agendamento.inicio.replace(tzinfo=tz.utc).astimezone(brasilia_offset).replace(tzinfo=None)
        if agendamento.fim:
            agendamento.fim_local = agendamento.fim.replace(tzinfo=tz.utc).astimezone(brasilia_offset).replace(tzinfo=None)
    
    return render_template('appointments/meus_agendamentos.html', 
                         agendamentos=agendamentos,
                         agora=agora)