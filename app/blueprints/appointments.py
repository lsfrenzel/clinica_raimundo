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
    from models import Especialidade, Agenda, Agendamento
    from datetime import timezone as tz
    especialidade = Especialidade.query.get_or_404(especialidade_id)
    medicos = especialidade.medicos.filter_by(ativo=True).all()
    
    # Parâmetros de busca
    data_busca = request.args.get('data_busca')
    periodo = request.args.get('periodo', '')
    
    # Definir data de busca
    if data_busca:
        try:
            data_inicial = datetime.strptime(data_busca, '%Y-%m-%d').date()
        except ValueError:
            data_inicial = datetime.now().date()
    else:
        data_inicial = datetime.now().date()
    
    # Garantir que data_busca tenha valor padrão para o template
    if not data_busca:
        data_busca = data_inicial.strftime('%Y-%m-%d')
    
    # Timezone de Brasília (UTC-3)
    brasilia_offset = tz(timedelta(hours=-3))
    
    # Buscar próximos horários disponíveis para cada médico com filtros
    for medico in medicos:
        medico.proximos_horarios = []
        
        # Buscar horários nos próximos 14 dias
        horarios_encontrados = []
        for dia_offset in range(14):
            data = data_inicial + timedelta(days=dia_offset)
            
            # Buscar agenda do médico para este dia
            agendas_dia = Agenda.query.filter(
                Agenda.medico_id == medico.id,
                Agenda.data == data,
                Agenda.ativo == True
            ).order_by(Agenda.hora_inicio).all()
            
            # Calcular início e fim do dia em horário de Brasília, depois converter para UTC
            # Início: 00:00:00 em Brasília
            inicio_dia_brasilia = datetime.combine(data, datetime.min.time()).replace(tzinfo=brasilia_offset)
            # Fim: próximo dia 00:00:00 em Brasília (exclusive)
            proximo_dia = data + timedelta(days=1)
            fim_dia_brasilia = datetime.combine(proximo_dia, datetime.min.time()).replace(tzinfo=brasilia_offset)
            
            inicio_dia_utc = inicio_dia_brasilia.astimezone(tz.utc).replace(tzinfo=None)
            fim_dia_utc = fim_dia_brasilia.astimezone(tz.utc).replace(tzinfo=None)
            
            # Buscar agendamentos já existentes (em UTC, mas filtrando pelo range correto)
            agendamentos = Agendamento.query.filter(
                Agendamento.medico_id == medico.id,
                Agendamento.inicio >= inicio_dia_utc,
                Agendamento.inicio < fim_dia_utc,
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).all()
            
            # Criar set com horários ocupados (convertendo de UTC para horário local de Brasília)
            agendamentos_existentes = set()
            for agendamento in agendamentos:
                # Converter de UTC para Brasília para comparar com agenda.hora_inicio
                inicio_brasilia = agendamento.inicio.replace(tzinfo=tz.utc).astimezone(brasilia_offset)
                agendamentos_existentes.add(inicio_brasilia.time())
            
            # Verificar horários livres
            for agenda in agendas_dia:
                if agenda.hora_inicio not in agendamentos_existentes:
                    # Filtrar por período se especificado
                    hora = agenda.hora_inicio.hour
                    if periodo == 'manha' and (hora < 6 or hora >= 12):
                        continue
                    elif periodo == 'tarde' and (hora < 12 or hora >= 18):
                        continue
                    elif periodo == 'noite' and (hora < 18 or hora >= 24):
                        continue
                    
                    # Só mostrar horários futuros
                    data_hora = datetime.combine(data, agenda.hora_inicio)
                    if data_hora > datetime.now():
                        horarios_encontrados.append({
                            'data': data,
                            'hora': agenda.hora_inicio,
                            'data_hora_completa': data_hora.isoformat()
                        })
                    
                    # Limitar a 10 horários por médico
                    if len(horarios_encontrados) >= 10:
                        break
            
            if len(horarios_encontrados) >= 10:
                break
        
        medico.proximos_horarios = horarios_encontrados
    
    return render_template('appointments/medicos.html', 
                         especialidade=especialidade, 
                         medicos=medicos,
                         data_busca=data_busca,
                         periodo=periodo,
                         datetime=datetime)

