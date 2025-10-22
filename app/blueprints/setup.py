"""
Blueprint para popular o banco de dados via URL
Acesse: /setup-database para executar
"""
from flask import Blueprint, jsonify
from extensions import db
from models import User, Especialidade, Medico, Agenda
from datetime import datetime, timedelta, time

bp = Blueprint('setup', __name__)

@bp.route('/verificar-usuarios')
def verificar_usuarios():
    """
    Rota para verificar se os usuários existem e testar senhas
    Acesse: https://seu-app.railway.app/verificar-usuarios
    """
    from models import User
    
    resultado = {
        'status': 'verificacao',
        'usuarios_verificados': []
    }
    
    # Usuários para verificar
    usuarios_teste = [
        {'email': 'ana.silva@email.com', 'senha': 'paciente123', 'nome_esperado': 'Ana Silva'},
        {'email': 'raimundo.nunes@clinicadrraimundonunes.com.br', 'senha': 'medico123', 'nome_esperado': 'Dr. Raimundo'},
        {'email': 'admin@clinicadrraimundonunes.com.br', 'senha': 'admin123', 'nome_esperado': 'Admin'}
    ]
    
    for teste in usuarios_teste:
        user = User.query.filter_by(email=teste['email']).first()
        
        info = {
            'email': teste['email'],
            'existe': bool(user),
            'ativo': user.ativo if user else None,
            'nome': user.nome if user else None,
            'role': user.role if user else None,
            'senha_hash_length': len(user.senha_hash) if user and user.senha_hash else 0,
            'senha_correta': user.check_password(teste['senha']) if user else False
        }
        
        resultado['usuarios_verificados'].append(info)
    
    # Total de usuários no banco
    resultado['total_usuarios'] = User.query.count()
    resultado['todos_usuarios'] = [{'email': u.email, 'nome': u.nome, 'role': u.role, 'ativo': u.ativo} 
                                     for u in User.query.all()]
    
    return jsonify(resultado), 200

@bp.route('/reset-senhas')
def reset_senhas():
    """
    Rota para forçar o reset de todas as senhas
    Acesse: https://seu-app.railway.app/reset-senhas
    """
    from models import User
    
    resultado = {
        'status': 'resetando',
        'mensagens': [],
        'usuarios_resetados': []
    }
    
    try:
        # Resetar senha da Ana Silva
        ana = User.query.filter_by(email='ana.silva@email.com').first()
        if ana:
            ana.set_password('paciente123')
            ana.ativo = True
            db.session.add(ana)
            resultado['mensagens'].append(f'✅ Senha de Ana Silva resetada')
            resultado['usuarios_resetados'].append({'email': ana.email, 'senha': 'paciente123'})
        else:
            # Criar Ana Silva se não existir
            ana = User()
            ana.nome = "Ana Silva Santos"
            ana.email = "ana.silva@email.com"
            ana.telefone = "(11) 99876-5432"
            ana.role = "paciente"
            ana.ativo = True
            ana.set_password("paciente123")
            db.session.add(ana)
            resultado['mensagens'].append(f'✅ Ana Silva criada')
            resultado['usuarios_resetados'].append({'email': ana.email, 'senha': 'paciente123'})
        
        # Resetar senha do Dr. Raimundo
        raimundo = User.query.filter_by(email='raimundo.nunes@clinicadrraimundonunes.com.br').first()
        if raimundo:
            raimundo.set_password('medico123')
            raimundo.ativo = True
            db.session.add(raimundo)
            resultado['mensagens'].append(f'✅ Senha de Dr. Raimundo Nunes resetada')
            resultado['usuarios_resetados'].append({'email': raimundo.email, 'senha': 'medico123'})
        else:
            resultado['mensagens'].append(f'❌ Dr. Raimundo Nunes não encontrado - execute /setup-database primeiro')
        
        # Resetar senha do Admin
        admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
        if admin:
            admin.set_password('admin123')
            admin.ativo = True
            db.session.add(admin)
            resultado['mensagens'].append(f'✅ Senha de Admin resetada')
            resultado['usuarios_resetados'].append({'email': admin.email, 'senha': 'admin123'})
        
        db.session.commit()
        resultado['status'] = 'sucesso'
        resultado['mensagens'].append('🎉 Todas as senhas foram resetadas!')
        
        return jsonify(resultado), 200
        
    except Exception as e:
        resultado['status'] = 'erro'
        resultado['mensagens'].append(f'❌ ERRO: {str(e)}')
        import traceback
        resultado['mensagens'].append(traceback.format_exc())
        return jsonify(resultado), 500

