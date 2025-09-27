# Admin blueprint - Painel administrativo
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from extensions import db

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
    from models import User, Medico, Agendamento
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
    """Visualização de agenda do dia específico"""
    data_param = request.args.get('data')
    if data_param:
        try:
            data_selecionada = datetime.strptime(data_param, '%Y-%m-%d').date()
        except ValueError:
            data_selecionada = datetime.now().date()
    else:
        data_selecionada = datetime.now().date()
    
    from models import Agendamento
    # Buscar agendamentos do dia
    agendamentos = Agendamento.query.filter(
        db.func.date(Agendamento.inicio) == data_selecionada
    ).order_by(Agendamento.inicio).all()
    
    return render_template('admin/agenda_dia.html', 
                         agendamentos=agendamentos,
                         data_selecionada=data_selecionada)

@bp.route('/medicos')
@login_required
@admin_required
def medicos():
    """Gerenciamento de médicos"""
    from models import Medico
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
        
        from models import User, Medico
        # Verificar se email já existe
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return render_template('admin/criar_medico.html')
        
        # Criar usuário
        user = User()
        user.nome = nome
        user.email = email
        user.telefone = telefone
        user.role = 'medico'
        user.set_password('123456')  # Senha temporária
        
        db.session.add(user)
        db.session.flush()  # Para obter o ID
        
        # Criar médico
        medico = Medico()
        medico.user_id = user.id
        medico.crm = crm
        medico.bio = bio
        
        db.session.add(medico)
        db.session.commit()
        
        flash(f'Médico {nome} criado com sucesso! Senha temporária: 123456', 'success')
        return redirect(url_for('admin.medicos'))
    
    from models import Especialidade
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    return render_template('admin/criar_medico.html', especialidades=especialidades)

@bp.route('/especialidades')
@login_required
@admin_required
def especialidades():
    """Gerenciamento de especialidades"""
    from models import Especialidade
    especialidades = Especialidade.query.all()
    return render_template('admin/especialidades.html', especialidades=especialidades)

@bp.route('/especialidades/nova', methods=['GET', 'POST'])
@login_required
@admin_required
def nova_especialidade():
    """Criar nova especialidade"""
    if request.method == 'POST':
        from models import Especialidade
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        duracao_padrao = int(request.form.get('duracao_padrao', 30))
        
        if not nome:
            flash('Nome da especialidade é obrigatório.', 'error')
            return render_template('admin/form_especialidade.html')
        
        # Verificar se já existe
        if Especialidade.query.filter_by(nome=nome).first():
            flash('Especialidade já existe.', 'error')
            return render_template('admin/form_especialidade.html')
        
        especialidade = Especialidade()
        especialidade.nome = nome
        especialidade.descricao = descricao
        especialidade.duracao_padrao = duracao_padrao
        
        db.session.add(especialidade)
        db.session.commit()
        
        flash(f'Especialidade "{nome}" criada com sucesso!', 'success')
        return redirect(url_for('admin.especialidades'))
    
    return render_template('admin/form_especialidade.html')

