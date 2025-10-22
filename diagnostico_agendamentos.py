#!/usr/bin/env python3
"""
Script de diagnóstico para verificar agendamentos no Railway
Execute este script no Railway para identificar problemas
"""

import os
import sys
from datetime import datetime

def main():
    print("=" * 80)
    print("DIAGNÓSTICO DE AGENDAMENTOS - RAILWAY")
    print("=" * 80)
    print()
    
    # Verificar variável de ambiente
    database_url = os.environ.get('DATABASE_URL')
    print(f"1. DATABASE_URL configurado: {'Sim' if database_url else 'Não'}")
    if database_url:
        # Ocultar senha
        safe_url = database_url.split('@')[1] if '@' in database_url else '***'
        print(f"   Conectando em: ...@{safe_url}")
    print()
    
    # Importar após verificar DATABASE_URL
    try:
        from main import app
        from models import User, Medico, Agendamento, Especialidade
        from extensions import db
    except Exception as e:
        print(f"❌ ERRO ao importar módulos: {e}")
        return
    
    with app.app_context():
        print("2. VERIFICANDO BANCO DE DADOS")
        print("-" * 80)
        
        # Contar registros
        total_users = User.query.count()
        total_medicos = Medico.query.count()
        total_users_medico = User.query.filter_by(role='medico').count()
        total_agendamentos = Agendamento.query.count()
        total_especialidades = Especialidade.query.count()
        
        print(f"   Total de usuários: {total_users}")
        print(f"   Total de usuários com role='medico': {total_users_medico}")
        print(f"   Total de médicos (tabela medicos): {total_medicos}")
        print(f"   Total de especialidades: {total_especialidades}")
        print(f"   Total de agendamentos: {total_agendamentos}")
        print()
        
        # Listar médicos
        print("3. MÉDICOS CADASTRADOS")
        print("-" * 80)
        medicos = Medico.query.all()
        if medicos:
            for medico in medicos:
                user = User.query.get(medico.user_id)
                print(f"   ID: {medico.id} | User ID: {medico.user_id} | Nome: {user.nome if user else 'N/A'} | CRM: {medico.crm}")
        else:
            print("   ⚠️  Nenhum médico cadastrado na tabela 'medicos'")
        print()
        
        # Listar agendamentos
        print("4. AGENDAMENTOS")
        print("-" * 80)
        agendamentos = Agendamento.query.order_by(Agendamento.inicio.desc()).limit(10).all()
        if agendamentos:
            print(f"   Mostrando últimos {len(agendamentos)} agendamentos:")
            for ag in agendamentos:
                medico = Medico.query.get(ag.medico_id) if ag.medico_id else None
                medico_nome = medico.usuario.nome if medico and medico.usuario else "N/A"
                print(f"   ID: {ag.id}")
                print(f"      Médico ID: {ag.medico_id} ({medico_nome})")
                print(f"      Paciente: {ag.nome_paciente}")
                print(f"      Data/Hora: {ag.inicio}")
                print(f"      Status: {ag.status}")
                print(f"      Origem: {ag.origem}")
                print()
        else:
            print("   ⚠️  Nenhum agendamento encontrado")
        print()
        
        # Verificar relacionamentos
        print("5. VERIFICANDO RELACIONAMENTOS")
        print("-" * 80)
        agendamentos_sem_medico = Agendamento.query.filter_by(medico_id=None).count()
        agendamentos_medico_invalido = 0
        
        for ag in Agendamento.query.all():
            if ag.medico_id:
                medico = Medico.query.get(ag.medico_id)
                if not medico:
                    agendamentos_medico_invalido += 1
        
        print(f"   Agendamentos sem medico_id (NULL): {agendamentos_sem_medico}")
        print(f"   Agendamentos com medico_id inválido: {agendamentos_medico_invalido}")
        print()
        
        # Verificar agendamentos por médico
        print("6. AGENDAMENTOS POR MÉDICO")
        print("-" * 80)
        for medico in medicos:
            agora = datetime.utcnow()
            agendamentos_medico = Agendamento.query.filter_by(medico_id=medico.id).all()
            futuros = [a for a in agendamentos_medico if a.inicio >= agora]
            passados = [a for a in agendamentos_medico if a.inicio < agora]
            
            user = User.query.get(medico.user_id)
            print(f"   Dr(a). {user.nome if user else 'N/A'} (ID: {medico.id})")
            print(f"      Total: {len(agendamentos_medico)} | Futuros: {len(futuros)} | Passados: {len(passados)}")
            
            if futuros:
                print(f"      Próximos agendamentos:")
                for ag in sorted(futuros, key=lambda x: x.inicio)[:3]:
                    print(f"         - {ag.inicio} | {ag.nome_paciente} | Status: {ag.status}")
        
        if not medicos:
            print("   ⚠️  Nenhum médico para verificar")
        print()
        
        print("=" * 80)
        print("DIAGNÓSTICO CONCLUÍDO")
        print("=" * 80)
        
        # Resumo de problemas
        problemas = []
        if total_medicos == 0:
            problemas.append("❌ Não há médicos cadastrados na tabela 'medicos'")
        if total_users_medico > total_medicos:
            problemas.append(f"⚠️  Há {total_users_medico - total_medicos} usuários com role='medico' sem perfil médico")
        if agendamentos_sem_medico > 0:
            problemas.append(f"❌ {agendamentos_sem_medico} agendamentos sem medico_id")
        if agendamentos_medico_invalido > 0:
            problemas.append(f"❌ {agendamentos_medico_invalido} agendamentos com medico_id inválido")
        
        if problemas:
            print("\n⚠️  PROBLEMAS ENCONTRADOS:")
            for problema in problemas:
                print(f"   {problema}")
        else:
            print("\n✅ Nenhum problema crítico encontrado!")
        print()

if __name__ == '__main__':
    main()