@bp.route('/testar-login/<email>/<senha>')
def testar_login(email, senha):
    """
    Rota para testar login de qualquer usuário
    Exemplo: https://seu-app.railway.app/testar-login/raimundo.nunes@clinicadrraimundonunes.com.br/medico123
    """
    from models import User
    import sys
    
    resultado = {
        'email_testado': email,
        'senha_testada': senha,
        'detalhes': {}
    }
    
    # Buscar usuário
    user = User.query.filter_by(email=email).first()
    
    if not user:
        resultado['status'] = 'usuario_nao_encontrado'
        resultado['detalhes']['existe'] = False
        return jsonify(resultado), 404
    
    # Detalhes do usuário
    resultado['detalhes']['existe'] = True
    resultado['detalhes']['nome'] = user.nome
    resultado['detalhes']['role'] = user.role
    resultado['detalhes']['ativo'] = user.ativo
    resultado['detalhes']['tem_senha_hash'] = bool(user.senha_hash)
    resultado['detalhes']['tamanho_hash'] = len(user.senha_hash) if user.senha_hash else 0
    
    # Testar senha
    try:
        senha_correta = user.check_password(senha)
        resultado['detalhes']['senha_correta'] = senha_correta
        resultado['detalhes']['erro_verificacao'] = None
        
        if senha_correta:
            resultado['status'] = 'login_ok'
            resultado['mensagem'] = '✅ Login funcionaria!'
        else:
            resultado['status'] = 'senha_incorreta'
            resultado['mensagem'] = '❌ Senha incorreta'
            
            # Tentar resetar a senha
            user.set_password(senha)
            db.session.commit()
            resultado['mensagem'] += ' - Senha resetada! Tente novamente.'
            
    except Exception as e:
        resultado['status'] = 'erro_verificacao'
        resultado['detalhes']['erro_verificacao'] = str(e)
        resultado['mensagem'] = f'❌ Erro ao verificar senha: {str(e)}'
    
    return jsonify(resultado), 200