@bp.route('/especialidades/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_especialidade(id):
    """Editar especialidade"""
    from models import Especialidade
    especialidade = Especialidade.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        duracao_padrao = int(request.form.get('duracao_padrao', 30))
        ativo = request.form.get('ativo') == 'on'
        
        if not nome:
            flash('Nome da especialidade é obrigatório.', 'error')
            return render_template('admin/form_especialidade.html', especialidade=especialidade)
        
        # Verificar se nome já existe em outra especialidade
        existe = Especialidade.query.filter_by(nome=nome).filter(Especialidade.id != id).first()
        if existe:
            flash('Especialidade com este nome já existe.', 'error')
            return render_template('admin/form_especialidade.html', especialidade=especialidade)
        
        especialidade.nome = nome
        especialidade.descricao = descricao
        especialidade.duracao_padrao = duracao_padrao
        especialidade.ativo = ativo
        
        db.session.commit()
        
        flash(f'Especialidade "{nome}" atualizada com sucesso!', 'success')
        return redirect(url_for('admin.especialidades'))
    
    return render_template('admin/form_especialidade.html', especialidade=especialidade)

@bp.route('/especialidades/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_especialidade(id):
    """Excluir especialidade"""
    from models import Especialidade, Agendamento
    especialidade = Especialidade.query.get_or_404(id)
    
    # Verificar se há agendamentos vinculados
    agendamentos = Agendamento.query.filter_by(especialidade_id=id).count()
    if agendamentos > 0:
        flash(f'Não é possível excluir a especialidade "{especialidade.nome}" pois há {agendamentos} agendamentos vinculados.', 'error')
        return redirect(url_for('admin.especialidades'))
    
    nome = especialidade.nome
    db.session.delete(especialidade)
    db.session.commit()
    
    flash(f'Especialidade "{nome}" excluída com sucesso!', 'success')
    return redirect(url_for('admin.especialidades'))

@bp.route('/agendamentos')
@login_required
@admin_required
def agendamentos():
    """Lista todos os agendamentos"""
    from models import Agendamento
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'todos')
    
    query = Agendamento.query
    if status != 'todos':
        query = query.filter_by(status=status)
    
    agendamentos = query.order_by(Agendamento.inicio.desc())\
                       .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/agendamentos.html', agendamentos=agendamentos, status_filtro=status)

@bp.route('/agenda/gerenciar')
@login_required
@admin_required  
def gerenciar_agenda():
    """Gerenciar agenda dos médicos"""
    from models import Medico, Agenda
    import calendar
    
    medicos = Medico.query.filter_by(ativo=True).all()
    
    # Buscar agenda da semana atual
    hoje = datetime.now().date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    agenda = Agenda.query.filter(
        Agenda.data >= inicio_semana,
        Agenda.data <= fim_semana
    ).order_by(Agenda.data, Agenda.hora_inicio).all()
    
    # Função auxiliar para calcular duração
    def calcular_duracao(hora_inicio, hora_fim):
        return (hora_fim.hour * 60 + hora_fim.minute) - (hora_inicio.hour * 60 + hora_inicio.minute)
    
    # Adicionar função auxiliar para templates
    from jinja2 import Environment
    
    return render_template('admin/agenda.html', 
                         medicos=medicos, 
                         agenda=agenda, 
                         inicio_semana=inicio_semana, 
                         fim_semana=fim_semana,
                         timedelta=timedelta,
                         calcular_duracao=calcular_duracao)

@bp.route('/agenda/criar', methods=['GET', 'POST'])
@login_required
@admin_required
def criar_agenda():
    """Criar novos horários na agenda"""
    from models import Medico, Agenda
    
    if request.method == 'POST':
        medico_id_str = request.form.get('medico_id')
        data_inicio_str = request.form.get('data_inicio')
        data_fim_str = request.form.get('data_fim')
        hora_inicio_str = request.form.get('hora_inicio')
        hora_fim_str = request.form.get('hora_fim')
        
        if not all([medico_id_str, data_inicio_str, data_fim_str, hora_inicio_str, hora_fim_str]):
            flash('Todos os campos são obrigatórios.', 'error')
            medicos = Medico.query.filter_by(ativo=True).all()
            return render_template('admin/criar_agenda.html', medicos=medicos)
        
        medico_id = int(medico_id_str)
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()
        intervalo = int(request.form.get('intervalo', 30))
        dias_semana = request.form.getlist('dias_semana')
        
        total_criados = 0
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            # Verificar se é um dia da semana selecionado (0=segunda, 6=domingo)
            if str(data_atual.weekday()) in dias_semana:
                
                # Criar slots para o dia
                hora_atual = datetime.combine(data_atual, hora_inicio)
                fim_dia = datetime.combine(data_atual, hora_fim)
                
                while hora_atual < fim_dia:
                    fim_slot = hora_atual + timedelta(minutes=intervalo)
                    
                    # Verificar se já existe
                    existe = Agenda.query.filter_by(
                        medico_id=medico_id,
                        data=data_atual,
                        hora_inicio=hora_atual.time()
                    ).first()
                    
                    if not existe:
                        agenda = Agenda()
                        agenda.medico_id = medico_id
                        agenda.data = data_atual
                        agenda.hora_inicio = hora_atual.time()
                        agenda.hora_fim = fim_slot.time()
                        agenda.ativo = True
                        agenda.duracao_minutos = intervalo
                        db.session.add(agenda)
                        total_criados += 1
                    
                    hora_atual = fim_slot
            
            data_atual += timedelta(days=1)
        
        db.session.commit()
        flash(f'{total_criados} horários criados com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_agenda'))
    
    medicos = Medico.query.filter_by(ativo=True).all()
    return render_template('admin/criar_agenda.html', medicos=medicos)

@bp.route('/medicos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_medico(id):
    """Editar médico"""
    from models import Medico, Especialidade, User
    medico = Medico.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        crm = request.form.get('crm')
        bio = request.form.get('bio')
        ativo = request.form.get('ativo') == 'on'
        especialidades_ids = request.form.getlist('especialidades')
        
        # Atualizar usuário
        medico.usuario.nome = nome
        medico.usuario.email = email
        medico.usuario.telefone = telefone
        medico.usuario.ativo = ativo
        
        # Atualizar médico
        medico.crm = crm
        medico.bio = bio
        medico.ativo = ativo
        
        # Atualizar especialidades
        especialidades = Especialidade.query.filter(Especialidade.id.in_(especialidades_ids)).all()
        medico.especialidades = especialidades
        
        db.session.commit()
        
        flash(f'Médico "{nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('admin.medicos'))
    
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    return render_template('admin/form_medico.html', medico=medico, especialidades=especialidades)

@bp.route('/medicos/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_medico(id):
    """Excluir médico"""
    from models import Medico, Agendamento
    medico = Medico.query.get_or_404(id)
    
    # Verificar se há agendamentos futuros
    agendamentos = Agendamento.query.filter(
        Agendamento.medico_id == id,
        Agendamento.inicio > datetime.now()
    ).count()
    
    if agendamentos > 0:
        flash(f'Não é possível excluir o médico "{medico.usuario.nome}" pois há {agendamentos} agendamentos futuros.', 'error')
        return redirect(url_for('admin.medicos'))
    
    nome = medico.usuario.nome
    
    # Excluir usuário (cascata excluirá o médico)
    db.session.delete(medico.usuario)
    db.session.commit()
    
    flash(f'Médico "{nome}" excluído com sucesso!', 'success')
    return redirect(url_for('admin.medicos'))

@bp.route('/agenda/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_agenda(id):
    """Excluir horário da agenda"""
    from models import Agenda, Agendamento
    agenda = Agenda.query.get_or_404(id)
    
    # Verificar se há agendamento marcado
    agendamento = Agendamento.query.filter(
        Agendamento.medico_id == agenda.medico_id,
        db.func.date(Agendamento.inicio) == agenda.data,
        db.func.time(Agendamento.inicio) == agenda.hora_inicio
    ).first()
    
    if agendamento:
        flash('Não é possível excluir este horário pois há um agendamento marcado.', 'error')
        return redirect(url_for('admin.gerenciar_agenda'))
    
    db.session.delete(agenda)
    db.session.commit()
    
    flash('Horário excluído com sucesso!', 'success')
    return redirect(url_for('admin.gerenciar_agenda'))