#!/usr/bin/env python3
import os
from datetime import datetime, timedelta

os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', ''))

from extensions import db
from models import Medico, Agenda, Agendamento, User
from main import app

def verificar_dados():
    with app.app_context():
        print("=" * 60)
        print("VERIFICAÇÃO DE DADOS - SISTEMA DE AGENDAMENTOS")
        print("=" * 60)
        
        # Verificar médicos
        medicos = Medico.query.filter_by(ativo=True).all()
        print(f"\n📋 Total de médicos ativos: {len(medicos)}")
        for medico in medicos:
            print(f"   - Dr(a). {medico.usuario.nome} (CRM: {medico.crm})")
        
        # Verificar agenda (horários disponíveis)
        hoje = datetime.now().date()
        proximos_30_dias = hoje + timedelta(days=30)
        
        agendas = Agenda.query.filter(
            Agenda.data >= hoje,
            Agenda.data <= proximos_30_dias,
            Agenda.ativo == True
        ).order_by(Agenda.data, Agenda.hora_inicio).all()
        
        print(f"\n📅 Total de horários cadastrados (próximos 30 dias): {len(agendas)}")
        
        # Mostrar alguns exemplos
        if agendas:
            print("\n   Exemplos de horários cadastrados:")
            for agenda in agendas[:10]:
                print(f"   - {agenda.data} {agenda.hora_inicio} - {agenda.hora_fim} | Dr(a). {agenda.medico.usuario.nome}")
        
        # Verificar agendamentos
        agendamentos = Agendamento.query.filter(
            Agendamento.inicio >= datetime.now(),
            Agendamento.status.in_(['agendado', 'confirmado'])
        ).order_by(Agendamento.inicio).all()
        
        print(f"\n🗓️  Total de agendamentos futuros: {len(agendamentos)}")
        
        if agendamentos:
            print("\n   Agendamentos confirmados:")
            for agend in agendamentos[:10]:
                print(f"   - {agend.inicio} | Paciente: {agend.nome_paciente} | Dr(a). {agend.medico.usuario.nome}")
        
        # Verificar compatibilidade entre agendas e agendamentos
        print("\n" + "=" * 60)
        print("VERIFICAÇÃO DE COMPATIBILIDADE")
        print("=" * 60)
        
        agendamentos_com_problema = []
        for agend in agendamentos:
            # Verificar se existe uma agenda correspondente
            agenda_correspondente = Agenda.query.filter(
                Agenda.medico_id == agend.medico_id,
                Agenda.data == agend.inicio.date(),
                Agenda.hora_inicio == agend.inicio.time(),
                Agenda.ativo == True
            ).first()
            
            if not agenda_correspondente:
                agendamentos_com_problema.append(agend)
        
        if agendamentos_com_problema:
            print(f"\n⚠️  ATENÇÃO: {len(agendamentos_com_problema)} agendamentos sem horário correspondente na agenda:")
            for agend in agendamentos_com_problema[:5]:
                print(f"   - {agend.inicio} | {agend.nome_paciente}")
        else:
            print("\n✅ Todos os agendamentos têm horários correspondentes na agenda!")
        
        print("\n" + "=" * 60)
        
        # Testar a query da API
        print("\nTESTANDO QUERY DA API DO CALENDÁRIO")
        print("=" * 60)
        
        data_inicio = hoje
        data_fim = hoje + timedelta(days=7)
        
        agendas_teste = Agenda.query.filter(
            Agenda.data >= data_inicio,
            Agenda.data <= data_fim,
            Agenda.ativo == True
        ).order_by(Agenda.data, Agenda.hora_inicio).all()
        
        print(f"\nHorários na agenda (próximos 7 dias): {len(agendas_teste)}")
        
        eventos_teste = []
        for agenda in agendas_teste:
            data_hora_inicio = datetime.combine(agenda.data, agenda.hora_inicio)
            
            agendamento = Agendamento.query.filter(
                Agendamento.medico_id == agenda.medico_id,
                Agendamento.inicio == data_hora_inicio,
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).first()
            
            status = "OCUPADO" if agendamento else "DISPONÍVEL"
            paciente = f" | Paciente: {agendamento.nome_paciente}" if agendamento else ""
            
            eventos_teste.append({
                'data': agenda.data,
                'hora': agenda.hora_inicio,
                'medico': agenda.medico.usuario.nome,
                'status': status,
                'paciente': paciente
            })
        
        if eventos_teste:
            print("\nEventos que serão exibidos no calendário:")
            for evt in eventos_teste[:15]:
                print(f"   {evt['data']} {evt['hora']} | Dr(a). {evt['medico']} | {evt['status']}{evt['paciente']}")
        else:
            print("\n⚠️  NENHUM EVENTO SERÁ EXIBIDO NO CALENDÁRIO!")
            print("   Possíveis causas:")
            print("   - Não há horários cadastrados na agenda para os próximos dias")
            print("   - Todos os horários estão marcados como inativos")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    verificar_dados()
