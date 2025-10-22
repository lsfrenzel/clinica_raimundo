#!/usr/bin/env python3
"""
Script para criar alguns agendamentos de teste
"""
import os
from datetime import datetime, timedelta

from extensions import db
from models import Agendamento, Medico, Especialidade, User, Agenda
from main import app

def criar_agendamentos():
    with app.app_context():
        print("🗓️  Criando agendamentos de teste...")
        
        # Buscar médicos e especialidades
        medicos = Medico.query.filter_by(ativo=True).limit(3).all()
        especialidades = Especialidade.query.all()
        
        if not medicos or not especialidades:
            print("❌ Não há médicos ou especialidades cadastrados!")
            return
        
        # Buscar algumas agendas disponíveis
        hoje = datetime.now().date()
        agendas_disponiveis = Agenda.query.filter(
            Agenda.data >= hoje,
            Agenda.data <= hoje + timedelta(days=7),
            Agenda.ativo == True
        ).limit(10).all()
        
        if not agendas_disponiveis:
            print("❌ Não há horários disponíveis!")
            return
        
        # Criar 5 agendamentos de teste
        agendamentos_criados = 0
        
        for i, agenda in enumerate(agendas_disponiveis[:5]):
            # Verificar se já existe agendamento para este horário
            data_hora_inicio = datetime.combine(agenda.data, agenda.hora_inicio)
            data_hora_fim = datetime.combine(agenda.data, agenda.hora_fim)
            
            ja_existe = Agendamento.query.filter(
                Agendamento.medico_id == agenda.medico_id,
                Agendamento.inicio == data_hora_inicio
            ).first()
            
            if ja_existe:
                continue
            
            # Criar agendamento
            agendamento = Agendamento()
            agendamento.nome_convidado = f"Paciente Teste {i+1}"
            agendamento.email_convidado = f"paciente{i+1}@teste.com"
            agendamento.telefone_convidado = f"(11) 9{1000+i:04d}-{2000+i:04d}"
            agendamento.medico_id = agenda.medico_id
            agendamento.especialidade_id = especialidades[i % len(especialidades)].id
            agendamento.inicio = data_hora_inicio
            agendamento.fim = data_hora_fim
            agendamento.status = 'confirmado'
            agendamento.origem = 'admin'
            
            db.session.add(agendamento)
            agendamentos_criados += 1
        
        db.session.commit()
        
        print(f"✅ {agendamentos_criados} agendamentos criados!")
        
        # Listar agendamentos criados
        print("\n📋 Agendamentos criados:")
        agendamentos = Agendamento.query.filter(
            Agendamento.inicio >= datetime.now()
        ).order_by(Agendamento.inicio).limit(10).all()
        
        for agend in agendamentos:
            print(f"   - {agend.inicio.strftime('%d/%m/%Y %H:%M')} | {agend.nome_paciente} | Dr(a). {agend.medico.usuario.nome}")

if __name__ == '__main__':
    criar_agendamentos()