@bp.route('/setup-database')
def setup_database():
    """
    Rota para popular o banco de dados
    Acesse: https://seu-app.railway.app/setup-database
    """
    
    resultado = {
        'status': 'iniciando',
        'mensagens': [],
        'dados_criados': {}
    }
    
    try:
        # 1. Criar tabelas
        resultado['mensagens'].append('📦 Criando tabelas...')
        db.create_all()
        resultado['mensagens'].append('✅ Tabelas criadas!')
        
        # 2. Verificar e criar admin
        resultado['mensagens'].append('👤 Verificando administrador...')
        admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
        
        if admin:
            resultado['mensagens'].append(f'✅ Admin já existe: {admin.email}')
            if not admin.check_password("admin123"):
                admin.set_password("admin123")
                admin.ativo = True
                db.session.commit()
                resultado['mensagens'].append('✅ Senha do admin resetada para: admin123')
        else:
            admin = User()
            admin.nome = "Administrador"
            admin.email = "admin@clinicadrraimundonunes.com.br"
            admin.telefone = "(11) 99999-9999"
            admin.role = "admin"
            admin.ativo = True
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            resultado['mensagens'].append('✅ Admin criado!')
        
        # 3. Verificar se já tem especialidades
        total_esp = Especialidade.query.count()
        if total_esp > 0:
            resultado['mensagens'].append(f'✅ Banco já tem {total_esp} especialidades')
            resultado['mensagens'].append(f'✅ Banco já tem {Medico.query.count()} médicos')
            resultado['dados_criados'] = {
                'especialidades': total_esp,
                'medicos': Medico.query.count(),
                'agenda': Agenda.query.count(),
                'usuarios': User.query.count()
            }
            resultado['status'] = 'ja_populado'
            return jsonify(resultado), 200
        
        # 4. Criar especialidades
        resultado['mensagens'].append('📋 Criando especialidades...')
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
            db.session.add(esp)
            especialidades.append(esp)
        db.session.commit()
        resultado['mensagens'].append(f'✅ {len(especialidades)} especialidades criadas!')
        
        # 5. Criar médicos
        resultado['mensagens'].append('👨‍⚕️ Criando médicos...')
        medicos_data = [
            {
                'nome': 'Dr. Raimundo Nunes',
                'email': 'raimundo.nunes@clinicadrraimundonunes.com.br',
                'telefone': '(11) 98765-4321',
                'crm': 'CRM/SP 12345',
                'bio': 'Mais de 30 anos de experiência em ginecologia e obstetrícia. Especialista em pré-natal de alto risco e cirurgia ginecológica.',
                'foto_url': '/static/images/dr-carlos-oliveira.jpg',
                'especialidades': ['DIU e Implanon', 'Pré-Natal de Alto Risco', 'Hipertensão e Diabetes Gestacional']
            },
            {
                'nome': 'Dra. Ana Carolina Silva',
                'email': 'ana@clinicadrraimundonunes.com.br', 
                'telefone': '(11) 98765-4322',
                'crm': 'CRM/SP 67890',
                'bio': 'Ginecologista e obstetra. Especialização em laparoscopia e endometriose. Atendimento humanizado.',
                'foto_url': '/static/images/dra-ana-silva.jpg',
                'especialidades': ['Mastologia', 'Uroginecologia', 'Sexualidade']
            },
            {
                'nome': 'Dr. Ricardo Mendes',
                'email': 'ricardo@clinicadrraimundonunes.com.br',
                'telefone': '(11) 98765-4323', 
                'crm': 'CRM/SP 54321',
                'bio': 'Especialista em reprodução humana e climatério. Formação em medicina reprodutiva.',
                'foto_url': '/static/images/dr-ricardo-mendes.jpg',
                'especialidades': ['Climatério e Menopausa', 'Reprodução Humana', 'PTGI']
            },
            {
                'nome': 'Dra. Maria Santos',
                'email': 'maria@clinicadrraimundonunes.com.br',
                'telefone': '(11) 98765-4324',
                'crm': 'CRM/SP 98765',
                'bio': 'Especialista em ginecologia preventiva e mastologia. Experiência em rastreamento de câncer.',
                'foto_url': '/static/images/dra-maria-santos.jpg',
                'especialidades': ['Mastologia', 'DIU e Implanon']
            },
            {
                'nome': 'Dra. Patrícia Lima',
                'email': 'patricia@clinicadrraimundonunes.com.br',
                'telefone': '(11) 98765-4325',
                'crm': 'CRM/SP 11111',
                'bio': 'Ginecologista com especialização em uroginecologia. Experiência em cirurgias minimamente invasivas.',
                'foto_url': '/static/images/dra-patricia-lima.jpg',
                'especialidades': ['Uroginecologia', 'Pré-Natal de Alto Risco']
            }
        ]
        
        medicos = []
        for med_data in medicos_data:
            # Criar usuário médico
            user = User()
            user.nome = med_data['nome']
            user.email = med_data['email']
            user.telefone = med_data['telefone']
            user.role = "medico"
            user.ativo = True
            user.set_password("medico123")
            db.session.add(user)
            db.session.commit()
            
            # Criar médico
            medico = Medico()
            medico.user_id = user.id
            medico.crm = med_data['crm']
            medico.bio = med_data['bio']
            medico.foto_url = med_data.get('foto_url')
            medico.ativo = True
            db.session.add(medico)
            db.session.flush()
            
            # Associar especialidades
            for esp_nome in med_data['especialidades']:
                especialidade = next((e for e in especialidades if e.nome == esp_nome), None)
                if especialidade:
                    medico.especialidades.append(especialidade)
            
            medicos.append(medico)
        
        db.session.commit()
        resultado['mensagens'].append(f'✅ {len(medicos)} médicos criados!')
        
        # 6. Criar agenda
        resultado['mensagens'].append('📅 Criando agenda dos médicos...')
        hoje = datetime.now().date()
        agenda_count = 0
        
        for medico in medicos:
            for dia_offset in range(60):  # Próximos 60 dias
                data = hoje + timedelta(days=dia_offset)
                # Pular fins de semana
                if data.weekday() >= 5:
                    continue
                
                # Criar slots de 1 hora das 8h às 20h (8h, 9h, ..., 19h)
                for hora in range(8, 20):
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
        resultado['mensagens'].append(f'✅ {agenda_count} slots de agenda criados!')
        resultado['mensagens'].append('   • Horário: 08:00 às 20:00 (Segunda a Sexta)')
        
        # 7. Criar paciente Ana Silva
        resultado['mensagens'].append('👥 Criando paciente Ana Silva...')
        paciente_ana = User.query.filter_by(email='ana.silva@email.com').first()
        
        if paciente_ana:
            resultado['mensagens'].append(f'✅ Paciente Ana Silva já existe: {paciente_ana.email}')
            if not paciente_ana.check_password("paciente123"):
                paciente_ana.set_password("paciente123")
                paciente_ana.ativo = True
                db.session.commit()
                resultado['mensagens'].append('✅ Senha da paciente Ana Silva resetada para: paciente123')
        else:
            paciente_ana = User()
            paciente_ana.nome = "Ana Silva Santos"
            paciente_ana.email = "ana.silva@email.com"
            paciente_ana.telefone = "(11) 99876-5432"
            paciente_ana.role = "paciente"
            paciente_ana.ativo = True
            paciente_ana.set_password("paciente123")
            db.session.add(paciente_ana)
            db.session.commit()
            resultado['mensagens'].append('✅ Paciente Ana Silva criada!')
        
        # 8. Resumo final
        resultado['status'] = 'sucesso'
        resultado['dados_criados'] = {
            'especialidades': Especialidade.query.count(),
            'medicos': Medico.query.count(),
            'agenda': Agenda.query.count(),
            'usuarios': User.query.count()
        }
        resultado['mensagens'].append('🎉 BANCO POPULADO COM SUCESSO!')
        resultado['mensagens'].append('')
        resultado['mensagens'].append('🔑 CREDENCIAIS DE LOGIN:')
        resultado['mensagens'].append('👨‍💼 ADMIN:')
        resultado['mensagens'].append('   Email: admin@clinicadrraimundonunes.com.br')
        resultado['mensagens'].append('   Senha: admin123')
        resultado['mensagens'].append('')
        resultado['mensagens'].append('👨‍⚕️ DR. RAIMUNDO NUNES (Médico):')
        resultado['mensagens'].append('   Email: raimundo.nunes@clinicadrraimundonunes.com.br')
        resultado['mensagens'].append('   Senha: medico123')
        resultado['mensagens'].append('')
        resultado['mensagens'].append('👥 ANA SILVA (Paciente):')
        resultado['mensagens'].append('   Email: ana.silva@email.com')
        resultado['mensagens'].append('   Senha: paciente123')
        resultado['mensagens'].append('')
        resultado['mensagens'].append('ℹ️ Todos os outros médicos também usam a senha: medico123')
        
        return jsonify(resultado), 200
        
    except Exception as e:
        resultado['status'] = 'erro'
        resultado['mensagens'].append(f'❌ ERRO: {str(e)}')
        import traceback
        resultado['mensagens'].append(traceback.format_exc())
        return jsonify(resultado), 500

