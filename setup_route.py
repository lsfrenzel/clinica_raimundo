"""
ENDPOINT TEMPORÁRIO DE SETUP - DELETE APÓS USAR!

Acesse https://seu-app.railway.app/setup para popular o banco de dados automaticamente.

IMPORTANTE: Delete este arquivo após usar por segurança!
"""

from flask import Blueprint, jsonify
from extensions import db
from models import User, Especialidade, Medico, Agenda
from datetime import datetime, timedelta, time

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/setup')
def setup_database():
    """Popular banco de dados - USE APENAS UMA VEZ E DELETE ESTE ARQUIVO!"""
    
    try:
        # Verificar se já existe admin
        admin_exists = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
        if admin_exists:
            return jsonify({
                'status': 'error',
                'message': 'Banco já foi populado! Admin já existe.',
                'admin_email': 'admin@clinicadrraimundonunes.com.br',
                'admin_senha': 'admin123'
            }), 400
        
        # 1. Criar especialidades
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
        
        # 2. Criar usuário admin
        admin = User()
        admin.nome = "Administrador"
        admin.email = "admin@clinicadrraimundonunes.com.br"
        admin.telefone = "(11) 99999-9999"
        admin.role = "admin"
        admin.ativo = True
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        
        # 3. Criar médicos
        medicos_data = [
            {'nome': 'Dr. Raimundo Nunes', 'crm': 'CRM/SP 123456', 'especialidade': 'Pré-Natal de Alto Risco'},
            {'nome': 'Dra. Ana Silva', 'crm': 'CRM/SP 234567', 'especialidade': 'Mastologia'},
            {'nome': 'Dr. Carlos Oliveira', 'crm': 'CRM/SP 345678', 'especialidade': 'Reprodução Humana'},
            {'nome': 'Dra. Maria Santos', 'crm': 'CRM/SP 456789', 'especialidade': 'Uroginecologia'},
            {'nome': 'Dr. Ricardo Mendes', 'crm': 'CRM/SP 567890', 'especialidade': 'Climatério e Menopausa'}
        ]
        
        medicos = []
        for med_data in medicos_data:
            user = User()
            user.nome = med_data['nome']
            user.email = f"{med_data['nome'].lower().replace(' ', '.').replace('dr.', '').replace('dra.', '').strip()}@clinicadrraimundonunes.com.br"
            user.telefone = f"(11) 9{9000 + len(medicos):04d}-{1234 + len(medicos):04d}"
            user.role = "medico"
            user.ativo = True
            user.set_password("medico123")
            db.session.add(user)
            db.session.commit()
            
            medico = Medico()
            medico.user_id = user.id
            medico.crm = med_data['crm']
            medico.bio = f"Especialista em {med_data['especialidade']} com mais de 10 anos de experiência."
            medico.ativo = True
            db.session.add(medico)
            
            # Associar especialidade
            especialidade = next((e for e in especialidades if e.nome == med_data['especialidade']), None)
            if especialidade:
                medico.especialidades.append(especialidade)
            
            medicos.append(medico)
        
        db.session.commit()
        
        # 4. Criar agenda (próximos 30 dias, 8h-17h, segunda a sexta)
        hoje = datetime.now().date()
        agenda_count = 0
        
        for medico in medicos:
            for dia_offset in range(30):
                data = hoje + timedelta(days=dia_offset)
                # Pular fins de semana
                if data.weekday() >= 5:
                    continue
                
                # Criar slots de 1 hora das 8h às 17h
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
            'message': '✅ Banco de dados populado com sucesso!',
            'dados_criados': {
                'especialidades': len(especialidades),
                'medicos': len(medicos),
                'admin': 1,
                'slots_agenda': agenda_count
            },
            'credenciais_admin': {
                'email': 'admin@clinicadrraimundonunes.com.br',
                'senha': 'admin123'
            },
            'proximos_passos': [
                '1. Faça login com as credenciais acima',
                '2. DELETE o arquivo setup_route.py por segurança!',
                '3. Altere a senha do admin após o primeiro login'
            ]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Erro ao popular banco: {str(e)}'
        }), 500