@bp.route('/horarios/<int:medico_id>')
def horarios_medico(medico_id):
    """Passo 3: Escolher horário específico do médico com filtros avançados"""
    from models import Medico, Agenda, Agendamento
    from datetime import timezone as tz
    medico = Medico.query.get_or_404(medico_id)
    
    # Parâmetros de busca
    data_param = request.args.get('data')
    periodo = request.args.get('periodo', '')
    
    # Validar e limitar parâmetro dias
    try:
        dias = int(request.args.get('dias', 1))
        # Limitar a valores permitidos
        if dias not in [1, 3, 7]:
            dias = 1
    except (ValueError, TypeError):
        dias = 1
    
    # Definir a data de busca
    if data_param:
        try:
            data_inicial = datetime.strptime(data_param, '%Y-%m-%d').date()
        except ValueError:
            data_inicial = datetime.now().date()
    else:
        data_inicial = datetime.now().date()
    
    # Timezone de Brasília (UTC-3)
    brasilia_offset = tz(timedelta(hours=-3))
    
    # Buscar horários disponíveis para múltiplos dias
    horarios_por_dia = {}
    
    for dia_offset in range(dias):
        data_atual = data_inicial + timedelta(days=dia_offset)
        horarios_disponiveis = []
        
        # Buscar todas as agendas do médico para este dia
        agendas_dia = Agenda.query.filter(
            Agenda.medico_id == medico.id,
            Agenda.data == data_atual,
            Agenda.ativo == True
        ).order_by(Agenda.hora_inicio).all()
        
        # Calcular início e fim do dia em horário de Brasília, depois converter para UTC
        # Isso garante que busquemos os agendamentos corretos considerando o timezone
        # Início: 00:00:00 em Brasília
        inicio_dia_brasilia = datetime.combine(data_atual, datetime.min.time()).replace(tzinfo=brasilia_offset)
        # Fim: próximo dia 00:00:00 em Brasília (exclusive)
        proximo_dia = data_atual + timedelta(days=1)
        fim_dia_brasilia = datetime.combine(proximo_dia, datetime.min.time()).replace(tzinfo=brasilia_offset)
        
        inicio_dia_utc = inicio_dia_brasilia.astimezone(tz.utc).replace(tzinfo=None)
        fim_dia_utc = fim_dia_brasilia.astimezone(tz.utc).replace(tzinfo=None)
        
        # Buscar agendamentos já existentes para este dia (em UTC, mas filtrando pelo range correto)
        agendamentos = Agendamento.query.filter(
            Agendamento.medico_id == medico.id,
            Agendamento.inicio >= inicio_dia_utc,
            Agendamento.inicio < fim_dia_utc,
            Agendamento.status.in_(['agendado', 'confirmado'])
        ).all()
        
        # Criar set com horários ocupados (convertendo de UTC para horário local de Brasília)
        agendamentos_existentes = set()
        for agendamento in agendamentos:
            # Converter de UTC para Brasília para comparar com agenda.hora_inicio
            inicio_brasilia = agendamento.inicio.replace(tzinfo=tz.utc).astimezone(brasilia_offset)
            agendamentos_existentes.add(inicio_brasilia.time())
        
        # Filtrar apenas horários livres
        for agenda in agendas_dia:
            if agenda.hora_inicio not in agendamentos_existentes:
                # Filtrar por período se especificado
                hora = agenda.hora_inicio.hour
                if periodo == 'manha' and (hora < 6 or hora >= 12):
                    continue
                elif periodo == 'tarde' and (hora < 12 or hora >= 18):
                    continue
                elif periodo == 'noite' and (hora < 18 or hora >= 24):
                    continue
                
                # Combinar data e hora para criar datetime completo
                data_hora = datetime.combine(data_atual, agenda.hora_inicio)
                
                # Só mostrar horários futuros
                if data_hora > datetime.now():
                    horarios_disponiveis.append({
                        'data': data_atual,
                        'hora': agenda.hora_inicio,
                        'duracao': agenda.duracao_minutos,
                        'data_hora_completa': data_hora.isoformat(),
                        'periodo_dia': 'Manhã' if hora < 12 else ('Tarde' if hora < 18 else 'Noite')
                    })
        
        if horarios_disponiveis:
            horarios_por_dia[data_atual] = horarios_disponiveis
    
    # Preparar variáveis para o template
    horarios_disponiveis = horarios_por_dia.get(data_inicial, []) if dias == 1 else []
    
    # Retornar template com todas as variáveis necessárias
    return render_template('appointments/horarios.html', 
                         medico=medico, 
                         horarios_disponiveis=horarios_disponiveis,
                         horarios_por_dia=horarios_por_dia if dias > 1 else {},
                         data_selecionada=data_inicial,
                         periodo=periodo,
                         dias=dias,
                         datetime=datetime)

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