@bp.route('/popular-horarios')
def popular_horarios():
    """
    Cria horários das 08:00 às 20:00 para todos os médicos (Segunda a Sexta)
    Acesse: /popular-horarios
    """
    from models import Medico, Agenda
    
    resultado = {
        'status': 'criando',
        'mensagens': [],
        'horarios_criados': 0
    }
    
    try:
        # Buscar todos os médicos
        medicos = Medico.query.filter_by(ativo=True).all()
        if not medicos:
            resultado['status'] = 'erro'
            resultado['mensagens'].append('❌ Nenhum médico encontrado. Execute /setup-database primeiro')
            return jsonify(resultado), 404
        
        # Limpar agendas antigas (opcional - comentar se quiser manter as existentes)
        # Agenda.query.delete()
        # db.session.commit()
        # resultado['mensagens'].append('🗑️ Agendas antigas removidas')
        
        resultado['mensagens'].append(f'📅 Criando horários para {len(medicos)} médicos...')
        
        # Criar horários para os próximos 60 dias
        hoje = datetime.now().date()
        horarios_criados = 0
        
        for medico in medicos:
            for dia_offset in range(60):  # Próximos 60 dias
                data = hoje + timedelta(days=dia_offset)
                
                # Apenas Segunda a Sexta (0 = Segunda, 4 = Sexta)
                if data.weekday() >= 5:
                    continue
                
                # Criar slots de 1 hora das 8h às 20h
                for hora in range(8, 20):  # 8h, 9h, 10h, ..., 19h
                    # Verificar se já existe
                    existe = Agenda.query.filter_by(
                        medico_id=medico.id,
                        data=data,
                        hora_inicio=time(hora, 0)
                    ).first()
                    
                    if not existe:
                        agenda = Agenda()
                        agenda.medico_id = medico.id
                        agenda.data = data
                        agenda.hora_inicio = time(hora, 0)
                        agenda.hora_fim = time(hora + 1, 0)
                        agenda.duracao_minutos = 60
                        agenda.tipo = 'presencial'
                        agenda.ativo = True
                        db.session.add(agenda)
                        horarios_criados += 1
        
        db.session.commit()
        
        resultado['status'] = 'sucesso'
        resultado['horarios_criados'] = horarios_criados
        resultado['mensagens'].append(f'✅ {horarios_criados} horários criados com sucesso!')
        resultado['mensagens'].append(f'📊 Total de horários no banco: {Agenda.query.count()}')
        resultado['mensagens'].append('')
        resultado['mensagens'].append('ℹ️ Horários criados:')
        resultado['mensagens'].append('   • Período: Segunda a Sexta')
        resultado['mensagens'].append('   • Horário: 08:00 às 20:00 (slots de 1 hora)')
        resultado['mensagens'].append('   • Próximos 60 dias')
        
        return jsonify(resultado), 200
        
    except Exception as e:
        db.session.rollback()
        resultado['status'] = 'erro'
        resultado['mensagens'].append(f'❌ ERRO: {str(e)}')
        import traceback
        resultado['traceback'] = traceback.format_exc()
        return jsonify(resultado), 500

