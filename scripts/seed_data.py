# Script para popular o banco de dados com dados de exemplo
# Clínica Dr. Raimundo Nunes - Sistema de Gestão

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from extensions import db
from models import User, Especialidade, Medico, Agenda, Agendamento
from datetime import datetime, timedelta, time
import random

def create_seed_data():
    """Cria dados de exemplo para demonstração do sistema"""
    
    app = create_app()
    with app.app_context():
        print("🚀 Iniciando criação de dados de exemplo...")
        
        # Limpar dados existentes (apenas para desenvolvimento)
        db.drop_all()
        db.create_all()
        
        # 1. Criar especialidades baseadas no site
        especialidades_data = [
            {
                'nome': 'DIU e Implanon',
                'descricao': 'Inserção e acompanhamento de DIU hormonal (Mirena, Kyleena) e implantes contraceptivos.',
                'duracao_padrao': 45
            },
            {
                'nome': 'Pré-Natal de Alto Risco', 
                'descricao': 'Acompanhamento especializado de gestações de alto risco com cuidado humanizado.',
                'duracao_padrao': 60
            },
            {
                'nome': 'Hipertensão e Diabetes Gestacional',
                'descricao': 'Tratamento e acompanhamento de complicações metabólicas na gestação.',
                'duracao_padrao': 45
            },
            {
                'nome': 'Mastologia',
                'descricao': 'Prevenção, diagnóstico e tratamento de doenças da mama.',
                'duracao_padrao': 30
            },
            {
                'nome': 'Uroginecologia',
                'descricao': 'Tratamento de incontinência urinária e prolapsos genitais.',
                'duracao_padrao': 45
            },
            {
                'nome': 'Climatério e Menopausa',
                'descricao': 'Acompanhamento e tratamento de sintomas do climatério e menopausa.',
                'duracao_padrao': 30
            },
            {
                'nome': 'PTGI',
                'descricao': 'Programa de Tratamento de Gestações Indesejadas com acompanhamento psicológico.',
                'duracao_padrao': 60
            },
            {
                'nome': 'Sexualidade',
                'descricao': 'Orientação e tratamento de disfunções sexuais femininas.',
                'duracao_padrao': 45
            },
            {
                'nome': 'Reprodução Humana',
                'descricao': 'Investigação e tratamento de infertilidade conjugal.',
                'duracao_padrao': 60
            }
        ]
        
        print("📝 Criando especialidades...")
        especialidades = []
        for esp_data in especialidades_data:
            especialidade = Especialidade()
            especialidade.nome = esp_data['nome']
            especialidade.descricao = esp_data['descricao'] 
            especialidade.duracao_padrao = esp_data['duracao_padrao']
            especialidade.ativo = True
            
            db.session.add(especialidade)
            especialidades.append(especialidade)
        
        db.session.commit()
        print(f"✅ {len(especialidades)} especialidades criadas")
        
        # 2. Criar usuário administrador
        print("👤 Criando usuário administrador...")
        admin_user = User()
        admin_user.nome = "Administrador"
        admin_user.email = "admin@clinicadrraimundonunes.com.br"
        admin_user.telefone = "(11) 99999-9999"
        admin_user.role = "admin"
        admin_user.ativo = True
        admin_user.set_password("admin123")
        
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Administrador criado - Email: admin@clinicadrraimundonunes.com.br | Senha: admin123")
        
        # 3. Criar médicos da equipe
        medicos_data = [
            {
                'nome': 'Dr. Raimundo Nunes',
                'email': 'raimundo.nunes@clinicadrraimundonunes.com.br',
                'telefone': '(11) 98765-4321',
                'crm': 'CRM/SP 12345',
                'bio': 'Mais de 30 anos de experiência em ginecologia e obstetrícia. Especialista em pré-natal de alto risco e cirurgia ginecológica. Reconhecido por sua atuação em casos de alta complexidade.',
                'foto_url': '/static/images/dr-carlos-oliveira.jpg',
                'especialidades': ['DIU e Implanon', 'Pré-Natal de Alto Risco', 'Hipertensão e Diabetes Gestacional']
            },
            {
                'nome': 'Dra. Ana Carolina Silva',
                'email': 'ana@clinicadrraimundonunes.com.br', 
                'telefone': '(11) 98765-4322',
                'crm': 'CRM/SP 67890',
                'bio': 'Ginecologista e obstetra formada pela Febrasgo. Especialização em laparoscopia e endometriose. Atendimento humanizado focado na saúde integral da mulher.',
                'foto_url': '/static/images/dra-ana-costa.jpg',
                'especialidades': ['Mastologia', 'Uroginecologia', 'Sexualidade']
            },
            {
                'nome': 'Dr. Ricardo Mendes',
                'email': 'ricardo@clinicadrraimundonunes.com.br',
                'telefone': '(11) 98765-4323', 
                'crm': 'CRM/SP 54321',
                'bio': 'Médico ginecologista especialista em reprodução humana e climatério. Formação complementar em medicina reprodutiva e endocrinologia ginecológica.',
                'foto_url': '/static/images/dr-pedro-alves.jpg',
                'especialidades': ['Climatério e Menopausa', 'Reprodução Humana', 'PTGI']
            },
            {
                'nome': 'Dra. Maria Santos',
                'email': 'maria@clinicadrraimundonunes.com.br',
                'telefone': '(11) 98765-4324',
                'crm': 'CRM/SP 98765',
                'bio': 'Especialista em ginecologia preventiva e mastologia. Ampla experiência em rastreamento de câncer ginecológico e acompanhamento de pacientes oncológicas.',
                'foto_url': '/static/images/dra-maria-silva.jpg',
                'especialidades': ['Mastologia', 'DIU e Implanon']
            },
            {
                'nome': 'Dra. Patrícia Lima',
                'email': 'patricia@clinicadrraimundonunes.com.br',
                'telefone': '(11) 98765-4325',
                'crm': 'CRM/SP 11111',
                'bio': 'Ginecologista e obstetra com especialização em uroginecologia. Experiência em cirurgias minimamente invasivas para correção de incontinência urinária.',
                'foto_url': '/static/images/dra-julia-santos.jpg',
                'especialidades': ['Uroginecologia', 'Pré-Natal de Alto Risco']
            }
        ]
        
        print("👨‍⚕️ Criando médicos...")
        medicos = []
        for medico_data in medicos_data:
            # Criar usuário médico
            user = User()
            user.nome = medico_data['nome']
            user.email = medico_data['email']
            user.telefone = medico_data['telefone']
            user.role = 'medico'
            user.ativo = True
            user.set_password('medico123')
            
            db.session.add(user)
            db.session.flush()  # Para obter o ID
            
            # Criar perfil do médico
            medico = Medico()
            medico.user_id = user.id
            medico.crm = medico_data['crm']
            medico.bio = medico_data['bio']
            medico.foto_url = medico_data.get('foto_url')
            medico.ativo = True
            
            # Associar especialidades
            for esp_nome in medico_data['especialidades']:
                especialidade = next((e for e in especialidades if e.nome == esp_nome), None)
                if especialidade:
                    medico.especialidades.append(especialidade)
            
            db.session.add(medico)
            medicos.append(medico)
        
        db.session.commit()
        print(f"✅ {len(medicos)} médicos criados - Senha padrão: medico123")
        
        # 4. Criar agenda para os médicos (próximos 30 dias úteis)
        print("📅 Criando agenda dos médicos...")
        total_slots = 0
        
        for medico in medicos:
            # Criar agenda para os próximos 30 dias úteis
            data_atual = datetime.now().date()
            for i in range(45):  # 45 dias para ter mais opções
                data = data_atual + timedelta(days=i)
                
                # Pular fins de semana
                if data.weekday() >= 5:  # 5=sábado, 6=domingo
                    continue
                
                # Horários de atendimento: 8h às 17h
                horarios = [
                    (time(8, 0), time(8, 30)),
                    (time(8, 30), time(9, 0)),
                    (time(9, 0), time(9, 30)),
                    (time(9, 30), time(10, 0)),
                    (time(10, 0), time(10, 30)),
                    (time(10, 30), time(11, 0)),
                    (time(11, 0), time(11, 30)),
                    (time(11, 30), time(12, 0)),
                    (time(14, 0), time(14, 30)),
                    (time(14, 30), time(15, 0)),
                    (time(15, 0), time(15, 30)),
                    (time(15, 30), time(16, 0)),
                    (time(16, 0), time(16, 30)),
                    (time(16, 30), time(17, 0)),
                ]
                
                # Cada médico trabalha em dias alternados para dar mais variedade
                if i % len(medicos) == medicos.index(medico):
                    for hora_inicio, hora_fim in horarios:
                        agenda = Agenda()
                        agenda.medico_id = medico.id
                        agenda.data = data
                        agenda.hora_inicio = hora_inicio
                        agenda.hora_fim = hora_fim
                        agenda.duracao_minutos = 30
                        agenda.tipo = 'presencial'
                        agenda.ativo = True
                        
                        db.session.add(agenda)
                        total_slots += 1
        
        db.session.commit()
        print(f"✅ {total_slots} slots de agenda criados")
        
        # 5. Criar alguns pacientes de exemplo
        print("👥 Criando pacientes de exemplo...")
        pacientes_data = [
            {'nome': 'Ana Silva Santos', 'email': 'ana.silva@email.com', 'telefone': '(11) 99876-5432'},
            {'nome': 'Maria José Oliveira', 'email': 'maria.jose@email.com', 'telefone': '(11) 99876-5433'},
            {'nome': 'Carla Fernanda Lima', 'email': 'carla.lima@email.com', 'telefone': '(11) 99876-5434'},
            {'nome': 'Fernanda Costa Silva', 'email': 'fernanda.costa@email.com', 'telefone': '(11) 99876-5435'},
            {'nome': 'Juliana Pereira Santos', 'email': 'juliana.pereira@email.com', 'telefone': '(11) 99876-5436'},
        ]
        
        pacientes = []
        for paciente_data in pacientes_data:
            paciente = User()
            paciente.nome = paciente_data['nome']
            paciente.email = paciente_data['email']
            paciente.telefone = paciente_data['telefone']
            paciente.role = 'paciente'
            paciente.ativo = True
            paciente.set_password('paciente123')
            
            db.session.add(paciente)
            pacientes.append(paciente)
        
        db.session.commit()
        print(f"✅ {len(pacientes)} pacientes criados - Senha padrão: paciente123")
        
        # 6. Criar alguns agendamentos de exemplo
        print("📋 Criando agendamentos de exemplo...")
        agendamentos_criados = 0
        
        # Buscar algumas agendas disponíveis
        agendas_disponiveis = Agenda.query.filter(
            Agenda.data >= datetime.now().date()
        ).order_by(Agenda.data, Agenda.hora_inicio).limit(20).all()
        
        for i, agenda in enumerate(agendas_disponiveis[:10]):  # Criar 10 agendamentos
            if i < len(pacientes):
                # Agendamento para paciente registrado
                paciente = pacientes[i % len(pacientes)]
                especialidade = random.choice(agenda.medico.especialidades)
                
                agendamento = Agendamento()
                agendamento.paciente_id = paciente.id
                agendamento.medico_id = agenda.medico_id
                agendamento.especialidade_id = especialidade.id
                agendamento.inicio = datetime.combine(agenda.data, agenda.hora_inicio)
                agendamento.fim = datetime.combine(agenda.data, agenda.hora_fim)
                agendamento.status = random.choice(['agendado', 'confirmado'])
                agendamento.origem = 'site'
                
                db.session.add(agendamento)
                agendamentos_criados += 1
            else:
                # Agendamento para convidado
                especialidade = random.choice(agenda.medico.especialidades)
                nomes_convidados = [
                    'Paula Rodrigues', 'Beatriz Santos', 'Camila Souza', 
                    'Leticia Alves', 'Gabriela Martins'
                ]
                
                agendamento = Agendamento()
                agendamento.nome_convidado = random.choice(nomes_convidados)
                agendamento.email_convidado = f"convidado{i}@email.com"
                agendamento.telefone_convidado = f"(11) 9999-{i:04d}"
                agendamento.medico_id = agenda.medico_id
                agendamento.especialidade_id = especialidade.id
                agendamento.inicio = datetime.combine(agenda.data, agenda.hora_inicio)
                agendamento.fim = datetime.combine(agenda.data, agenda.hora_fim)
                agendamento.status = 'agendado'
                agendamento.origem = 'site'
                
                db.session.add(agendamento)
                agendamentos_criados += 1
        
        db.session.commit()
        print(f"✅ {agendamentos_criados} agendamentos criados")
        
        print("\n🎉 Dados de exemplo criados com sucesso!")
        print("\n📋 RESUMO:")
        print(f"   • {len(especialidades)} especialidades")
        print(f"   • {len(medicos)} médicos")
        print(f"   • {len(pacientes)} pacientes")
        print(f"   • {total_slots} slots de agenda")
        print(f"   • {agendamentos_criados} agendamentos")
        print(f"   • 1 administrador")
        
        print("\n🔑 CREDENCIAIS DE ACESSO:")
        print("   👨‍💼 Admin: admin@clinicadrraimundonunes.com.br / admin123")
        print("   👨‍⚕️ Médicos: [email] / medico123")
        print("   👥 Pacientes: [email] / paciente123")
        
        print("\n🌐 Acesse: http://localhost:5000")

if __name__ == '__main__':
    create_seed_data()