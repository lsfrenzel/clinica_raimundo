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

@bp.route('/init-database')
def init_database():
    """Rota especial para inicializar o banco de dados - USE APENAS UMA VEZ"""
    from models import User, Especialidade, Medico, Agenda
    from datetime import time
    
    try:
        # Criar tabelas
        db.create_all()
        
        # Verificar se já existe admin
        admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
        if admin:
            return jsonify({
                'status': 'already_exists',
                'message': 'Banco já foi inicializado! Admin já existe.',
                'admin_email': 'admin@clinicadrraimundonunes.com.br',
                'admin_password': 'admin123'
            })
        
        # Criar especialidades
        especialidades_data = [
            {'nome': 'DIU e Implanon', 'descricao': 'Inserção e acompanhamento de DIU hormonal e implantes contraceptivos.', 'duracao_padrao': 45},
            {'nome': 'Pré-Natal de Alto Risco', 'descricao': 'Acompanhamento especializado de gestações de alto risco.', 'duracao_padrao': 60},
            {'nome': 'Hipertensão e Diabetes Gestacional', 'descricao': 'Tratamento de complicações metabólicas na gestação.', 'duracao_padrao': 45},
            {'nome': 'Mastologia', 'descricao': 'Prevenção, diagnóstico e tratamento de doenças da mama.', 'duracao_padrao': 30},
            {'nome': 'Uroginecologia', 'descricao': 'Tratamento de incontinência urinária e prolapsos genitais.', 'duracao_padrao': 45},
            {'nome': 'Climatério e Menopausa', 'descricao': 'Acompanhamento e tratamento de sintomas do climatério.', 'duracao_padrao': 30},
            {'nome': 'PTGI', 'descricao': 'Programa de Tratamento de Gestações Indesejadas.', 'duracao_padrao': 60},
            {'nome': 'Sexualidade', 'descricao': 'Orientação e tratamento de disfunções sexuais femininas.', 'duracao_padrao': 45},
            {'nome': 'Reprodução Humana', 'descricao': 'Investigação e tratamento de infertilidade conjugal.', 'duracao_padrao': 60}
        ]
        
        especialidades = []
        for esp_data in especialidades_data:
            esp = Especialidade(**esp_data)
            esp.ativo = True
            db.session.add(esp)
            especialidades.append(esp)
        db.session.commit()
        
        # Criar admin
        admin = User()
        admin.nome = "Administrador"
        admin.email = "admin@clinicadrraimundonunes.com.br"
        admin.telefone = "(11) 99999-9999"
        admin.role = "admin"
        admin.ativo = True
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        
        # Criar médicos
        medicos_data = [
            {'nome': 'Dr. Raimundo Nunes', 'crm': 'CRM/SP 123456', 'email': 'raimundo.nunes@clinicadrraimundonunes.com.br', 'telefone': '(11) 99001-1234', 'especialidades': ['Pré-Natal de Alto Risco']},
            {'nome': 'Dra. Ana Silva', 'crm': 'CRM/SP 234567', 'email': 'ana.silva@clinicadrraimundonunes.com.br', 'telefone': '(11) 99002-1234', 'especialidades': ['Mastologia']},
            {'nome': 'Dr. Carlos Oliveira', 'crm': 'CRM/SP 345678', 'email': 'carlos.oliveira@clinicadrraimundonunes.com.br', 'telefone': '(11) 99003-1234', 'especialidades': ['Reprodução Humana']},
            {'nome': 'Dra. Maria Santos', 'crm': 'CRM/SP 456789', 'email': 'maria.santos@clinicadrraimundonunes.com.br', 'telefone': '(11) 99004-1234', 'especialidades': ['Uroginecologia']},
            {'nome': 'Dr. Ricardo Mendes', 'crm': 'CRM/SP 567890', 'email': 'ricardo.mendes@clinicadrraimundonunes.com.br', 'telefone': '(11) 99005-1234', 'especialidades': ['Climatério e Menopausa']}
        ]
        
        medicos = []
        for med_data in medicos_data:
            user = User()
            user.nome = med_data['nome']
            user.email = med_data['email']
            user.telefone = med_data['telefone']
            user.role = "medico"
            user.ativo = True
            user.set_password("medico123")
            db.session.add(user)
            db.session.commit()
            
            medico = Medico()
            medico.user_id = user.id
            medico.crm = med_data['crm']
            medico.bio = f"Especialista em {med_data['especialidades'][0]} com mais de 10 anos de experiência."
            medico.ativo = True
            db.session.add(medico)
            db.session.flush()
            
            for esp_nome in med_data['especialidades']:
                especialidade = next((e for e in especialidades if e.nome == esp_nome), None)
                if especialidade:
                    medico.especialidades.append(especialidade)
            
            medicos.append(medico)
        db.session.commit()
        
        # Criar agenda (próximos 30 dias)
        hoje = datetime.now().date()
        agenda_count = 0
        for medico in medicos:
            for dia_offset in range(30):
                data = hoje + timedelta(days=dia_offset)
                if data.weekday() >= 5:
                    continue
                for hora in range(8, 17):
                    agenda = Agenda()
                    agenda.medico_id = medico.id
                    agenda.data = data
                    agenda.hora_inicio = time(hora, 0)
                    agenda.hora_fim = time(hora + 1, 0)
                    agenda.duracao_minutos = 60
                    agenda.tipo = 'presencial'
                    agenda.ativo = True
                    db.session.add(agenda)
                    agenda_count += 1
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Banco de dados inicializado com sucesso!',
            'dados_criados': {
                'especialidades': len(especialidades),
                'medicos': len(medicos),
                'agenda_slots': agenda_count
            },
            'credenciais': {
                'admin_email': 'admin@clinicadrraimundonunes.com.br',
                'admin_password': 'admin123',
                'medicos_password': 'medico123'
            },
            'proximo_passo': 'Acesse /auth/login e faça login com as credenciais do admin'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Erro ao inicializar banco: {str(e)}'
        }), 500