@bp.route('/criar-agendamentos-teste')
def criar_agendamentos_teste():
    """
    Cria agendamentos de teste para visualizar no painel médico
    Acesse: /criar-agendamentos-teste
    """
    from models import User, Medico, Agendamento, Especialidade
    import random
    
    resultado = {
        'status': 'criando',
        'mensagens': [],
        'agendamentos_criados': []
    }
    
    try:
        # Buscar paciente Ana Silva
        ana = User.query.filter_by(email='ana.silva@email.com').first()
        if not ana:
            resultado['status'] = 'erro'
            resultado['mensagens'].append('❌ Paciente Ana Silva não encontrada. Execute /reset-senhas primeiro')
            return jsonify(resultado), 404
        
        # Buscar todos os médicos
        medicos = Medico.query.filter_by(ativo=True).all()
        if not medicos:
            resultado['status'] = 'erro'
            resultado['mensagens'].append('❌ Nenhum médico encontrado. Execute /setup-database primeiro')
            return jsonify(resultado), 404
        
        # Buscar todas as especialidades
        especialidades = Especialidade.query.filter_by(ativo=True).all()
        if not especialidades:
            resultado['status'] = 'erro'
            resultado['mensagens'].append('❌ Nenhuma especialidade encontrada. Execute /setup-database primeiro')
            return jsonify(resultado), 404
        
        # Criar 5 agendamentos nos próximos 7 dias
        agendamentos_criados = 0
        hoje = datetime.now()
        
        for i in range(5):
            # Escolher médico aleatório
            medico = random.choice(medicos)
            
            # Escolher especialidade aleatória do médico
            if medico.especialidades:
                especialidade = random.choice(list(medico.especialidades))
            else:
                especialidade = random.choice(especialidades)
            
            # Criar horário aleatório nos próximos 7 dias
            dias_futuro = random.randint(1, 7)
            hora = random.choice([8, 9, 10, 11, 14, 15, 16])
            
            inicio = hoje + timedelta(days=dias_futuro)
            inicio = inicio.replace(hour=hora, minute=0, second=0, microsecond=0)
            fim = inicio + timedelta(minutes=30)
            
            # Verificar se já existe agendamento para este horário
            existe = Agendamento.query.filter_by(
                medico_id=medico.id,
                inicio=inicio
            ).first()
            
            if not existe:
                agendamento = Agendamento()
                agendamento.paciente_id = ana.id
                agendamento.medico_id = medico.id
                agendamento.especialidade_id = especialidade.id
                agendamento.inicio = inicio
                agendamento.fim = fim
                agendamento.status = random.choice(['agendado', 'confirmado'])
                agendamento.observacoes = f'Consulta de teste #{i+1}'
                
                db.session.add(agendamento)
                agendamentos_criados += 1
                
                user_medico = User.query.get(medico.user_id)
                resultado['agendamentos_criados'].append({
                    'medico': user_medico.nome if user_medico else 'N/A',
                    'especialidade': especialidade.nome,
                    'data_hora': inicio.strftime('%d/%m/%Y %H:%M'),
                    'status': agendamento.status
                })
        
        db.session.commit()
        
        resultado['status'] = 'sucesso'
        resultado['mensagens'].append(f'✅ {agendamentos_criados} agendamentos de teste criados!')
        resultado['total_agendamentos_banco'] = Agendamento.query.count()
        
        return jsonify(resultado), 200
        
    except Exception as e:
        db.session.rollback()
        resultado['status'] = 'erro'
        resultado['mensagens'].append(f'❌ ERRO: {str(e)}')
        import traceback
        resultado['traceback'] = traceback.format_exc()
        return jsonify(resultado), 500
