#!/usr/bin/env python3
"""
Script de migration automático para Railway/Produção
Cria TODAS as tabelas e popula com dados iniciais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from extensions import db
from models import User, Especialidade, Medico, Agenda, Agendamento
from datetime import datetime, timedelta, time

def run_migrations():
    """Executa migrations e popula dados automaticamente"""
    
    app = create_app()
    
    print("🚀 SISTEMA DE MIGRATION AUTOMÁTICO - RAILWAY")
    print("=" * 60)
    
    with app.app_context():
        # 1. Criar todas as tabelas
        print("\n📦 Criando/atualizando tabelas no banco...")
        try:
            db.create_all()
            print("✅ Tabelas criadas/atualizadas com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            return False
        
        # 2. Garantir que admin existe
        admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
        if admin:
            print(f"✅ Admin existe: {admin.email}")
            if not admin.check_password("admin123"):
                admin.set_password("admin123")
                admin.ativo = True
                db.session.commit()
                print("   ✅ Senha resetada!")
        else:
            print("⚠️  Admin não encontrado, criando...")
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
        
        # 3. Verificar se já tem especialidades
        total_esp = Especialidade.query.count()
        if total_esp > 0:
            print(f"\n✅ Banco já tem especialidades ({total_esp})")
            print(f"✅ Banco já tem médicos ({Medico.query.count()})")
            print("\n✨ Migration completa!")
            print("=" * 60)
            return True
        
        print("\n📝 Banco vazio - Populando com dados iniciais...")
        
        # 3. Criar especialidades
        print("\n📋 Criando especialidades...")
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
        print(f"✅ {len(especialidades)} especialidades criadas")
        
        # 4. Criar admin
        print("\n👤 Criando administrador...")
        admin = User()
        admin.nome = "Administrador"
        admin.email = "admin@clinicadrraimundonunes.com.br"
        admin.telefone = "(11) 99999-9999"
        admin.role = "admin"
        admin.ativo = True
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin criado - Email: {admin.email} | Senha: admin123")
        
        # 5. Criar médicos
        print("\n👨‍⚕️ Criando médicos...")
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
        print(f"✅ {len(medicos)} médicos criados - Senha padrão: medico123")
        
        # 6. Criar agenda (próximos 30 dias)
        print("\n📅 Criando agenda dos médicos...")
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
        print(f"✅ {agenda_count} slots de agenda criados")
        
        # 7. Resumo final
        print("\n" + "=" * 60)
        print("✅ BANCO POPULADO COM SUCESSO!")
        print("=" * 60)
        print(f"\n📊 DADOS CRIADOS:")
        print(f"   • Especialidades: {Especialidade.query.count()}")
        print(f"   • Médicos: {Medico.query.count()}")
        print(f"   • Agenda: {Agenda.query.count()} slots")
        print(f"   • Admin: 1")
        
        print(f"\n🔑 CREDENCIAIS DE LOGIN:")
        print(f"   Email: admin@clinicadrraimundonunes.com.br")
        print(f"   Senha: admin123")
        
        print("\n✨ Migration completa!")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