@bp.route('/diagnostico-detalhado')
def diagnostico_detalhado():
    """Rota para diagnóstico detalhado do banco de dados"""
    from models import User, Especialidade, Medico, Agenda
    from sqlalchemy import text
    
    try:
        resultado = {
            'database_url': 'Conectado (URL oculta por segurança)',
            'especialidades': [],
            'medicos': [],
            'usuarios': [],
            'tabela_associacao': []
        }
        
        especialidades = Especialidade.query.all()
        for esp in especialidades:
            medicos_list = esp.medicos.filter_by(ativo=True).all()
            resultado['especialidades'].append({
                'id': esp.id,
                'nome': esp.nome,
                'ativo': esp.ativo,
                'medicos_count': len(medicos_list),
                'medicos': [{'id': m.id, 'crm': m.crm, 'nome': User.query.get(m.user_id).nome if User.query.get(m.user_id) else 'N/A'} for m in medicos_list]
            })
        
        medicos = Medico.query.all()
        for medico in medicos:
            user = User.query.get(medico.user_id)
            especialidades_list = [e.nome for e in medico.especialidades]
            resultado['medicos'].append({
                'id': medico.id,
                'nome': user.nome if user else 'N/A',
                'crm': medico.crm,
                'ativo': medico.ativo,
                'user_id': medico.user_id,
                'especialidades': especialidades_list
            })
        
        users = User.query.filter_by(role='medico').all()
        for user in users:
            resultado['usuarios'].append({
                'id': user.id,
                'nome': user.nome,
                'email': user.email,
                'role': user.role,
                'ativo': user.ativo
            })
        
        with db.engine.connect() as connection:
            query = text("SELECT * FROM medico_especialidade")
            result = connection.execute(query)
            for row in result:
                resultado['tabela_associacao'].append({
                    'medico_id': row[0],
                    'especialidade_id': row[1]
                })
        
        return jsonify(resultado)
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Erro: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@bp.route('/corrigir-medicos')
def corrigir_medicos():
    """Rota para diagnosticar e corrigir associações de médicos com especialidades"""
    from models import User, Especialidade, Medico, Agenda
    from datetime import time
    
    try:
        resultado = {
            'diagnostico': {},
            'correcoes': [],
            'status': 'success'
        }
        
        # 1. DIAGNÓSTICO
        especialidades = Especialidade.query.all()
        medicos = Medico.query.all()
        users = User.query.all()
        agendas = Agenda.query.filter_by(ativo=True).count()
        
        resultado['diagnostico'] = {
            'total_especialidades': len(especialidades),
            'total_medicos': len(medicos),
            'total_usuarios': len(users),
            'total_agendas_ativas': agendas,
            'especialidades_detalhes': []
        }
        
        # Detalhar cada especialidade
        for esp in especialidades:
            medicos_count = esp.medicos.filter_by(ativo=True).count()
            resultado['diagnostico']['especialidades_detalhes'].append({
                'id': esp.id,
                'nome': esp.nome,
                'medicos_ativos': medicos_count
            })
        
        # 2. CORREÇÃO: Criar especialidades se não existirem
        especialidades_data = [
            {'nome': 'DIU e Implanon', 'descricao': 'Inserção e acompanhamento de DIU hormonal e implantes contraceptivos.', 'duracao_padrao': 45},
            {'nome': 'Pré-Natal de Alto Risco', 'descricao': 'Acompanhamento especializado de gestações de alto risco.', 'duracao_padrao': 60},
            {'nome': 'Hipertensão e Diabetes Gestacional', 'descricao': 'Tratamento de complicações metabólicas na gestação.', 'duracao_padrao': 45},
            {'nome': 'Mastologia', 'descricao': 'Prevenção, diagnóstico e tratamento de doenças da mama.', 'duracao_padrao': 30},
            {'nome': 'Uroginecologia', 'descricao': 'Tratamento de incontinência urinária e prolapsos genitais.', 'duracao_padrao': 45},
            {'nome': 'Climatério e Menopausa', 'descricao': 'Acompanhamento e tratamento de sintomas do climatério.', 'duracao_padrao': 30},
            {'nome': 'PTGI', 'descricao': 'Programa de Tratamento de Gestações Indesejadas.', 'duracao_padrao': 60},
            {'nome': 'Sexualidade', 'descricao': 'Orientação e tratamento de disfunções sexuais femininas.', 'duracao_padrao': 45},
            {'nome': 'Reprodução Humana', 'descricao': 'Investigação e tratamento de infertilidade conjugal.', 'duracao_padrao': 60}
        ]
        
        especialidades_criadas = 0
        for esp_data in especialidades_data:
            esp = Especialidade.query.filter_by(nome=esp_data['nome']).first()
            if not esp:
                esp = Especialidade(**esp_data)
                esp.ativo = True
                db.session.add(esp)
                especialidades_criadas += 1
        
        if especialidades_criadas > 0:
            db.session.commit()
            resultado['correcoes'].append(f'✅ {especialidades_criadas} especialidades criadas')
        
        # Recarregar especialidades
        especialidades = Especialidade.query.all()
        
        # 3. CRIAR MÉDICOS SE NÃO EXISTIREM
        medicos_count = Medico.query.count()
        if medicos_count == 0:
            resultado['correcoes'].append('⚠️ Nenhum médico encontrado. Criando médicos...')
            
            medicos_data = [
                {'nome': 'Dr. Raimundo Nunes', 'crm': 'CRM/SP 123456', 'email': 'raimundo.nunes@clinicadrraimundonunes.com.br', 'telefone': '(11) 99001-1234', 'especialidades': ['Pré-Natal de Alto Risco', 'DIU e Implanon', 'Hipertensão e Diabetes Gestacional']},
                {'nome': 'Dra. Ana Silva', 'crm': 'CRM/SP 234567', 'email': 'ana.silva@clinicadrraimundonunes.com.br', 'telefone': '(11) 99002-1234', 'especialidades': ['Mastologia', 'Climatério e Menopausa']},
                {'nome': 'Dr. Carlos Oliveira', 'crm': 'CRM/SP 345678', 'email': 'carlos.oliveira@clinicadrraimundonunes.com.br', 'telefone': '(11) 99003-1234', 'especialidades': ['Reprodução Humana', 'PTGI']},
                {'nome': 'Dra. Maria Santos', 'crm': 'CRM/SP 456789', 'email': 'maria.santos@clinicadrraimundonunes.com.br', 'telefone': '(11) 99004-1234', 'especialidades': ['Uroginecologia', 'Sexualidade']},
                {'nome': 'Dr. Ricardo Mendes', 'crm': 'CRM/SP 567890', 'email': 'ricardo.mendes@clinicadrraimundonunes.com.br', 'telefone': '(11) 99005-1234', 'especialidades': ['Climatério e Menopausa', 'Sexualidade', 'Mastologia']}
            ]
            
            medicos_criados = []
            for med_data in medicos_data:
                user = User.query.filter_by(email=med_data['email']).first()
                if not user:
                    user = User()
                    user.nome = med_data['nome']
                    user.email = med_data['email']
                    user.telefone = med_data['telefone']
                    user.role = "medico"
                    user.ativo = True
                    user.set_password("medico123")
                    db.session.add(user)
                    db.session.commit()
                
                medico = Medico.query.filter_by(user_id=user.id).first()
                if not medico:
                    medico = Medico()
                    medico.user_id = user.id
                    medico.crm = med_data['crm']
                    medico.bio = f"Especialista com mais de 10 anos de experiência."
                    medico.ativo = True
                    db.session.add(medico)
                    db.session.flush()
                
                for esp_nome in med_data['especialidades']:
                    especialidade = next((e for e in especialidades if e.nome == esp_nome), None)
                    if especialidade and especialidade not in medico.especialidades:
                        medico.especialidades.append(especialidade)
                
                medicos_criados.append(medico)
            
            db.session.commit()
            resultado['correcoes'].append(f'✅ {len(medicos_criados)} médicos criados')
        
        # 4. CORRIGIR ASSOCIAÇÕES DE MÉDICOS EXISTENTES
        correcoes_associacoes = [
            {'crm': 'CRM/SP 123456', 'especialidades': ['Pré-Natal de Alto Risco', 'DIU e Implanon', 'Hipertensão e Diabetes Gestacional']},
            {'crm': 'CRM/SP 234567', 'especialidades': ['Mastologia', 'Climatério e Menopausa']},
            {'crm': 'CRM/SP 345678', 'especialidades': ['Reprodução Humana', 'PTGI']},
            {'crm': 'CRM/SP 456789', 'especialidades': ['Uroginecologia', 'Sexualidade']},
            {'crm': 'CRM/SP 567890', 'especialidades': ['Climatério e Menopausa', 'Sexualidade', 'Mastologia']}
        ]
        
        associacoes_corrigidas = 0
        for corr in correcoes_associacoes:
            medico = Medico.query.filter_by(crm=corr['crm']).first()
            if medico:
                medico.especialidades = []
                for esp_nome in corr['especialidades']:
                    esp = Especialidade.query.filter_by(nome=esp_nome).first()
                    if esp and esp not in medico.especialidades:
                        medico.especialidades.append(esp)
                        associacoes_corrigidas += 1
        
        if associacoes_corrigidas > 0:
            db.session.commit()
            resultado['correcoes'].append(f'✅ {associacoes_corrigidas} associações médico-especialidade corrigidas')
        
        # 5. CRIAR AGENDAS SE NECESSÁRIO
        hoje = datetime.now().date()
        agenda_count = 0
        
        for medico in Medico.query.filter_by(ativo=True).all():
            agendas_futuras = Agenda.query.filter(
                Agenda.medico_id == medico.id,
                Agenda.data >= hoje,
                Agenda.ativo == True
            ).count()
            
            if agendas_futuras < 10:
                for dia_offset in range(30):
                    data = hoje + timedelta(days=dia_offset)
                    if data.weekday() >= 5:
                        continue
                    
                    existe = Agenda.query.filter_by(
                        medico_id=medico.id,
                        data=data
                    ).first()
                    
                    if not existe:
                        for hora in range(8, 17):
                            agenda = Agenda()
                            agenda.medico_id = medico.id
                            agenda.data = data
                            agenda.hora_inicio = time(hora, 0)
                            agenda.hora_fim = time(hora + 1, 0)
                            agenda.duracao_minutos = 60
                            agenda.tipo = 'presencial'
                            agenda.ativo = True
                            db.session.add(agenda)
                            agenda_count += 1
        
        if agenda_count > 0:
            db.session.commit()
            resultado['correcoes'].append(f'✅ {agenda_count} slots de agenda criados')
        
        # 6. RESULTADO FINAL
        resultado['resultado_final'] = {}
        for esp in Especialidade.query.all():
            medicos_ativos = esp.medicos.filter_by(ativo=True).count()
            resultado['resultado_final'][esp.nome] = {
                'id': esp.id,
                'medicos_ativos': medicos_ativos
            }
        
        # URLs para teste
        resultado['urls_teste'] = [
            '/appointments/medicos/1',
            '/appointments/medicos/2',
            '/appointments/medicos/3',
            '/appointments/medicos/4',
            '/appointments/medicos/5'
        ]
        
        return jsonify(resultado)
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Erro ao corrigir médicos: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

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
        
        from models import User, Medico, Especialidade
        # Verificar se email já existe
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            especialidades = Especialidade.query.filter_by(ativo=True).all()
            return render_template('admin/form_medico.html', especialidades=especialidades)
        
        # Criar usuário
        user = User()
        user.nome = nome
        user.email = email
        user.telefone = telefone
        user.role = 'medico'
        user.ativo = True
        
        # Senha personalizada ou padrão
        senha = request.form.get('senha', '').strip()
        if not senha:
            senha = 'medico123'  # Senha padrão
        user.set_password(senha)
        
        db.session.add(user)
        db.session.flush()  # Para obter o ID
        
        # Criar médico
        medico = Medico()
        medico.user_id = user.id
        medico.crm = crm
        medico.bio = bio
        medico.ativo = True
        foto_url = request.form.get('foto_url')
        if foto_url:
            medico.foto_url = foto_url
        
        db.session.add(medico)
        db.session.flush()
        
        # Adicionar especialidades
        especialidades_ids = request.form.getlist('especialidades')
        for esp_id in especialidades_ids:
            especialidade = Especialidade.query.get(int(esp_id))
            if especialidade:
                medico.especialidades.append(especialidade)
        
        db.session.commit()
        
        flash(f'Médico {nome} criado com sucesso! Email: {email} | Senha: {senha}', 'success')
        return redirect(url_for('admin.medicos'))
    
    from models import Especialidade
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    return render_template('admin/form_medico.html', especialidades=especialidades)

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

