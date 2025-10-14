#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir o problema dos médicos no Railway
Execute: python diagnosticar_railway.py
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

def diagnosticar_e_corrigir():
    """Diagnosticar e corrigir problemas no banco de dados do Railway"""
    
    app = create_app()
    
    print("🔍 DIAGNÓSTICO DO BANCO DE DADOS RAILWAY")
    print("=" * 60)
    
    with app.app_context():
        # Verificar conexão
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        print(f"📍 Conectado a: {db_url[:80]}...")
        
        # 1. Verificar especialidades
        print("\n📝 ESPECIALIDADES:")
        especialidades = Especialidade.query.all()
        print(f"   Total: {len(especialidades)}")
        for esp in especialidades:
            medicos_count = esp.medicos.count()
            print(f"   • {esp.nome} (ID: {esp.id}) - {medicos_count} médicos")
        
        # 2. Verificar usuários
        print(f"\n👤 USUÁRIOS:")
        users = User.query.all()
        print(f"   Total: {len(users)}")
        for user in users:
            print(f"   • {user.nome} ({user.role}) - Email: {user.email} - Ativo: {user.ativo}")
        
        # 3. Verificar médicos
        print(f"\n👨‍⚕️ MÉDICOS:")
        medicos = Medico.query.all()
        print(f"   Total: {len(medicos)}")
        for medico in medicos:
            user = User.query.get(medico.user_id)
            esp_nomes = [e.nome for e in medico.especialidades]
            print(f"   • {user.nome if user else 'N/A'} (CRM: {medico.crm}) - Ativo: {medico.ativo}")
            print(f"     Especialidades: {', '.join(esp_nomes) if esp_nomes else 'NENHUMA!'}")
        
        # 4. Verificar agendas
        print(f"\n📅 AGENDAS:")
        agendas = Agenda.query.filter_by(ativo=True).all()
        print(f"   Total de slots ativos: {len(agendas)}")
        
        # 5. CORREÇÃO: Associar médicos às especialidades se necessário
        print("\n🔧 CORRIGINDO ASSOCIAÇÕES...")
        
        # Dados de correção
        correcoes = [
            {'crm': 'CRM/SP 123456', 'especialidades': ['Pré-Natal de Alto Risco', 'DIU e Implanon']},
            {'crm': 'CRM/SP 234567', 'especialidades': ['Mastologia']},
            {'crm': 'CRM/SP 345678', 'especialidades': ['Reprodução Humana']},
            {'crm': 'CRM/SP 456789', 'especialidades': ['Uroginecologia']},
            {'crm': 'CRM/SP 567890', 'especialidades': ['Climatério e Menopausa', 'Sexualidade']}
        ]
        
        correcoes_feitas = 0
        for corr in correcoes:
            medico = Medico.query.filter_by(crm=corr['crm']).first()
            if medico:
                # Limpar especialidades antigas
                medico.especialidades = []
                
                # Adicionar novas especialidades
                for esp_nome in corr['especialidades']:
                    esp = Especialidade.query.filter_by(nome=esp_nome).first()
                    if esp and esp not in medico.especialidades:
                        medico.especialidades.append(esp)
                        correcoes_feitas += 1
                        print(f"   ✅ {medico.usuario.nome} → {esp_nome}")
        
        if correcoes_feitas > 0:
            db.session.commit()
            print(f"\n✅ {correcoes_feitas} associações corrigidas!")
        else:
            print("\n✅ Nenhuma correção necessária!")
        
        # 6. CRIAR AGENDAS SE NECESSÁRIO
        print("\n📅 VERIFICANDO AGENDAS...")
        hoje = datetime.now().date()
        agenda_count = 0
        
        for medico in Medico.query.filter_by(ativo=True).all():
            # Verificar se tem agenda futura
            agendas_futuras = Agenda.query.filter(
                Agenda.medico_id == medico.id,
                Agenda.data >= hoje,
                Agenda.ativo == True
            ).count()
            
            if agendas_futuras < 10:
                print(f"   ⚠️  {medico.usuario.nome} tem apenas {agendas_futuras} slots futuros. Criando mais...")
                
                for dia_offset in range(30):
                    data = hoje + timedelta(days=dia_offset)
                    if data.weekday() >= 5:  # Pular fins de semana
                        continue
                    
                    # Verificar se já existe agenda para este dia
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
            print(f"   ✅ {agenda_count} novos slots criados!")
        
        # 7. RESUMO FINAL
        print("\n" + "=" * 60)
        print("✅ DIAGNÓSTICO E CORREÇÃO CONCLUÍDOS!")
        print("=" * 60)
        
        print(f"\n📊 RESULTADO FINAL:")
        for esp in Especialidade.query.all():
            medicos_ativos = esp.medicos.filter_by(ativo=True).count()
            print(f"   • {esp.nome}: {medicos_ativos} médicos ativos")
        
        print(f"\n🌐 Teste agora:")
        print(f"   https://clinicaraimundo-production.up.railway.app/appointments/medicos/1")
        print(f"   https://clinicaraimundo-production.up.railway.app/appointments/medicos/3")
        
        return True

if __name__ == '__main__':
    try:
        success = diagnosticar_e_corrigir()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
