#!/usr/bin/env python3
"""
Script para popular o banco de dados do Railway
Execute: python popular_railway.py
"""

import sys
import os

# Garantir que DATABASE_URL aponte para o Railway
if not os.environ.get("DATABASE_URL"):
    print("❌ ERROR: DATABASE_URL não configurado!")
    print("Configure a variável de ambiente DATABASE_URL com a URL do PostgreSQL do Railway")
    sys.exit(1)

from main import create_app
from extensions import db
from models import User, Especialidade, Medico, Agenda
from datetime import datetime, timedelta, time

def popular_railway():
    """Popular banco de dados do Railway"""
    
    app = create_app()
    
    print("🚀 POPULANDO BANCO DE DADOS RAILWAY")
    print("=" * 60)
    
    with app.app_context():
        # Verificar conexão
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'railway' in db_url or 'postgres' in db_url:
            print(f"✅ Conectado ao Railway PostgreSQL")
        else:
            print(f"⚠️  Conectado a: {db_url[:50]}...")
        
        # 1. Criar todas as tabelas
        print("\n📦 Criando tabelas...")
        try:
            db.create_all()
            print("✅ Tabelas criadas!")
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            return False
        
        # 2. Verificar se já tem dados
        user_count = User.query.count()
        if user_count > 0:
            print(f"\n⚠️  Banco já tem {user_count} usuários!")
            admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
            if admin:
                print(f"✅ Admin existe: {admin.email}")
                print(f"   Resetando senha para: admin123")
                admin.set_password("admin123")
                admin.ativo = True
                db.session.commit()
                print("✅ Senha resetada!")
                return True
            else:
                print("❌ Admin não encontrado, criando...")
        
        # 3. Criar especialidades
        print("\n📝 Criando especialidades...")
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
            esp = Especialidade.query.filter_by(nome=esp_data['nome']).first()
            if not esp:
                esp = Especialidade(**esp_data)
                db.session.add(esp)
            especialidades.append(esp)
        
        db.session.commit()
        print(f"✅ {len(especialidades)} especialidades criadas!")
        
        # 4. Criar admin
        print("\n👤 Criando administrador...")
        admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
        
        if not admin:
            admin = User()
            admin.nome = "Administrador"
            admin.email = "admin@clinicadrraimundonunes.com.br"
            admin.telefone = "(11) 99999-9999"
            admin.role = "admin"
            admin.ativo = True
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin criado!")
        else:
            print("✅ Admin já existe!")
        
        print(f"   Email: {admin.email}")
        print(f"   Senha: admin123")
        
        # 5. Criar médicos
        print("\n👨‍⚕️ Criando médicos...")
        medicos_data = [
            {
                'nome': 'Dr. Raimundo Nunes', 
                'crm': 'CRM/SP 123456', 
                'especialidade': 'Pré-Natal de Alto Risco',
                'foto_url': '/static/images/professional_male_do_55c38d12.jpg'
            },
            {
                'nome': 'Dra. Ana Silva', 
                'crm': 'CRM/SP 234567', 
                'especialidade': 'Mastologia',
                'foto_url': '/static/images/professional_female__98725e36.jpg'
            },
            {
                'nome': 'Dr. Carlos Oliveira', 
                'crm': 'CRM/SP 345678', 
                'especialidade': 'Reprodução Humana',
                'foto_url': '/static/images/professional_male_do_f99c6925.jpg'
            },
            {
                'nome': 'Dra. Maria Santos', 
                'crm': 'CRM/SP 456789', 
                'especialidade': 'Uroginecologia',
                'foto_url': '/static/images/professional_female__90265671.jpg'
            },
            {
                'nome': 'Dr. Ricardo Mendes', 
                'crm': 'CRM/SP 567890', 
                'especialidade': 'Climatério e Menopausa',
                'foto_url': '/static/images/professional_male_do_57c90351.jpg'
            }
        ]
        
        medicos = []
        for med_data in medicos_data:
            # Criar usuário médico
            email = f"{med_data['nome'].lower().replace(' ', '.').replace('dr.', '').replace('dra.', '').strip()}@clinicadrraimundonunes.com.br"
            user = User.query.filter_by(email=email).first()
            
            if not user:
                user = User()
                user.nome = med_data['nome']
                user.email = email
                user.telefone = f"(11) 9{9000 + len(medicos):04d}-{1234 + len(medicos):04d}"
                user.role = "medico"
                user.ativo = True
                user.set_password("medico123")
                db.session.add(user)
                db.session.commit()
            
            # Criar médico
            medico = Medico.query.filter_by(user_id=user.id).first()
            if not medico:
                medico = Medico()
                medico.user_id = user.id
                medico.crm = med_data['crm']
                medico.bio = f"Especialista em {med_data['especialidade']} com mais de 10 anos de experiência."
                medico.foto_url = med_data.get('foto_url', '')
                medico.ativo = True
                db.session.add(medico)
                
                # Associar especialidade
                especialidade = next((e for e in especialidades if e.nome == med_data['especialidade']), None)
                if especialidade and especialidade not in medico.especialidades:
                    medico.especialidades.append(especialidade)
                
                medicos.append(medico)
        
        db.session.commit()
        print(f"✅ {len(medicos)} médicos criados!")
        
        # 6. Criar agenda
        print("\n📅 Criando agenda...")
        hoje = datetime.now().date()
        agenda_count = 0
        
        for medico in Medico.query.all():
            # Contar agendas existentes
            existing = Agenda.query.filter_by(medico_id=medico.id).count()
            if existing > 0:
                continue
                
            for dia_offset in range(30):
                data = hoje + timedelta(days=dia_offset)
                if data.weekday() >= 5:  # Pular fins de semana
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
        print(f"✅ {agenda_count} slots de agenda criados!")
        
        # 7. Resumo final
        print("\n" + "=" * 60)
        print("✅ BANCO POPULADO COM SUCESSO!")
        print("=" * 60)
        print(f"\n📊 DADOS CRIADOS:")
        print(f"   • Especialidades: {Especialidade.query.count()}")
        print(f"   • Usuários: {User.query.count()}")
        print(f"   • Médicos: {Medico.query.count()}")
        print(f"   • Agenda: {Agenda.query.count()} slots")
        
        print(f"\n🔑 CREDENCIAIS DE LOGIN:")
        print(f"   Email: admin@clinicadrraimundonunes.com.br")
        print(f"   Senha: admin123")
        print(f"\n🌐 Acesse: https://seu-app.railway.app/auth/login")
        
        return True

if __name__ == '__main__':
    try:
        success = popular_railway()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