@bp.route('/agendamentos/<int:id>/confirmar', methods=['POST'])
@login_required
@admin_required
def confirmar_agendamento(id):
    """Confirmar agendamento"""
    from models import Agendamento
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = 'confirmado'
    agendamento.confirmado_em = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Agendamento confirmado com sucesso!'})

@bp.route('/agendamentos/<int:id>/cancelar', methods=['POST'])
@login_required
@admin_required
def cancelar_agendamento(id):
    """Cancelar agendamento"""
    from models import Agendamento
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = 'cancelado'
    motivo = request.json.get('motivo', '') if request.is_json else request.form.get('motivo', '')
    if motivo:
        agendamento.observacoes = f"{agendamento.observacoes or ''}\nCancelado: {motivo}".strip()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Agendamento cancelado com sucesso!'})

@bp.route('/agendamentos/<int:id>/concluir', methods=['POST'])
@login_required
@admin_required
def concluir_agendamento(id):
    """Concluir agendamento"""
    from models import Agendamento
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = 'concluido'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Agendamento concluído com sucesso!'})

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

@bp.route('/agenda/api/eventos')
@login_required
@admin_required
def api_agenda_eventos():
    """API para fornecer eventos da agenda em formato JSON para o calendário"""
    from models import Medico, Agenda, Agendamento, User
    
    start = request.args.get('start')
    end = request.args.get('end')
    medico_id = request.args.get('medico_id')
    
    if not start or not end:
        return jsonify([])
    
    try:
        data_inicio = datetime.fromisoformat(start.replace('Z', '+00:00')).date()
        data_fim = datetime.fromisoformat(end.replace('Z', '+00:00')).date()
    except (ValueError, AttributeError):
        return jsonify([])
    
    query = Agenda.query.filter(
        Agenda.data >= data_inicio,
        Agenda.data <= data_fim,
        Agenda.ativo == True
    )
    
    if medico_id:
        query = query.filter(Agenda.medico_id == int(medico_id))
    
    agendas = query.order_by(Agenda.data, Agenda.hora_inicio).all()
    
    eventos = []
    for agenda in agendas:
        agendamento = Agendamento.query.filter_by(
            agenda_id=agenda.id,
            status='confirmado'
        ).first()
        
        disponivel = agendamento is None
        
        data_hora_inicio = datetime.combine(agenda.data, agenda.hora_inicio)
        data_hora_fim = datetime.combine(agenda.data, agenda.hora_fim)
        
        duracao = (agenda.hora_fim.hour * 60 + agenda.hora_fim.minute) - (agenda.hora_inicio.hour * 60 + agenda.hora_inicio.minute)
        
        medico_nome = f"Dr(a). {agenda.medico.usuario.nome}"
        
        evento = {
            'id': f'agenda_{agenda.id}',
            'title': f"{medico_nome} - {'Disponível' if disponivel else 'Ocupado'}",
            'start': data_hora_inicio.isoformat(),
            'end': data_hora_fim.isoformat(),
            'backgroundColor': '#10b981' if disponivel else '#ef4444',
            'borderColor': '#10b981' if disponivel else '#ef4444',
            'textColor': '#ffffff',
            'extendedProps': {
                'agenda_id': agenda.id,
                'medico_id': agenda.medico_id,
                'medico_nome': medico_nome,
                'disponivel': disponivel,
                'duracao': duracao,
                'paciente_nome': agendamento.paciente.nome if agendamento and agendamento.paciente else None
            }
        }
        
        eventos.append(evento)
    
    return jsonify(eventos)

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

@bp.route('/medicos/<int:id>/resetar-senha', methods=['POST'])
@login_required
@admin_required
def resetar_senha_medico(id):
    """Resetar senha de um médico"""
    from models import Medico, User
    medico = Medico.query.get_or_404(id)
    
    nova_senha = request.form.get('nova_senha', '').strip()
    if not nova_senha:
        nova_senha = 'medico123'
    
    medico.usuario.set_password(nova_senha)
    db.session.commit()
    
    flash(f'Senha de {medico.usuario.nome} resetada para: {nova_senha}', 'success')
    return redirect(url_for('admin.medicos'))

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

@bp.route('/corrigir-timezone-agendamentos', methods=['GET'])
@login_required
@admin_required
def corrigir_timezone_agendamentos_preview():
    """
    Rota administrativa para VISUALIZAR as correções de timezone (GET).
    Mostra preview dos agendamentos que serão corrigidos.
    """
    from models import Agendamento
    
    cutoff_date_str = request.args.get('cutoff_date')
    
    # Validar cutoff_date
    if not cutoff_date_str:
        flash('ERRO: cutoff_date é obrigatória! Use ?cutoff_date=YYYY-MM-DD-HH-MM-SS', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d-%H-%M-%S")
    except ValueError:
        flash('ERRO: Formato de data inválido. Use YYYY-MM-DD-HH-MM-SS (exemplo: 2025-10-21-22-30-00)', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Buscar agendamentos criados via API ou chatbot ANTES da data de corte
    # que ainda não foram corrigidos
    agendamentos = Agendamento.query.filter(
        Agendamento.origem.in_(['mobile', 'chatbot']),
        Agendamento.created_at < cutoff_date,
        ~Agendamento.observacoes.contains('[TIMEZONE_CORRIGIDO]')
    ).all()
    
    if not agendamentos:
        flash('Nenhum agendamento para corrigir!', 'info')
        return redirect(url_for('admin.dashboard'))
    
    # Modo preview (GET): apenas mostra o que seria alterado
    resultado = []
    for agendamento in agendamentos:
        inicio_atual = agendamento.inicio
        fim_atual = agendamento.fim
        
        # Adicionar 3 horas (converter de Brasília UTC-3 para UTC)
        inicio_corrigido = inicio_atual + timedelta(hours=3)
        fim_corrigido = fim_atual + timedelta(hours=3)
        
        resultado.append({
            'id': agendamento.id,
            'paciente': agendamento.paciente.nome if agendamento.paciente else 'N/A',
            'inicio_atual': inicio_atual.strftime('%d/%m/%Y %H:%M'),
            'inicio_corrigido': inicio_corrigido.strftime('%d/%m/%Y %H:%M'),
            'fim_atual': fim_atual.strftime('%d/%m/%Y %H:%M'),
            'fim_corrigido': fim_corrigido.strftime('%d/%m/%Y %H:%M'),
            'origem': agendamento.origem,
            'criado_em': agendamento.created_at.strftime('%d/%m/%Y %H:%M:%S') if agendamento.created_at else 'N/A'
        })
    
    return render_template('admin/correcao_timezone.html',
                         modo='preview',
                         agendamentos=resultado,
                         total=len(resultado),
                         cutoff_date=cutoff_date,
                         cutoff_date_str=cutoff_date_str)

@bp.route('/corrigir-timezone-agendamentos/aplicar', methods=['POST'])
@login_required
@admin_required
def corrigir_timezone_agendamentos_aplicar():
    """
    Rota administrativa para APLICAR as correções de timezone (POST com CSRF).
    Converte agendamentos de Brasília (UTC-3) para UTC.
    """
    from models import Agendamento
    
    cutoff_date_str = request.form.get('cutoff_date')
    
    # Validar cutoff_date
    if not cutoff_date_str:
        flash('ERRO: cutoff_date é obrigatória!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d-%H-%M-%S")
    except ValueError:
        flash('ERRO: Formato de data inválido.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Buscar agendamentos criados via API ou chatbot ANTES da data de corte
    # que ainda não foram corrigidos
    agendamentos = Agendamento.query.filter(
        Agendamento.origem.in_(['mobile', 'chatbot']),
        Agendamento.created_at < cutoff_date,
        ~Agendamento.observacoes.contains('[TIMEZONE_CORRIGIDO]')
    ).all()
    
    if not agendamentos:
        flash('Nenhum agendamento para corrigir!', 'info')
        return redirect(url_for('admin.dashboard'))
    
    # Modo aplicar (POST): faz as correções
    corrigidos = 0
    erros = []
    
    for agendamento in agendamentos:
        try:
            # Verificar novamente se já não foi corrigido (proteção dupla)
            if agendamento.observacoes and '[TIMEZONE_CORRIGIDO]' in agendamento.observacoes:
                continue
            
            # Verificar se foi criado antes da data de corte
            if agendamento.created_at and agendamento.created_at >= cutoff_date:
                continue
            
            # Adicionar 3 horas (converter de Brasília UTC-3 para UTC)
            agendamento.inicio = agendamento.inicio + timedelta(hours=3)
            agendamento.fim = agendamento.fim + timedelta(hours=3)
            
            # Marcar como corrigido
            obs_atual = agendamento.observacoes or ''
            agendamento.observacoes = f"{obs_atual}\n[TIMEZONE_CORRIGIDO em {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC]".strip()
            
            corrigidos += 1
        except Exception as e:
            erros.append(f"Agendamento ID {agendamento.id}: {str(e)}")
    
    # Commit apenas se não houver erros
    if not erros:
        db.session.commit()
        flash(f'✅ Sucesso! {corrigidos} agendamentos foram corrigidos.', 'success')
    else:
        db.session.rollback()
        flash(f'❌ Erro ao corrigir agendamentos: {"; ".join(erros)}', 'error')
    
    return redirect(url_for('admin.dashboard'))